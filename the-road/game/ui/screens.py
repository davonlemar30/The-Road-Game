"""Rich screen composition helpers for persistent terminal layouts."""

from __future__ import annotations

from dataclasses import dataclass
from shutil import get_terminal_size

from rich.console import Group
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

from game.ui.view_models import JournalView, SceneView, SidebarSection


@dataclass
class FrameSpec:
    width: int
    height: int
    left_width: int
    right_width: int
    bottom_height: int
    small_terminal: bool


def compute_frame_spec() -> FrameSpec:
    cols, rows = get_terminal_size(fallback=(100, 34))
    small_terminal = cols < 84 or rows < 22
    if small_terminal:
        return FrameSpec(cols, rows, cols - 2, cols - 2, 7, True)

    left = max(56, int(cols * 0.72))
    right = max(24, cols - left - 3)
    left = cols - right - 3
    return FrameSpec(cols, rows, left, right, 7, False)


def _story_panel(view: SceneView) -> Panel:
    body_lines = [line.rstrip() for line in view.main_lines if line is not None]
    if not body_lines:
        body_lines = [""]
    return Panel(
        Group(*[Text.from_markup(line) for line in body_lines]),
        title=view.location_name or "Scene",
        border_style="grey39",
        padding=(0, 1),
    )


def _sidebar_panel(sections: list[SidebarSection]) -> Panel:
    rendered: list[Text] = []
    for idx, section in enumerate(sections):
        if idx > 0:
            rendered.append(Text(""))
        rendered.append(Text(section.title.upper(), style="bold grey70"))
        if section.lines:
            for line in section.lines:
                rendered.append(Text(line))
        else:
            rendered.append(Text("-", style="grey50"))
    if not rendered:
        rendered = [Text("No world data", style="grey50")]
    return Panel(Group(*rendered), title="World", border_style="grey39", padding=(0, 1))


def _command_panel(view: SceneView) -> Panel:
    lines: list[Text] = []
    for i, action in enumerate(view.suggested_actions[:6], 1):
        lines.append(Text(f"[{i}] {action}", style="grey70"))
    if view.current_choices:
        lines.append(Text(""))
        for i, choice in enumerate(view.current_choices[:6], 1):
            lines.append(Text(f"({i}) {choice}"))
    if view.footer_hint:
        lines.append(Text(""))
        lines.append(Text(view.footer_hint, style="grey58"))
    lines.append(Text(view.input_prompt or "> ", style="bold cyan"))
    return Panel(Group(*lines), title="Commands", border_style="grey39", padding=(0, 1))


def build_fixed_frame(view: SceneView) -> Layout:
    spec = compute_frame_spec()
    layout = Layout(name="root")

    if spec.small_terminal:
        layout.split_column(
            Layout(_story_panel(view), name="story", ratio=6),
            Layout(_sidebar_panel(view.sidebar_sections), name="sidebar", size=10),
            Layout(_command_panel(view), name="commands", size=spec.bottom_height),
        )
        return layout

    layout.split_column(
        Layout(name="top", ratio=8),
        Layout(_command_panel(view), name="commands", size=spec.bottom_height),
    )
    layout["top"].split_row(
        Layout(_story_panel(view), name="story", ratio=7),
        Layout(_sidebar_panel(view.sidebar_sections), name="sidebar", ratio=3),
    )
    return layout


def _journal_sections(journal: JournalView) -> Group:
    notes = journal.notes or ["No notes discovered yet."]
    side_objectives = journal.side_objectives or ["No side objectives."]
    main_objective = journal.main_objective or "No main objective set."

    rows: list[Text] = [
        Text("Main Objective", style="bold"),
        Text(main_objective),
        Text(""),
        Text("Side Objectives", style="bold"),
    ]
    rows.extend(Text(f"• {item}") for item in side_objectives)
    rows.extend([Text(""), Text("Notes", style="bold")])
    rows.extend(Text(f"• {item}") for item in notes)
    return Group(*rows)


def build_journal_overlay(view: SceneView) -> Layout:
    journal = view.journal or JournalView()
    layout = Layout(name="root")
    body = Panel(
        _journal_sections(journal),
        title="Journal",
        subtitle="Press Enter to return",
        border_style="grey39",
        padding=(1, 2),
    )
    layout.update(body)
    return layout
