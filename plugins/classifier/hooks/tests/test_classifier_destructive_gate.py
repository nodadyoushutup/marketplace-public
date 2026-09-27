"""Tests for the classifier destructive-command gate hook."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

HOOKS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HOOKS_DIR))

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "classifier_gate_under_test", HOOKS_DIR / "classifier-destructive-gate.py"
)
gate = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(gate)


class CatastrophicTests(unittest.TestCase):
    def test_root_wipe_is_catastrophic(self) -> None:
        self.assertIsNotNone(gate.catastrophic("rm -rf --no-preserve-root /"))

    def test_mkfs_is_catastrophic(self) -> None:
        self.assertIsNotNone(gate.catastrophic("mkfs.ext4 /dev/sda1"))

    def test_dd_to_device_is_catastrophic(self) -> None:
        self.assertIsNotNone(gate.catastrophic("dd if=/dev/zero of=/dev/sda bs=1M"))

    def test_fork_bomb_is_catastrophic(self) -> None:
        self.assertIsNotNone(gate.catastrophic(":() { :|:& };:"))

    def test_ordinary_rm_is_not_catastrophic(self) -> None:
        self.assertIsNone(gate.catastrophic("rm -rf ./build"))


class RiskyTests(unittest.TestCase):
    def test_read_only_commands_are_not_risky(self) -> None:
        for command in (
            "git status",
            "ls -la",
            "docker compose ps",
            "kubectl get pods",
            "cat file.txt",
        ):
            self.assertFalse(gate.risky(command), command)

    def test_force_push_is_risky(self) -> None:
        self.assertTrue(gate.risky("git push --force origin main"))

    def test_compose_down_volumes_is_risky(self) -> None:
        self.assertTrue(gate.risky("docker compose down -v"))

    def test_drop_table_is_risky(self) -> None:
        self.assertTrue(gate.risky("psql -c 'drop table users'"))

    def test_plain_recursive_rm_is_risky(self) -> None:
        self.assertTrue(gate.risky("rm -rf ./build"))


class DestructiveProbabilityTests(unittest.TestCase):
    def test_reads_deny_from_answers(self) -> None:
        payload = {"answers": {"gate": {"allow": 0.1, "deny": 0.9}}}
        self.assertAlmostEqual(gate.destructive_probability(payload) or 0, 0.9)

    def test_reads_nested_label(self) -> None:
        payload = {"answers": {"gate": {"unrecoverable": {"noul": 0.94}}}}
        self.assertAlmostEqual(gate.destructive_probability(payload) or 0, 0.94)

    def test_reads_top_level_deny(self) -> None:
        self.assertAlmostEqual(
            gate.destructive_probability({"deny": 0.7}) or 0, 0.7
        )

    def test_unknown_shape_returns_none(self) -> None:
        self.assertIsNone(gate.destructive_probability({"answers": {"gate": {}}}))

    def test_non_dict_returns_none(self) -> None:
        self.assertIsNone(gate.destructive_probability(["nope"]))


class ThresholdTests(unittest.TestCase):
    def test_default_threshold(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertAlmostEqual(gate.threshold(), gate.DEFAULT_THRESHOLD)

    def test_env_override(self) -> None:
        with mock.patch.dict("os.environ", {"CLASSIFIER_GATE_THRESHOLD": "0.8"}):
            self.assertAlmostEqual(gate.threshold(), 0.8)

    def test_invalid_env_falls_back(self) -> None:
        with mock.patch.dict("os.environ", {"CLASSIFIER_GATE_THRESHOLD": "abc"}):
            self.assertAlmostEqual(gate.threshold(), gate.DEFAULT_THRESHOLD)

    def test_out_of_range_is_clamped(self) -> None:
        with mock.patch.dict("os.environ", {"CLASSIFIER_GATE_THRESHOLD": "2"}):
            self.assertAlmostEqual(gate.threshold(), 1.0)


class DecideTests(unittest.TestCase):
    def test_empty_command_allows(self) -> None:
        self.assertEqual(gate.decide("", {})[0], "allow")

    def test_safe_command_allows(self) -> None:
        self.assertEqual(gate.decide("git status", {})[0], "allow")

    def test_catastrophic_command_denies(self) -> None:
        self.assertEqual(gate.decide("rm -rf --no-preserve-root /", {})[0], "deny")

    def test_risky_without_classifier_asks(self) -> None:
        with mock.patch.object(gate, "classify", return_value=None):
            permission, user_message, _agent = gate.decide("rm -rf ./build", {})
        self.assertEqual(permission, "ask")
        self.assertTrue(user_message)

    def test_risky_classifier_confident_asks(self) -> None:
        with mock.patch.object(gate, "classify", return_value=0.94):
            self.assertEqual(gate.decide("rm -rf ./build", {})[0], "ask")

    def test_risky_classifier_confident_safe_allows(self) -> None:
        with mock.patch.object(gate, "classify", return_value=0.04):
            self.assertEqual(gate.decide("rm -rf ./build", {})[0], "allow")

    def test_read_only_never_calls_classifier(self) -> None:
        with mock.patch.object(gate, "classify") as classify:
            gate.decide("docker compose ps", {})
            classify.assert_not_called()


class SubprocessTests(unittest.TestCase):
    def _run(self, payload: dict, env: dict | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(HOOKS_DIR / "classifier-destructive-gate.py")],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            env={
                "PATH": "",
                "CLASSIFIER_ENDPOINT": "",
                **(env or {}),
            },
        )

    def test_safe_command_allows(self) -> None:
        completed = self._run({"command": "git status"})
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(json.loads(completed.stdout)["permission"], "allow")

    def test_catastrophic_denies(self) -> None:
        completed = self._run({"command": "mkfs.ext4 /dev/sda1"})
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(json.loads(completed.stdout)["permission"], "deny")

    def test_malformed_stdin_allows(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(HOOKS_DIR / "classifier-destructive-gate.py")],
            input="not json",
            capture_output=True,
            text=True,
            env={"PATH": ""},
        )
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(json.loads(completed.stdout)["permission"], "allow")

    def test_risky_without_endpoint_asks(self) -> None:
        completed = self._run({"command": "docker compose down -v"})
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(json.loads(completed.stdout)["permission"], "ask")


if __name__ == "__main__":
    unittest.main()