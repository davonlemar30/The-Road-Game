"""Combat domain models for the 1v1 Astari MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

CombatOwner = Literal["player", "enemy"]
BattleKind = Literal["wild", "trainer", "scripted"]
PathAlignment = Literal["base", "seraph", "infernal"]


@dataclass
class Move:
    move_id: str
    name: str
    type: str
    power: int
    accuracy: int | None = None
    effect: str | None = None
    effect_chance: float | None = None
    text_lines: list[str] = field(default_factory=list)


@dataclass
class Combatant:
    name: str
    species_id: str
    level: int
    primary_type: str
    secondary_type: str | None
    max_hp: int
    current_hp: int
    attack: int
    defense: int
    resolve: int
    speed: int
    moves: list[Move]
    status: str | None
    owner: CombatOwner
    is_wild: bool
    bond_level: int
    path_alignment: PathAlignment = "base"
    will_broken: bool = False

    def is_active(self) -> bool:
        return not self.will_broken and self.current_hp > 0


@dataclass
class BattleState:
    player_active: Combatant
    enemy_active: Combatant
    player_reserve: list[Combatant] = field(default_factory=list)
    battle_kind: BattleKind = "wild"
    player_cubes: int = 0
    turn_number: int = 1
    notes: dict[str, bool] = field(default_factory=dict)


@dataclass
class BattleResult:
    result_type: Literal["won", "lost", "captured", "fled"]
    captured_species: str | None
    player_hp_end: int
    enemy_will_broken: bool
    notes: dict[str, bool] = field(default_factory=dict)
