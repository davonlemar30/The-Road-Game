"""Fixed-screen terminal renderer for The Road."""

from __future__ import annotations

from collections import deque
from typing import Iterable

from rich.console import Console
from rich.live import Live

from game.display import (
    menu_choice as _menu_choice,
    print_status_screen as _print_status_screen,
    print_title_screen as _print_title_screen,
)
from game.ui.screens import build_fixed_frame, build_journal_overlay
from game.ui.view_models import SceneView


class Renderer:
    """Central screen manager: owns layout, buffers and incremental pane updates."""

    def __init__(self) -> None:
        self.console = Console()
        self._story_lines: deque[str] = deque(maxlen=220)
        self._pending_actions: list[str] = []
        self._pending_choices: list[str] = []
        self._sidebar_sections = []
        self._location_name = ""
        self._footer_hint = ""
        self._input_prompt = "> "
        self._last_screen: SceneView | None = None
        self._in_dialogue_session: bool = False

        self._live = Live(console=self.console, refresh_per_second=12, transient=False, auto_refresh=False)
        self._live_started = False

    def _ensure_live(self) -> None:
        if not self._live_started:
            self._live.start()
            self._live_started = True

    def _stop_live(self) -> None:
        if self._live_started:
            self._live.stop()
            self._live_started = False

    def close(self) -> None:
        self._stop_live()

    def render(self, view: SceneView) -> int | None:
        if view.current_mode == "journal":
            self._render_journal(view)
            return None

        if view.current_mode == "inspect":
            self._append_story([f"[{view.inspect_target}]", view.inspect_text])
            self._render_main(view)
            return None

        if view.current_mode == "threat":
            threat = [f"Threat: {view.threat_name}", *view.threat_lines, "", *view.player_status_lines]
            self._append_story(threat)
            self._pending_actions = view.combat_actions[:]
            self._render_main(view)
            return None

        if view.current_mode == "dialogue":
            if view.dialogue_lines:
                self._append_story(view.dialogue_lines)
            if view.footer_hint:
                self._append_story(["", view.footer_hint])
            if view.current_choices:
                self._pending_choices = view.current_choices[:]
                self._render_main(view)
                return self._get_numeric_choice(view.current_choices)
            self._render_main(view)
            return None

        if view.main_lines:
            self._story_lines.clear()
            self._append_story(view.main_lines)
        if view.system_lines:
            self._append_story(view.system_lines)
        if view.suggested_actions:
            self._pending_actions = view.suggested_actions[:]

        self._render_main(view)
        return None

    def _render_main(self, view: SceneView) -> None:
        self._location_name = view.location_name or self._location_name
        if view.sidebar_sections:
            self._sidebar_sections = view.sidebar_sections
        self._input_prompt = view.input_prompt or self._input_prompt
        self._footer_hint = view.footer_hint or ""

        display = SceneView(
            current_mode=view.current_mode,
            location_name=self._location_name,
            sidebar_sections=self._sidebar_sections,
            main_lines=list(self._story_lines),
            current_choices=self._pending_choices,
            suggested_actions=self._pending_actions,
            footer_hint=self._footer_hint,
            input_prompt=self._input_prompt,
        )
        self._last_screen = display
        self._ensure_live()
        self._live.update(build_fixed_frame(display), refresh=True)

    def _render_journal(self, view: SceneView) -> None:
        self._ensure_live()
        self._live.update(build_journal_overlay(view), refresh=True)

    def _append_story(self, lines: Iterable[str]) -> None:
        for line in lines:
            for split in str(line).split("\n"):
                self._story_lines.append(split)

    def _get_numeric_choice(self, choices: list[str]) -> int:
        while True:
            raw = self.get_input(prompt="\nChoose > ").strip()
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(choices):
                    self._pending_choices = []
                    if self._last_screen is not None:
                        self._render_main(self._last_screen)
                    return idx
            self._append_story([f"Enter a number from 1 to {len(choices)}."])
            if self._last_screen is not None:
                self._render_main(self._last_screen)

    def show_title(self) -> None:
        self._stop_live()
        _print_title_screen()

    def show_menu(self, prompt: str, options: list[str]) -> int:
        self._stop_live()
        return _menu_choice(prompt, options)

    def show_status(self, state, location_name: str) -> None:
        self._stop_live()
        _print_status_screen(state, location_name)

    def show_dialogue(self, lines: list[str]) -> None:
        self._append_story(lines)

    def show_hint(self, text: str) -> None:
        if text:
            self._append_story([text])

    def show_choices(self, prompt_lines: list[str], choices: list[str]) -> int:
        self._append_story(prompt_lines)
        self._pending_choices = choices[:]
        if self._last_screen is not None:
            self._render_main(self._last_screen)
        return self._get_numeric_choice(choices)

    def begin_dialogue_session(self, speaker_name: str) -> None:
        self._in_dialogue_session = True
        self._append_story([f"{speaker_name}", ""])

    def end_dialogue_session(self) -> None:
        self._in_dialogue_session = False

    def show_system(self, text: str) -> None:
        self._append_story([text])

    def show_location(self, text: str) -> None:
        self._append_story([""])
        self._append_story(text.split("\n"))

    def show_lines(self, lines: list[str]) -> None:
        self._append_story(lines)

    def show_log_view(self) -> None:
        self._append_story(["", "Recent log:", *list(self._story_lines)[-14:]])

    def get_input(self, prompt: str = "\n> ") -> str:
        self._ensure_live()
        return self.console.input(prompt)

    def get_text_input(self, prompt: str) -> str:
        self._ensure_live()
        return self.console.input(prompt)

    def invalidate_hud(self) -> None:
        return
