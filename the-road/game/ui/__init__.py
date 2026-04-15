"""
game.ui — presentation layer for The Road.

Status (Task 5 — current):
    All primary output paths run through Renderer.render(SceneView) or named
    Renderer methods.  engine.py does not call print() or input() directly.

    Explore mode
        Stable HUD (5 lines, ANSI-anchored in TTY).  Bounded system-text
        region (deque, 14 visual rows).  show_location() is the primary-
        content entry point for room descriptions — it clears the system
        buffer so 'look' output anchors the display region rather than
        appending to stale feedback.  show_system() handles transient
        feedback (nav, errors, objective updates).

    Dialogue mode
        Routed through SceneView(current_mode="dialogue").  DialogueSession
        manages beats; choices go through run_scene_choice().  Session chrome
        (header/footer) uses begin_dialogue_session() / end_dialogue_session().

    Inspect mode
        SceneView(current_mode="inspect") renders a labeled 80-char panel.
        Supports single- and multi-paragraph text (paragraph breaks on \\n\\n).
        Blocks for Enter in TTY, then returns to explore cleanly.

    Log view (modal, not a SceneView mode)
        show_log_view() renders a framed overlay of recent log entries drawn
        from _log_buffer (persistent rolling history of all show_system /
        show_location output).  Accessible via the 'log' command.

    What remains for Task 6+
        - Portrait / ASCII art rendering
        - Combat shell (if added to game design)
        - Rich / Textual migration (if desired)
        - Full fixed-screen layout (if terminal size allows)
"""
from game.ui.renderer import Renderer
from game.ui.view_models import HudData, SceneView

__all__ = ["HudData", "Renderer", "SceneView"]
