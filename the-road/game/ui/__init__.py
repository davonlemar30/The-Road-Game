"""
game.ui — presentation layer for The Road.

Status (Task 3):
    GameEngine builds a SceneView each loop iteration and passes it to
    Renderer.render(view).  In explore mode the HUD is drawn with ANSI
    cursor anchoring so it occupies a stable visual region.

    Dialogue, menu, and inspect modes still use direct Renderer method
    calls as compatibility paths.  Full scene-view migration for those
    modes is planned for future tasks.
"""
from game.ui.renderer import Renderer
from game.ui.view_models import HudData, SceneView

__all__ = ["HudData", "Renderer", "SceneView"]
