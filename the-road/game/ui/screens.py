"""Screen composition helpers for fixed terminal layouts."""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from shutil import get_terminal_size

from game.ui.view_models import SceneView, SidebarSection


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
    bottom = 7
    return FrameSpec(cols, rows, left, right, bottom, False)


def _wrap_lines(lines: list[str], width: int) -> list[str]:
    out: list[str] = []
    for line in lines:
        if not line.strip():
            out.append("")
            continue
        out.extend(textwrap.wrap(line, width=width, replace_whitespace=False) or [""])
    return out


def _box(title: str, lines: list[str], width: int, height: int) -> list[str]:
    title_text = f" {title} " if title else ""
    top_fill = max(0, width - 2 - len(title_text))
    top = "┌" + title_text + "─" * top_fill + "┐"
    bot = "└" + "─" * (width - 2) + "┘"
    inner_w = width - 2

    wrapped = _wrap_lines(lines, inner_w - 2)
    clipped = wrapped[: max(0, height - 2)]
    while len(clipped) < max(0, height - 2):
        clipped.append("")

    body = [f"│ {row[:inner_w-2]:<{inner_w-2}} │" for row in clipped]
    return [top, *body, bot]


def _build_sidebar_lines(sections: list[SidebarSection], width: int, height: int) -> list[str]:
    inner = width - 2
    lines: list[str] = []
    for idx, section in enumerate(sections):
        if idx > 0:
            lines.append("")
        lines.append(f"[{section.title}]")
        if section.lines:
            for line in section.lines:
                lines.extend(_wrap_lines([line], inner - 2))
        else:
            lines.append("-")
    return lines[: max(0, height - 2)]


def build_fixed_frame(view: SceneView) -> str:
    spec = compute_frame_spec()
    top_height = max(10, spec.height - spec.bottom_height - 2)

    # Main story pane
    main_lines = view.main_lines[:]
    if view.speaker_name:
        main_lines = [f"{view.speaker_name}", ""] + main_lines
    if view.footer_hint:
        main_lines += ["", view.footer_hint]

    if spec.small_terminal:
        story = _box(view.location_name or "Scene", main_lines, spec.width, top_height)
        sidebar_lines = _build_sidebar_lines(view.sidebar_sections, spec.width, top_height)
        sidebar = _box("World", sidebar_lines, spec.width, min(12, top_height))
        command_lines = []
        for i, a in enumerate(view.suggested_actions[:4], 1):
            command_lines.append(f"[{i}] {a}")
        if view.current_choices:
            command_lines.append("Choices: " + " | ".join(str(i + 1) for i in range(len(view.current_choices))))
        command_lines.append(view.input_prompt)
        command = _box("Commands", command_lines, spec.width, spec.bottom_height)
        return "\n".join([*story, *sidebar, *command])

    left_lines = _box(view.location_name or "Scene", main_lines, spec.left_width, top_height)
    sidebar_content = _build_sidebar_lines(view.sidebar_sections, spec.right_width, top_height)
    right_lines = _box("World", sidebar_content, spec.right_width, top_height)

    combined_top = [
        left_lines[i] + " " + right_lines[i]
        for i in range(min(len(left_lines), len(right_lines)))
    ]

    command_lines: list[str] = []
    for i, action in enumerate(view.suggested_actions[:4], 1):
        command_lines.append(f"[{i}] {action}")
    if view.current_choices:
        for i, choice in enumerate(view.current_choices[:4], 1):
            command_lines.append(f"[{i}] {choice}")
    command_lines.append(view.input_prompt)

    bottom = _box("Commands", command_lines, spec.width, spec.bottom_height)
    return "\n".join([*combined_top, *bottom])
