"""Fixed-screen terminal renderer for The Road."""

from __future__ import annotations

from collections import deque
from typing import Iterable

from game.display import (
    menu_choice as _menu_choice,
    print_status_screen as _print_status_screen,
    print_title_screen as _print_title_screen,
)
from game.ui.screens import build_fixed_frame
from game.ui.view_models import SceneView


class Renderer:
    """Central screen manager: keeps story buffers and redraws one full frame."""

    def __init__(self) -> None:
        self._story_lines: deque[str] = deque(maxlen=120)
        self._event_lines: deque[str] = deque(maxlen=30)
        self._pending_actions: list[str] = []
        self._pending_choices: list[str] = []
        self._in_dialogue_session: bool = False

    def render(self, view: SceneView) -> int | None:
        if view.current_mode == "inspect":
            self.show_system(f"\n[{view.inspect_target}]\n{view.inspect_text}")
            return None

        if view.current_mode == "threat":
            threat = [f"Threat: {view.threat_name}", *view.threat_lines, "", *view.player_status_lines]
            self.show_location("\n".join(threat))
            self._pending_actions = view.combat_actions[:]
            return None

        if view.current_mode == "dialogue":
            if view.dialogue_lines:
                self._append_story(view.dialogue_lines)
            if view.footer_hint:
                self._append_story(["", view.footer_hint])
            if view.current_choices:
                self._pending_choices = view.current_choices[:]
                self._draw(view)
                return self._get_numeric_choice(view.current_choices)
            self._draw(view)
            return None

        if view.system_lines:
            self._append_events(view.system_lines)
        if view.suggested_actions:
            self._pending_actions = view.suggested_actions[:]
        self._draw(view)
        return None

    def _draw(self, view: SceneView) -> None:
        display = SceneView(
            current_mode=view.current_mode,
            location_name=view.location_name,
            speaker_name=view.speaker_name,
            hud=view.hud,
            sidebar_sections=view.sidebar_sections,
            main_lines=list(self._story_lines)[-60:],
            current_choices=self._pending_choices,
            suggested_actions=self._pending_actions,
            footer_hint="",
            input_prompt=view.input_prompt or "> ",
        )
        if self._event_lines:
            display.main_lines += ["", "—"] + list(self._event_lines)[-8:]

        print("\033[2J\033[H", end="")
        print(build_fixed_frame(display), end="", flush=True)

    def _append_story(self, lines: Iterable[str]) -> None:
        for line in lines:
            self._story_lines.append(line)

    def _append_events(self, lines: Iterable[str]) -> None:
        for line in lines:
            for split in str(line).split("\n"):
                self._event_lines.append(split)

    def _get_numeric_choice(self, choices: list[str]) -> int:
        while True:
            raw = input("\n> ").strip()
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(choices):
                    self._pending_choices = []
                    return idx
            self._append_events([f"Enter a number from 1 to {len(choices)}."])

    def show_title(self) -> None:
        _print_title_screen()

    def show_menu(self, prompt: str, options: list[str]) -> int:
        return _menu_choice(prompt, options)

    def show_status(self, state, location_name: str) -> None:
        _print_status_screen(state, location_name)

    def show_dialogue(self, lines: list[str]) -> None:
        self._append_story(lines)

    def show_hint(self, text: str) -> None:
        if text:
            self._append_events([text])

    def show_choices(self, prompt_lines: list[str], choices: list[str]) -> int:
        self._append_story(prompt_lines)
        self._pending_choices = choices[:]
        return self._get_numeric_choice(choices)

    def begin_dialogue_session(self, speaker_name: str) -> None:
        self._in_dialogue_session = True
        self._append_story([f"{speaker_name}", ""])

    def end_dialogue_session(self) -> None:
        self._in_dialogue_session = False

    def show_system(self, text: str) -> None:
        if text.strip().startswith("[") or "\n[" in text:
            self.show_location(text)
            return
        self._append_events([text])

    def show_location(self, text: str) -> None:
        self._event_lines.clear()
        self._story_lines.clear()
        self._append_story(text.split("\n"))

    def show_lines(self, lines: list[str]) -> None:
        self._append_events(lines)

    def show_log_view(self) -> None:
        self._append_events(["Recent log:", *list(self._event_lines)[-12:]])

    def get_input(self, prompt: str = "\n> ") -> str:
        return input(prompt)

    def get_text_input(self, prompt: str) -> str:
        return input(prompt)

    def invalidate_hud(self) -> None:
        return
