"""Terminal text helper for combat beats."""

from __future__ import annotations

from game.combat.models import BattleState, Move


class BattleRenderer:
    def __init__(self, renderer) -> None:
        self.renderer = renderer

    def intro(self, battle: BattleState, lines: list[str] | None = None) -> None:
        header = [
            "",
            "╭─ Astari Encounter ─────────────────────────────",
            f"Your {battle.player_active.name} vs {battle.enemy_active.name}",
            "╰────────────────────────────────────────────────",
        ]
        if lines:
            header.extend(lines)
        self.renderer.show_lines(header)

    def status(self, battle: BattleState) -> None:
        p = battle.player_active
        e = battle.enemy_active
        self.renderer.show_lines(
            [
                "",
                f"Turn {battle.turn_number}",
                f"{p.name}: {p.current_hp}/{p.max_hp} HP" + (f" [{p.status}]" if p.status else ""),
                f"{e.name}: {e.current_hp}/{e.max_hp} HP" + (f" [{e.status}]" if e.status else ""),
            ]
        )

    def choose_action(self, actions: list[str]) -> int:
        idx = self.renderer.show_menu("Choose action:", actions)
        return idx

    def choose_move(self, moves: list[Move]) -> int:
        options = [f"{mv.name} ({mv.type}, Pow {mv.power})" for mv in moves]
        return self.renderer.show_menu("Choose move:", options)

    def lines(self, lines: list[str]) -> None:
        self.renderer.show_lines(lines)
