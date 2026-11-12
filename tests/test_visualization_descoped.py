from pathlib import Path

from src.app.strings import NAVIGATION


ROOT = Path(__file__).resolve().parents[1]


def test_removed_renderer_is_not_a_runtime_dependency():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    assert "ursina" not in requirements
    assert "panda3d" not in requirements
    assert not (ROOT / "src" / "visualization" / "three_d").exists()
    assert not (ROOT / "src" / "visualization" / "simulation_3d.py").exists()


def test_sidebar_lists_only_the_seven_retained_screens():
    assert len(NAVIGATION) == 7
    assert all("3d" not in label.lower() for label in NAVIGATION)
