"""Unit tests for Safe Demo Engine simulation mode."""

from cmeplus.demo.engine import DemoEngine


def test_demo_engine_offline_execution(capsys):
    demo = DemoEngine(speed=0.0)  # zero delay for test suite speed
    result_set = demo.run()

    assert result_set.total >= 3
    assert result_set.success_count >= 2
    assert result_set.unavailable_count >= 1

    captured = capsys.readouterr()
    assert "CrackMapExec+ Safe Demo Mode" in captured.out
    assert "zero packets transmitted" in captured.out.lower()
