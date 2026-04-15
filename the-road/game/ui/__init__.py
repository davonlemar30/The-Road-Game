"""
game.ui — presentation layer for The Road.

Status (Tasks 5 + 6 merged — current):
    All primary output paths run through Renderer.render(SceneView) or named
    Renderer methods.  engine.py does not call print() or input() directly.

    Explore mode (Task 5)
        Stable HUD (5 lines, ANSI-anchored in TTY).  Bounded system-text
        region (deque, 14 visual rows).  show_location() is the primary-
        content entry point for room descriptions — it clears the system
        buffer so 'look' output anchors the display region rather than
        appending to stale feedback.  show_system() handles transient
        feedback (nav, errors, objective updates).

    Log view (Task 5, modal — not a SceneView mode)
        show_log_view() renders a framed overlay of recent log entries drawn
        from _log_buffer (persistent rolling history of all show_system /
        show_location output).  Accessible via the 'log' command.

    Dialogue mode
        Routed through SceneView(current_mode="dialogue").  DialogueSession
        manages beats; choices go through run_scene_choice().  Session chrome
        (header/footer) uses begin_dialogue_session() / end_dialogue_session().
        portrait_id is stored on DialogueSession but not yet rendered in
        dialogue beats — portrait rendering is planned for a future task.

    Inspect mode
        SceneView(current_mode="inspect") renders a labeled 80-char panel.
        Supports single- and multi-paragraph text (paragraph breaks on \\n\\n).
        Blocks for Enter in TTY, then returns to explore cleanly.

    Threat / combat shell (Task 6 scaffold)
        SceneView(current_mode="threat") renders a preview panel with threat
        narrative, player status snapshot, and available actions (display only).
        Portrait art from portraits.py renders above the panel when a matching
        portrait_id is set.  No game logic or input is collected yet — this is
        a presentation scaffold for the combat design phase.
        Accessible via 'threat' command (dev preview).

    What remains for future tasks
        - Full portrait rendering in dialogue beats
        - Real combat input / resolution logic
        - Rich / Textual migration (if desired)
        - Full fixed-screen layout (if terminal size allows)
"""
from game.ui.renderer import Renderer
from game.ui.view_models import HudData, SceneView

__all__ = ["HudData", "Renderer", "SceneView"]
