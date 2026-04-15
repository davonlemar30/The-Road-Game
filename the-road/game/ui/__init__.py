"""
game.ui — presentation layer for The Road.

Status (Task 6):
    GameEngine builds a SceneView each loop iteration and passes it to
    Renderer.render(view).  In explore mode the HUD is drawn with ANSI
    cursor anchoring so it occupies a stable visual region.

    Dialogue is routed through SceneView/Renderer paths and now supports
    optional terminal-safe portraits.  A threat/combat shell mode also
    exists as a presentation scaffold for later combat-system work.
"""
from game.ui.renderer import Renderer
from game.ui.view_models import HudData, SceneView

__all__ = ["HudData", "Renderer", "SceneView"]
