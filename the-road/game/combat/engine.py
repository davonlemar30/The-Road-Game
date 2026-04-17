"""1v1 combat engine for the first Astari playable slice."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Optional

from game.combat.data import CUBE_MODIFIERS
from game.combat.models import BattleResult, BattleState, Combatant, Move
from game.combat.renderer import BattleRenderer

_STATUS_SET = {"Burn", "Drenched", "Rooted", "Confused"}
_TYPE_ADVANTAGE: dict[tuple[str, str], float] = {
    ("Fire", "Air"): 2.0,
    ("Water", "Fire"): 2.0,
    ("Earth", "Water"): 2.0,
    ("Air", "Earth"): 2.0,
}


@dataclass
class Action:
    kind: str
    move: Move | None = None


class Scene3MurkmindScript:
    """Canon-driven wrapper around the 1v1 loop for the Lake Ambush.

    - Turn 2: pressure spike narration + outer pressure-spike choice hook.
    - Turn 3: forced capture sequence (Switch pulse → Nate signals → Cube from bag).
    - Lethal hits on the player are clamped to leave 1 HP before the capture fires;
      canon Scene 3: GP is outmatched but "keeps finding their feet" until the window.
    """

    def __init__(
        self,
        on_pressure_spike: Optional[Callable[[BattleState], None]] = None,
    ) -> None:
        self.pressure_spike_triggered = False
        self.capture_sequence_triggered = False
        self.on_pressure_spike = on_pressure_spike
        self._pressure_hook_fired = False

    def opening_lines(self) -> list[str]:
        return [
            "This is not clean. This is survival.",
        ]

    def on_turn_start(self, battle: BattleState) -> tuple[list[str], str | None]:
        """Return (narration_lines, forced_result) for this turn.

        forced_result == "captured" tells the engine to run the scripted
        capture sequence instead of a normal exchange.
        """
        lines: list[str] = []
        forced_result: str | None = None

        if battle.turn_number == 2 and not self.pressure_spike_triggered:
            self.pressure_spike_triggered = True
            lines.extend(
                [
                    "Pressure spikes. Your thoughts skid.",
                    "Bob's Switch starts to hum in your pocket.",
                ]
            )
        if battle.turn_number == 3 and not self.capture_sequence_triggered:
            self.capture_sequence_triggered = True
            forced_result = "captured"
        return lines, forced_result

    def capture_narration(self) -> list[str]:
        return [
            "You trigger the Switch pulse — resonance snaps out of phase.",
            "Murkmind buckles and drops hard to the stone.",
            "Nate jerks half-upright. 'Now. Cube. My bag — throw it.'",
            "You pull a Cube from Nate's bag and send it in one clean arc.",
            "The Cube seals with a hard flash. Captured.",
            "Nate slumps back. He doesn't get up.",
        ]

    def protect_player(self, player: Combatant, incoming_damage: int) -> int:
        """Clamp lethal damage so the scripted fight can't end the player before
        the capture window. Leaves exactly 1 HP on an otherwise-lethal hit."""
        if self.capture_sequence_triggered:
            return incoming_damage
        if player.current_hp - incoming_damage <= 0:
            return max(0, player.current_hp - 1)
        return incoming_damage


class BattleEngine:
    def __init__(self, renderer, rng: random.Random | None = None) -> None:
        self.output = BattleRenderer(renderer)
        self.rng = rng or random.Random()
        self._script: Scene3MurkmindScript | None = None

    def run(self, battle: BattleState, script: Scene3MurkmindScript | None = None) -> BattleResult:
        self._script = script
        try:
            intro = script.opening_lines() if script else []
            self.output.intro(battle, intro)

            while True:
                if script:
                    lines, forced = script.on_turn_start(battle)
                    self.output.lines(lines)
                    if (
                        script.pressure_spike_triggered
                        and not script._pressure_hook_fired
                    ):
                        script._pressure_hook_fired = True
                        if script.on_pressure_spike is not None:
                            script.on_pressure_spike(battle)
                    if forced == "captured":
                        return self._run_forced_capture(battle, script)
                self.output.status(battle)

                player_action = self._choose_player_action(battle)
                enemy_action = self._choose_enemy_action(battle)
                turn_actions = self._ordered_actions(battle, player_action, enemy_action)

                for actor, target, action in turn_actions:
                    if not actor.is_active() or not target.is_active():
                        continue
                    if action.kind == "fight" and action.move:
                        self._resolve_move(actor, target, action.move)
                    elif action.kind == "capture":
                        result = self._attempt_capture(battle, target)
                        if result:
                            return result
                    elif action.kind == "flee":
                        self.output.lines(["You break contact and run the trail."])
                        return self._result("fled", battle)
                    elif action.kind == "switch":
                        self._resolve_switch(battle)

                    result = self._check_battle_end(battle)
                    if result:
                        return result

                self._end_of_turn(battle)
                result = self._check_battle_end(battle)
                if result:
                    return result

                battle.turn_number += 1
        finally:
            self._script = None

    def _run_forced_capture(
        self, battle: BattleState, script: Scene3MurkmindScript
    ) -> BattleResult:
        self.output.lines(script.capture_narration())
        enemy = battle.enemy_active
        enemy.current_hp = 0
        enemy.will_broken = True
        return self._result("captured", battle, captured_species=enemy.species_id)

    def _choose_player_action(self, battle: BattleState) -> Action:
        actions = ["Fight"]
        if battle.battle_kind == "wild":
            actions.append("Capture")
            actions.append("Flee")
        if any(c.is_active() for c in battle.player_reserve):
            actions.append("Switch")

        idx = self.output.choose_action(actions)
        choice = actions[idx]
        if choice == "Fight":
            move_idx = self.output.choose_move(battle.player_active.moves)
            return Action(kind="fight", move=battle.player_active.moves[move_idx])
        if choice == "Capture":
            return Action(kind="capture")
        if choice == "Flee":
            return Action(kind="flee")
        return Action(kind="switch")

    def _choose_enemy_action(self, battle: BattleState) -> Action:
        choices = [mv for mv in battle.enemy_active.moves if mv.power > 0]
        return Action(kind="fight", move=self.rng.choice(choices or battle.enemy_active.moves))

    def _ordered_actions(
        self,
        battle: BattleState,
        player_action: Action,
        enemy_action: Action,
    ) -> list[tuple[Combatant, Combatant, Action]]:
        p = battle.player_active
        e = battle.enemy_active
        if p.speed > e.speed:
            return [(p, e, player_action), (e, p, enemy_action)]
        if e.speed > p.speed:
            return [(e, p, enemy_action), (p, e, player_action)]
        if self.rng.random() < 0.5:
            return [(p, e, player_action), (e, p, enemy_action)]
        return [(e, p, enemy_action), (p, e, player_action)]

    def _resolve_move(self, actor: Combatant, target: Combatant, move: Move) -> None:
        if actor.status == "Confused" and self.rng.random() < 0.33:
            self_dmg = max(1, actor.max_hp // 12)
            actor.current_hp = max(0, actor.current_hp - self_dmg)
            self.output.lines([f"{actor.name} stumbles in confusion and takes {self_dmg} damage."])
            self._check_will_break(actor)
            return

        if move.accuracy is not None and self.rng.randint(1, 100) > move.accuracy:
            self.output.lines([f"{actor.name} uses {move.name}, but it misses."])
            return

        for line in move.text_lines:
            self.output.lines([f"{actor.name}: {line}"])

        damage = self._calculate_damage(actor, target, move)
        if self._script is not None and target.owner == "player":
            damage = self._script.protect_player(target, damage)
        target.current_hp = max(0, target.current_hp - damage)
        self.output.lines([f"{target.name} takes {damage} damage."])
        self._check_will_break(target)

        if target.is_active() and move.effect in _STATUS_SET and target.status is None:
            chance = move.effect_chance if move.effect_chance is not None else 1.0
            if self.rng.random() <= chance:
                target.status = move.effect
                self.output.lines([f"{target.name} is now {move.effect}."])

    def _calculate_damage(self, actor: Combatant, target: Combatant, move: Move) -> int:
        level_term = (2 * actor.level / 5) + 2
        base = ((level_term * move.power * actor.attack / max(1, target.defense)) / 50) + 2
        type_mod = self._type_modifier(move.type, target)
        stab_mod = 1.5 if move.type == actor.primary_type else 1.0
        path_mod = self._path_modifier(actor.path_alignment)

        total = base
        total *= type_mod
        total *= stab_mod
        total *= path_mod

        if type_mod > 1.0:
            self.output.lines(["It's type-advantaged!"])
        elif type_mod < 1.0:
            self.output.lines(["It's resisted."])

        return max(1, int(total))

    def _type_modifier(self, attack_type: str, target: Combatant) -> float:
        if attack_type == target.primary_type:
            return 0.5
        return _TYPE_ADVANTAGE.get((attack_type, target.primary_type), 1.0)

    def _path_modifier(self, path_alignment: str) -> float:
        if path_alignment in {"base", "seraph"}:
            return 1.0
        return 1.0

    def _check_will_break(self, target: Combatant) -> None:
        if target.current_hp <= 0:
            target.current_hp = 0
            target.will_broken = True
            self.output.lines([f"{target.name}'s Will breaks."])

    def _end_of_turn(self, battle: BattleState) -> None:
        for c in (battle.player_active, battle.enemy_active):
            if not c.is_active():
                continue
            if c.status == "Burn":
                burn = max(1, c.max_hp // 16)
                c.current_hp = max(0, c.current_hp - burn)
                self.output.lines([f"Burn scorches {c.name} for {burn} damage."])
                self._check_will_break(c)

    def _attempt_capture(self, battle: BattleState, target: Combatant) -> BattleResult | None:
        if battle.battle_kind != "wild":
            self.output.lines(["You can only capture in wild encounters."])
            return None
        if battle.player_cubes <= 0:
            self.output.lines(["No Cubes left."])
            return None
        if not target.will_broken:
            self.output.lines([f"{target.name} is still resisting. Capture isn't stable yet."])
            return None

        battle.player_cubes -= 1
        cube_mod = CUBE_MODIFIERS["Standard Cube"]
        chance = min(0.95, 0.6 * cube_mod + (0.25 if target.will_broken else 0.0))
        if self.rng.random() <= chance:
            self.output.lines(["Capture successful."])
            return self._result("captured", battle, captured_species=target.species_id)

        self.output.lines(["The Cube cracks open — capture failed."])
        return None

    def _resolve_switch(self, battle: BattleState) -> None:
        for idx, reserve in enumerate(battle.player_reserve):
            if reserve.is_active():
                battle.player_reserve[idx] = battle.player_active
                battle.player_active = reserve
                self.output.lines([f"Switch complete. {reserve.name} takes point."])
                return
        self.output.lines(["No valid Astari to switch to."])

    def _check_battle_end(self, battle: BattleState) -> BattleResult | None:
        if battle.enemy_active.will_broken:
            if battle.battle_kind == "wild":
                if not battle.notes.get("enemy_break_announced"):
                    self.output.lines(["Enemy is broken. Capture is now valid."])
                    battle.notes["enemy_break_announced"] = True
            else:
                return self._result("won", battle)
        if battle.player_active.will_broken:
            if not any(c.is_active() for c in battle.player_reserve):
                return self._result("lost", battle)
        return None

    def _result(
        self,
        result_type: str,
        battle: BattleState,
        captured_species: str | None = None,
    ) -> BattleResult:
        return BattleResult(
            result_type=result_type,
            captured_species=captured_species,
            player_hp_end=battle.player_active.current_hp,
            enemy_will_broken=battle.enemy_active.will_broken,
            notes=battle.notes,
        )
