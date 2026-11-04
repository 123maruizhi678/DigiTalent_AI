"""质量入口必须原样传播失败，并区分格式检查和写入命令。"""

from types import SimpleNamespace
from unittest.mock import Mock

import quality


def test_quality_stops_on_failure(monkeypatch):
    run = Mock(return_value=SimpleNamespace(returncode=7))
    monkeypatch.setattr(quality.subprocess, "run", run)
    monkeypatch.setattr(quality.sys, "argv", ["quality.py", "all", "quality-check"])
    assert quality.main() == 7
    assert run.call_count == 1
    assert run.call_args.args[0][-2:] == ["check", "."]


def test_format_check_never_writes(monkeypatch):
    run = Mock(return_value=SimpleNamespace(returncode=0))
    monkeypatch.setattr(quality.subprocess, "run", run)
    monkeypatch.setattr(quality.sys, "argv", ["quality.py", "all", "format-check"])
    assert quality.main() == 0
    assert run.call_count == 2
    assert run.call_args_list[0].args[0][-3:] == ["format", "--check", "."]
    assert run.call_args_list[1].args[0][-2:] == ["run", "format:check"]
    assert run.call_args_list[1].kwargs["cwd"] == quality.ROOT / "frontend"
