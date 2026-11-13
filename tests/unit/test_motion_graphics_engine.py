import os
import sys
import pytest

from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "studio" / "system"))
sys.path.insert(0, str(REPO_ROOT / "iva"))

import motion_graphics_engine as mge

def test_signature_styles_configuration():
    assert "kinetic_type" in mge.STYLES
    assert "liquid_glass" in mge.STYLES
    assert "editorial_grain" in mge.STYLES
    assert "pop_bold" in mge.STYLES

    for style_key, conf in mge.STYLES.items():
        assert "name" in conf
        assert "font_family" in conf
        assert "easing" in conf

def test_classic_moves_catalog():
    assert len(mge.MOVES) == 10
    move_ids = [m["id"] for m in mge.MOVES]
    assert "rise" in move_ids
    assert "pop" in move_ids
    assert "count_up" in move_ids
    assert "checklist" in move_ids
    assert "bar_fill" in move_ids

def test_sfx_catalog_presence():
    assert len(mge.AVAILABLE_SFX) == 9
    assert "pop.wav" in mge.AVAILABLE_SFX
    assert "chime.wav" in mge.AVAILABLE_SFX
    assert "counter.wav" in mge.AVAILABLE_SFX

def test_html_builder_generation():
    beats = ["First Hook Line", "Key Feature", "Final CTA"]
    html = mge.build_motion_html(
        title="Test Motion Graphic",
        script_beats=beats,
        style_key="kinetic_type",
        width=1080,
        height=1920,
        duration_s=6.0
    )
    assert "<!DOCTYPE html>" in html
    assert "gsap.min.js" in html
    assert "First" in html
    assert "Hook Line" in html
    assert "window.renderReady = true" in html
