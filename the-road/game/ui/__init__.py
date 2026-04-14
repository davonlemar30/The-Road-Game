"""
game.ui — presentation layer scaffold for The Road.

Current status (Task 1 — audit + foundation):
    This package exists to define the seam between engine logic and rendering.
    Nothing in the main game imports from here yet.  The game runs entirely
    through the existing print/display.py pipeline.

Next step (Task 2):
    Wire GameEngine to use Renderer instead of calling print() and display.py
    functions directly.  The Renderer methods are already the right shape;
    the engine just needs to be updated to call them.
"""
from game.ui.renderer import Renderer
from game.ui.view_models import SceneView

__all__ = ["Renderer", "SceneView"]
