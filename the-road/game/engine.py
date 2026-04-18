"""Main game engine and command loop."""

from __future__ import annotations

from data.dialogue_data import MOTHER_SCENE1_PART1, MOTHER_SCENE1_PART2
from data.npcs import NPCS
from game.dialogue import DialogueManager
from game.dialogue_session import Beat, DialogueSession
from game.map_renderer import render_map
from game.objectives import ObjectiveTracker
from game.parser import parse_command
from game.persistence import SAVE_FILE, load_game, save_game
from game.astari import (
    MURKMIND_SCENE3_INSTANCE_ID,
    build_owned_murkmind,
    find_owned,
)
from game.choices import run_scene_choice
from game.state import GameState
from game.timekeeper import advance_time, format_time_label
from game.town import TownWorld
from game.ui import Renderer
from game.ui.view_models import HudData, JournalView, SceneView, SidebarSection
from game.world import World


class GameEngine:
    def __init__(self) -> None:
        self.state = GameState()
        self.world = World()
        self.town = TownWorld()
        self.objectives = ObjectiveTracker()
        self.dialogue = DialogueManager()
        self.renderer = Renderer()

    def run(self) -> None:
        try:
            loaded = self._show_main_menu()
            if not loaded:
                self._show_intro()
                self._prompt_player_name()
                self._set_objective("look_around")
                self.renderer.show_system("\nType 'look' to take in your room.")

            while self.state.running:
                view = self._build_view()
                self.renderer.render(view)
                raw = self.renderer.get_input()
                if raw.strip().isdigit():
                    idx = int(raw.strip()) - 1
                    if 0 <= idx < len(view.suggested_actions):
                        raw = view.suggested_actions[idx]
                verb, arg = parse_command(raw)
                self._handle_command(verb, arg)
        finally:
            self.renderer.close()

    # ── Startup ──────────────────────────────────────────────────────────────

    def _show_main_menu(self) -> bool:
        """
        Display the title screen and main menu.
        Returns True if a save was loaded (skip new-game setup).
        Returns False to start a new game.
        """
        import os

        self.renderer.show_title()

        save_exists = os.path.exists(SAVE_FILE)
        options = ["New Game", "Load Game", "Quit"] if save_exists else ["New Game", "Quit"]

        idx = self.renderer.show_menu("", options)
        choice = options[idx]

        if choice == "Quit":
            self.state.running = False
            return True  # skip new-game setup; while loop exits immediately

        if choice == "Load Game":
            ok, result = load_game()
            if ok:
                self.state = result
                self.renderer.show_system(f"\nWelcome back, {self.state.player_name}.")
                self.renderer.show_system(f"Current objective: {self.state.current_objective}")
                self.renderer.show_system("\nType 'look' to get your bearings.")
                return True
            else:
                self.renderer.show_system(f"\nCould not load save: {result}")
                self.renderer.show_system("Starting a new game instead.")

        # "New Game" (or failed load)
        return False

    def _show_intro(self) -> None:
        self.renderer.show_system(
            "\nYou wake where you've always been: "
            "waiting for movement to become a decision."
        )
        self.renderer.show_system(
            "The room is the same. Morning light through the curtains. "
            "The house is already awake below you."
        )

    def _build_view(self) -> SceneView:
        """Build a SceneView snapshot from the current runtime state."""
        location_name = self._current_location_name()
        suggested_actions = self._suggested_actions()
        sidebar_sections = self._build_sidebar_sections(location_name)
        return SceneView(
            current_mode="explore",
            location_name=location_name,
            suggested_actions=suggested_actions,
            sidebar_sections=sidebar_sections,
            hud=HudData(
                player_name=self.state.player_name,
                location_name=location_name,
                time_label=self.state.time_label,
                money=self.state.money,
                objective=self.state.current_objective,
                reputation=self.state.reputation,
            ),
        )

    def _reputation_label(self) -> str:
        rep = self.state.reputation
        if rep <= 0:
            return "Unknown"
        if rep <= 2:
            return "Noticed"
        if rep <= 4:
            return "Known"
        return "Respected"

    def _context_hint(self) -> list[str]:
        """Return a context-sensitive hint line, or nothing if no useful hint applies."""
        loc = self.state.current_location
        flags = self.state.flags
        if flags.get("scene4_started") and not flags.get("scene4_completed") \
                and loc == "mystic_trail_safe_hollow":
            missing = []
            if not flags.get("water_secured"):
                missing.append("gather water")
            if not flags.get("camp_secured"):
                missing.append("prepare camp")
            if not missing:
                return ["rest when ready"]
            return [" · ".join(missing)]
        if not flags.get("in_town") and not flags.get("mom_talked"):
            return ["talk mom"]
        if flags.get("saw_fog_boundary"):
            return ["fog boundary reached"]
        return []

    def _build_sidebar_sections(self, location_name: str) -> list[SidebarSection]:
        sections: list[SidebarSection] = [
            SidebarSection("Location", [location_name, self.state.time_label]),
            SidebarSection(
                "Player",
                [
                    f"Name: {self.state.player_name or 'Unknown'}",
                    f"Standing: {self._reputation_label()}",
                ],
            ),
        ]

        if self.state.inventory:
            sections.append(SidebarSection("Inventory", self.state.inventory[:4]))

        if self.state.flags["in_town"]:
            node = self.town.get_node(self.state.current_location)
            npcs = node.get("visible_npcs", [])
            if npcs:
                sections.append(SidebarSection("Nearby", npcs[:4]))
        else:
            if self.state.current_location == "living_room" and not self.state.flags["mom_talked"]:
                sections.append(SidebarSection("Nearby", ["Your mom is here"]))

        hint_lines = self._context_hint()
        if hint_lines:
            sections.append(SidebarSection("Hint", hint_lines))
        return sections

    def _suggested_actions(self) -> list[str]:
        actions = ["look", "where", "inventory", "help"]

        if self.state.flags["in_town"]:
            if (
                self.state.flags.get("scene4_started")
                and not self.state.flags.get("scene4_completed")
                and self.state.current_location == "mystic_trail_safe_hollow"
            ):
                actions.extend(["gather water", "prepare camp", "rest"])
                if not self.state.flags.get("campfire_lit"):
                    actions.append("light fire")
                return actions[:6]
            node = self.town.get_node(self.state.current_location)
            neighbors = node.get("neighbors", [])[:2]
            for neighbor_id in neighbors:
                actions.append(f"go {self.town.get_node(neighbor_id)['name'].lower()}")
            npcs = node.get("visible_npcs", [])
            if npcs:
                actions.append(f"talk {npcs[0].split()[0].lower()}")
            if node.get("shops"):
                actions.append("browse")
        else:
            exits = self.world.get_location(self.state.current_location).get("exits", {})
            # Deduplicate by destination so aliases (down/downstairs) don't both appear.
            seen_dests: set[str] = set()
            for exit_name, dest in exits.items():
                if dest not in seen_dests:
                    seen_dests.add(dest)
                    actions.append(f"go {exit_name}")
                    if len(seen_dests) >= 2:
                        break
            if self.state.current_location == "living_room":
                actions.append("talk mom")

        # preserve order, remove duplicates
        seen: set[str] = set()
        ordered: list[str] = []
        for action in actions:
            if action not in seen:
                seen.add(action)
                ordered.append(action)
        return ordered[:6]

    def _current_location_name(self) -> str:
        if self.state.flags["in_town"]:
            return self.town.get_node(self.state.current_location)["name"]
        return self.world.get_location(self.state.current_location)["name"]

    def _prompt_player_name(self) -> None:
        while not self.state.player_name:
            name = self.renderer.get_text_input("\nWhat is your name? ").strip()
            if name:
                self.state.player_name = name
            else:
                self.renderer.show_system("Please enter a name.")
        self.renderer.show_system("\nThat's the name you've carried this long. Might as well keep it.")

    # ── Command dispatch ─────────────────────────────────────────────────────

    def _handle_command(self, verb: str, arg: str) -> None:
        if not verb:
            if self.state.flags["in_town"]:
                self.renderer.show_system(
                    "Type a command. Try: look, go square, where, inspect door, talk bob, help."
                )
            else:
                self.renderer.show_system(
                    "Type a command. Try: look, go downstairs, inspect mirror, talk mom, help."
                )
            return

        handlers = {
            "look":      self._cmd_look,
            "go":        self._cmd_go,
            "enter":     self._cmd_enter,
            "inspect":   self._cmd_inspect,
            "talk":      self._cmd_talk,
            "ask":       self._cmd_ask,
            "browse":    self._cmd_browse,
            "buy":       self._cmd_buy,
            "where":     self._cmd_where,
            "map":       self._cmd_map,
            "use":       self._cmd_use,
            "inventory": self._cmd_inventory,
            "log":       self._cmd_log,
            "save":      self._cmd_save,
            "load":      self._cmd_load,
            "help":      self._cmd_help,
            "objective": self._cmd_objective,
            "journal":   self._cmd_journal,
            "status":    self._cmd_status,
            "quit":      self._cmd_quit,
        }

        handler = handlers.get(verb)
        if handler is None:
            self._handle_unknown(verb, arg)
            return

        handler(arg)

    def _set_objective(self, key: str, *, added: bool = False) -> None:
        previous_objective = self.state.current_objective
        message = self.objectives.set_objective(self.state, key, added=added)
        self.renderer.show_system(message)
        if previous_objective and previous_objective not in self.state.side_objectives:
            self.state.side_objectives.append(previous_objective)
        if self.state.current_objective and self.state.current_objective not in self.state.journal_notes:
            self.state.journal_notes.append(self.state.current_objective)

    # ── Handlers ─────────────────────────────────────────────────────────────

    def _cmd_look(self, _arg: str) -> None:
        self.renderer.clear_story()
        if self.state.flags["in_town"]:
            self.renderer.show_location(self.town.describe(self.state.current_location))
        else:
            desc = self.world.describe_location(self.state.current_location)
            # If mom is present in the living room, mention her in the look description
            if (
                self.state.current_location == "living_room"
                and self.state.flags["met_mother"]
                and not self.state.flags["mom_talked"]
            ):
                desc += "\n\nYour mom is in her chair. She's aware of you."
            elif (
                self.state.current_location == "living_room"
                and self.state.flags["mom_talked"]
            ):
                desc += "\n\nYour mom is still in her chair. She gives you a look that says: go."
            self.renderer.show_location(desc)

    def _cmd_go(self, arg: str) -> None:
        if self.state.flags["in_town"]:
            self._cmd_go_town(arg)
        else:
            self._cmd_go_house(arg)

    def _cmd_go_house(self, arg: str) -> None:
        direction = arg.strip().lower()
        if not direction:
            self.renderer.show_system(
                "Go where? Try: go downstairs  /  go kitchen  /  go front door  /  go out"
            )
            return

        # Any exit that leads to "outside" in the front_door exits dict means
        # the player wants to leave the house — route to _transition_to_town.
        if self.state.current_location == "front_door":
            exits = self.world.get_location("front_door")["exits"]
            if exits.get(direction) == "outside":
                if not self.state.flags["mom_talked"]:
                    self.renderer.show_system(
                        "Something holds you at the threshold. "
                        "You haven't talked to your mom yet — not really."
                    )
                    return
                self._transition_to_town()
                return

        success, result = self.world.move(self.state.current_location, direction)
        if not success:
            self.renderer.show_system(result)
            return

        self.state.current_location = result
        advance_time(self.state, 5)
        # Auto-look: clear stale content and show the new room immediately so
        # the story pane, title, and sidebar all reflect the same location.
        self._cmd_look("")
        # Location-entry events append below the fresh room description.
        self._on_location_entered(result)

    def _cmd_go_town(self, arg: str) -> None:
        target = arg.strip()
        if not target:
            self.renderer.show_system(
                "Go where? Example: go square  /  go keeper's dome  /  go market"
            )
            return
        target_key = target.lower()

        if (
            self.state.flags.get("scene4_started")
            and not self.state.flags.get("scene4_completed")
            and self.state.current_location == "mystic_trail_safe_hollow"
        ):
            self.renderer.show_system(
                "Nate isn't stable enough. Get water and shelter first."
            )
            return

        # Allow returning to GP's House from Front Street for post-Scene-4 Mom path.
        if self.state.current_location == "front_street" and target_key in {
            "house", "home", "gp house", "front door", "door", "inside", "in",
        }:
            self.state.flags["in_town"] = False
            self.state.current_location = "front_door"
            advance_time(self.state, 5)
            self._cmd_look("")
            return

        # "go inside" / "go in" → treat as enter command at current location
        if target_key in {"inside", "in", "through", "through the door"}:
            self._cmd_enter("")
            return

        if (
            self.state.current_location == "mystic_trail_fog_boundary"
            and target_key in {
                "farther", "further", "enter fog", "fog", "forbidden trail", "go forbidden trail",
                "beyond", "go beyond", "deeper", "go deeper",
            }
        ):
            self._handle_fog_boundary_attempt()
            return

        success, result = self.town.move_to(self.state.current_location, target)
        if not success:
            self.renderer.show_system(result)
            return

        self.state.current_location = result
        advance_time(self.state, 15)
        # Auto-look: clear stale content and show the new location immediately.
        self._cmd_look("")
        self._on_town_node_entered(result)

    def _cmd_inspect(self, arg: str) -> None:
        if not arg:
            self.renderer.show_system("Inspect what? (example: inspect mirror)")
            return

        if self.state.flags["in_town"]:
            result = self.town.inspect(self.state.current_location, arg)
        else:
            result = self.world.inspect(self.state.current_location, arg)

        self.renderer.render(SceneView(
            current_mode="inspect",
            inspect_target=arg.strip(),
            inspect_text=result,
        ))
        self.renderer.invalidate_hud()

    def _cmd_enter(self, arg: str) -> None:
        """Handle 'enter', 'open door', 'knock', 'go inside' in town."""
        if not self.state.flags["in_town"]:
            self.renderer.show_system("There's nothing to enter here.")
            return

        loc = self.state.current_location
        if loc == "mystic_trail_fog_boundary" and arg.strip().lower() in {
            "", "fog", "the fog", "forbidden trail", "beyond", "deeper",
        }:
            self._handle_fog_boundary_attempt()
            return

        if loc == "keepers_dome":
            if not self.state.flags["dome_entered"]:
                # Should have been triggered on arrival — fire it now if missed
                self.state.flags["dome_entered"] = True
                self._scene2_hook()
                return

            # Scene 2 interior: Audri farewell + Keeper Bob Codex handoff
            if not self.state.flags["codex_given"]:
                self.state.flags["codex_given"] = True
                if "Nate's Codex Parcel" not in self.state.inventory:
                    self.state.inventory.append("Nate's Codex Parcel")

                # ── Dialogue Mode: three-beat Bob session ─────────────────────
                # Beat 1: Audri exit → Bob opener → "Who was that?" choice
                # Beat 2: Codex explanation (pulls parcel, explains situation)
                # Beat 3: Closing context + Codex handoff choice
                player = self.state.player_name or "you"
                session = DialogueSession(
                    npc_name="Keeper Bob",
                    portrait_id="npc_bob",
                    beats=[
                        Beat(
                            lines=[
                                "The space inside the Dome smells like ozone, dried herbs, and old wood.",
                                "Keeper Bob is at the worktable, hands busy. He doesn't look up yet.",
                                "A young woman stands near the far side of the table.",
                                "She doesn't fill the room with noise. But the room feels different with her in it.",
                                'Bob\'s voice, steady: "All five Crests. You\'ve done this town proud."',
                                "The young woman nods once.",
                                '"I\'m staying in Iso Town for a bit," she says. "Rest. Prep. Then I\'m back on the road."',
                                'Bob: "The road doesn\'t wait."',
                                '"Neither do I."',
                                "She turns to leave.",
                                "As she passes the threshold, she pauses.",
                                "Her eyes find yours — warm, curious. Just for a second.",
                                "Then she's gone, the door easing shut behind her.",
                                "The Dome feels too quiet. Like the air is deciding what to do now that she isn't in it.",
                                f'Keeper Bob finally turns to you. "Ah. Good timing, {player}," he says.',
                                '"I need a favor."',
                            ],
                            choice_id="audri_who_choice",
                        ),
                        Beat(
                            lines=[
                                "He reaches into the tray labeled PENDING and pulls out a small parcel.",
                                '"This keeps ending up right back where it started," he mutters.',
                                '"I\'ve been trying to get it to Nate for over a week."',
                                "He taps the tag with one finger.",
                                '"His Codex."',
                                "He watches your face, like he's waiting for you to object.",
                                '"You know that spot you two used to hang at? The overlook above the lake, on Mystic Trail?"',
                                '"Nate went out there last night and hasn\'t come back."',
                                '"Goddamn it — I meant to ask Audri to look into it while she was here."',
                                "He holds the parcel out.",
                                '"Take it to him."',
                            ],
                        ),
                        Beat(
                            lines=[
                                '"Be careful with it. Useful, but delicate."',
                                "His voice softens slightly. Not sentiment — patience.",
                                '"And... yeah. I\'ve got a second Codex back here."',
                                '"Just saying."',
                                "He doesn't push you toward it. He just lets that truth sit in the room.",
                                '"Mystic Trail is usually fine, but lately the path\'s been feeling off."',
                                '"So be careful."',
                                "",
                                "Before you go, he reaches under the bench.",
                                "Two things, set on the table without ceremony.",
                                "A small field switch. An empty cube sealed at the hinge.",
                                '"Insurance," he says. "Not a plan. Don\'t lose the cube."',
                            ],
                            choice_id="bob_codex_response",
                        ),
                    ],
                )
                session.run(self.state, self.renderer)
                self.renderer.invalidate_hud()
                self._set_objective("deliver_codex", added=True)
                return

            # Post-delivery follow-up
            if self.state.flags["codex_delivered"]:
                # Ensure mom blessing path is accessible on any fresh save path
                if not self.state.flags.get("mom_blessing_available"):
                    self.state.flags["mom_blessing_available"] = True
                DialogueSession(
                    npc_name="Keeper Bob",
                    portrait_id="npc_bob",
                    beats=[Beat(lines=[
                        "Keeper Bob checks your face before your hands.",
                        '"You found him."',
                        "Not a question.",
                        "A beat. He sets down what he's working on.",
                        '"Before you push deeper — talk to your mom."',
                        '"She should hear it from you, not from the road."',
                        '"After that, Dreamleaf. Bring it back clean."',
                    ])],
                ).run(self.state, self.renderer)
                self.renderer.invalidate_hud()
                self._set_objective("find_dreamleaf")
                return

            reminder = '"Nate needs that Codex. Get it to the overlook."'
            if "bob_codex_accept_cleanly" in self.state.choice_history:
                reminder = '"You said you\'d head out. I\'m still expecting that."'
            elif "bob_codex_ask_urgency" in self.state.choice_history:
                reminder = '"Same answer: the Field is loud, Nate has no guide. Get there."'
            elif "bob_codex_why_me" in self.state.choice_history:
                reminder = '"Still wondering why you? Carry it. Answers come on the road."'
            DialogueSession(
                npc_name="Keeper Bob",
                portrait_id="npc_bob",
                beats=[Beat(lines=[
                    '"You still have it."',
                    "Not accusing. Just noting.",
                    reminder,
                ])],
            ).run(self.state, self.renderer)
            self.renderer.invalidate_hud()
            return

        # Generic response for other locations
        self.renderer.show_system("There's no door to enter here.")

    def _resolve_npc_here(self, target: str) -> str | None:
        target = target.strip().lower()
        if not target:
            return None
        for npc_id, data in NPCS.items():
            if target in data["aliases"] and data["location"] == self.state.current_location:
                return npc_id
        return None

    def _cmd_talk(self, arg: str) -> None:
        target = arg.strip().lower()
        if not target:
            self.renderer.show_system("Talk to who? (example: talk mom)")
            return

        npc_id = self._resolve_npc_here(target)
        if npc_id is None:
            self.renderer.show_system(f"There's no one called '{target}' here.")
            return

        # ── NPC name for Dialogue Mode header ─────────────────────────────────
        npc_name = "Your Mom" if npc_id == "mother" else NPCS[npc_id]["name"]

        if npc_id == "mother":
            was_talked = self.state.flags["mom_talked"]
            lines, hint = self.dialogue.talk_to_mother(self.state)

            if not was_talked and self.state.flags["mom_talked"]:
                # ── First encounter: Dialogue Mode, two-beat session ──────────
                # Beat A: "Mornin', baby. You sleep okay?" → sleep response
                # Beat B: Bob's visit + Nate news → nate response
                session = DialogueSession(
                    npc_name=npc_name,
                    portrait_id="npc_mother",
                    beats=[
                        Beat(lines=MOTHER_SCENE1_PART1, choice_id="mom_sleep_response"),
                        Beat(lines=MOTHER_SCENE1_PART2, choice_id="mom_nate_response"),
                    ],
                    closing_hint="She's here if there's more on your mind.",
                )
                session.run(self.state, self.renderer)
                self.renderer.invalidate_hud()
                self._set_objective("find_bob", added=True)
                return

            # ── Subsequent visits — still use Dialogue Mode for consistency ───
            if lines:
                session = DialogueSession(
                    npc_name=npc_name,
                    portrait_id="npc_mother",
                    beats=[Beat(lines=lines)],
                    closing_hint=hint,
                )
                session.run(self.state, self.renderer)
                self.renderer.invalidate_hud()
            elif hint:
                self.renderer.render(SceneView(current_mode="dialogue", footer_hint=hint))
            return

        elif npc_id == "bob":
            if self.state.current_location == "keepers_dome":
                self.renderer.show_system("He's inside. Step in.")
                return
            lines, hint = [], ""
        else:
            lines, hint = self.dialogue.talk_to_town_npc(npc_id)

        # ── All other NPCs: wrap in Dialogue Mode ────────────────────────────
        # (bob follow-ups, fruit_vendor, old_guard, archivist, etc.)
        # portrait_id intentionally omitted here — generic town NPCs do not
        # have defined portrait art in portraits.py.  Assign explicitly (like
        # the mother/bob branches above) when portrait art is added for an NPC.
        if lines:
            session = DialogueSession(
                npc_name=npc_name,
                portrait_id=f"npc_{npc_id}",
                beats=[Beat(lines=lines)],
                closing_hint=hint,
            )
            session.run(self.state, self.renderer)
            self.renderer.invalidate_hud()
        elif hint:
            self.renderer.render(SceneView(current_mode="dialogue", footer_hint=hint))

    def _cmd_ask(self, arg: str) -> None:
        trimmed = arg.strip().lower()
        if trimmed.startswith("about "):
            topic_only = trimmed[6:].strip()
            candidates = [
                npc_id for npc_id, data in NPCS.items()
                if data["location"] == self.state.current_location
            ]
            if len(candidates) == 1:
                target = candidates[0]
                topic = topic_only
                if target == "mother":
                    before_told = self.state.flags.get("told_mom_plans", False)
                    lines, hint = self.dialogue.ask_mom(self.state, topic)
                    dreamleaf_obj = self.objectives.objectives.get("find_dreamleaf", "")
                    if (not before_told) and self.state.flags.get("told_mom_plans", False) \
                            and self.state.current_objective != dreamleaf_obj:
                        self._set_objective("return_to_dome")
                elif target == "bob":
                    lines, hint = self.dialogue.ask_bob(self.state, topic)
                else:
                    lines, hint = self.dialogue.ask_town_npc(target, topic)
                if lines or hint:
                    self.renderer.render(SceneView(
                        current_mode="dialogue",
                        dialogue_lines=lines or [],
                        footer_hint=hint or "",
                    ))
                return
            self.renderer.show_system("Ask who about that? (example: ask mom about bob)")
            return

        parts = arg.strip().split(maxsplit=1)
        if not parts:
            self.renderer.show_system("Ask who? (example: ask mom nate)")
            return

        target = parts[0].lower()
        topic = parts[1] if len(parts) > 1 else ""

        npc_id = self._resolve_npc_here(target)
        if npc_id is None:
            self.renderer.show_system(f"You don't see '{target}' to ask.")
            return

        if npc_id == "mother":
            before_told = self.state.flags.get("told_mom_plans", False)
            lines, hint = self.dialogue.ask_mom(self.state, topic)
            dreamleaf_obj = self.objectives.objectives.get("find_dreamleaf", "")
            if (not before_told) and self.state.flags.get("told_mom_plans", False) \
                    and self.state.current_objective != dreamleaf_obj:
                self._set_objective("return_to_dome")
        elif npc_id == "bob":
            lines, hint = self.dialogue.ask_bob(self.state, topic)
        else:
            lines, hint = self.dialogue.ask_town_npc(npc_id, topic)
        if lines or hint:
            self.renderer.render(SceneView(
                current_mode="dialogue",
                dialogue_lines=lines or [],
                footer_hint=hint or "",
            ))

    def _cmd_browse(self, arg: str) -> None:
        if not self.state.flags["in_town"]:
            self.renderer.show_system("There's nothing to browse in here.")
            return
        ok, text = self.town.browse(self.state.current_location, arg.strip())
        self.renderer.show_system(text)

    def _cmd_buy(self, arg: str) -> None:
        item = arg.strip().lower()
        if self.state.current_location != "the_market":
            self.renderer.show_system("No one is selling that here.")
            return
        if not item:
            self.renderer.show_system("Buy what? (example: buy water flask)")
            return
        catalog = {
            "dried fruit pack": ("Dried Fruit Pack", 4),
            "fruit": ("Dried Fruit Pack", 4),
            "water flask": ("Clean Water Flask", 3),
            "flask": ("Clean Water Flask", 3),
        }
        if item not in catalog:
            self.renderer.show_system("That isn't on display. Try 'browse'.")
            return
        name, cost = catalog[item]
        if self.state.money < cost:
            self.renderer.show_system(
                f"You only have {self.state.money} gold. {name} costs {cost} gold."
            )
            return
        self.state.money -= cost
        self.state.inventory.append(name)
        self.renderer.show_system(
            f"You buy {name} for {cost} gold. ({self.state.money} gold left.)"
        )

    def _cmd_where(self, _arg: str) -> None:
        if not self.state.flags["in_town"]:
            loc = self.world.get_location(self.state.current_location)
            paths = ", ".join(loc["exits"].keys())
            self.renderer.show_system(f"\nYou're at {loc['name']}. Paths: {paths}")
            return

        node = self.town.get_node(self.state.current_location)
        nearby = self.town.neighbors_text(self.state.current_location)
        self.renderer.show_system(f"\nYou're at {node['name']}. Paths: {nearby}")

    def _cmd_map(self, _arg: str) -> None:
        if not self.state.flags["in_town"]:
            self.renderer.show_system("You're inside. Step outside first.")
            return
        if not self.state.flags["has_old_phone"]:
            self.renderer.show_system("You don't have anything to check a map on.")
            return
        if not self.state.flags["phone_unlocked"]:
            self.renderer.show_system("The phone is off. Type 'use phone' to turn it on.")
            return
        discovered = set(self.state.discovered_locations)
        self.renderer.show_system(render_map(self.state.current_location, discovered))

    def _cmd_use(self, arg: str) -> None:
        item = arg.strip().lower()
        if not item:
            self.renderer.show_system("Use what?")
            return

        if item in {"phone", "old phone", "mom's phone"}:
            self._use_phone()
            return

        self.renderer.show_system(f"You're not sure how to use '{item}'.")

    def _use_phone(self) -> None:
        if not self.state.flags["has_old_phone"]:
            self.renderer.show_system("You don't have a phone.")
            return

        if self.state.flags["phone_unlocked"]:
            self.renderer.show_system(
                "The phone's on. You have: map, field notes (locked), contacts (locked).\n"
                "Type 'map' to see ISO Town."
            )
            return

        # First unlock
        self.state.flags["phone_unlocked"] = True
        self.renderer.show_system(
            "\nThe phone powers on with a low hum. The screen is scratched but clear."
        )
        self.renderer.show_system(
            "There's a map of ISO Town, field notes locked behind a passphrase, "
            "and a contacts list that hasn't been updated in a while."
        )
        self.renderer.show_system("\nType 'map' to see where you are.")

    def _cmd_inventory(self, _arg: str) -> None:
        if not self.state.inventory:
            self.renderer.show_system(f"You're carrying nothing. Gold: {self.state.money}")
        else:
            lines = [f"You have ({self.state.money} gold):"]
            lines.extend(f"  - {item}" for item in self.state.inventory)
            self.renderer.show_lines(lines)

    def _cmd_log(self, _arg: str) -> None:
        """Show a modal overlay of recent exploration log entries."""
        self.renderer.show_log_view()
        self.renderer.invalidate_hud()

    def _cmd_status(self, _arg: str) -> None:
        self.renderer.show_status(self.state, self._current_location_name())

    def _cmd_save(self, _arg: str) -> None:
        if not self.state.player_name:
            self.renderer.show_system("Nothing to save yet.")
            return
        self.renderer.show_system(save_game(self.state))

    def _cmd_load(self, _arg: str) -> None:
        ok, result = load_game()
        if ok:
            self.state = result
            self.renderer.show_system(f"Save loaded. Welcome back, {self.state.player_name}.")
            self.renderer.show_system(f"Current objective: {self.state.current_objective}")
        else:
            self.renderer.show_system(result)

    def _cmd_help(self, _arg: str) -> None:
        lines = [
            "\nCommands:",
            "  look (or l)              — describe where you are",
            "  where                    — quick location + nearby places",
        ]
        if self.state.flags["in_town"]:
            lines.append(
                "  go [place]               — travel by name (e.g. go square  /  go keeper's dome)"
            )
        else:
            lines.append(
                "  go [room or direction]   — e.g. go downstairs  /  go kitchen  /  go out"
            )
        lines += [
            "  inspect [object]         — examine something here",
            "  talk [npc]               — start a conversation  (e.g. talk mom)",
            "  ask [npc] [topic]        — ask something specific (e.g. ask mom nate)",
            "  browse [shop]            — view nearby stalls/shop stock",
            "  buy [item]               — purchase a simple item if available",
            "  ask about [topic]        — shorthand when only one NPC is present",
            "  tell me about [topic]    — natural phrasing, same as ask about",
            "  tell mom [your plan]     — e.g. 'tell mom i'm going' to commit to leaving",
            "  inventory (or inv)       — show what you're carrying",
            "  status                   — open player status hub",
        ]
        if self.state.flags["has_old_phone"]:
            lines.append("  use phone                — open the old phone")
        if self.state.flags["phone_unlocked"]:
            lines.append("  map                      — show ISO Town map")
        lines += [
            "  log                      — show recent exploration log",
            "  objective                — show current objective",
            "  journal                  — open objective + notes journal",
            "  save / load              — save or restore your progress",
            "  help                     — show this list",
            "  quit                     — exit the game",
        ]
        self.renderer.show_lines(lines)

    def _cmd_objective(self, _arg: str) -> None:
        if self.state.current_objective:
            self.renderer.show_system(f"Current objective: {self.state.current_objective}")
        else:
            self.renderer.show_system("No objective set.")
        self.renderer.show_system(f"Current time: {format_time_label(self.state)}")

    def _cmd_journal(self, _arg: str) -> None:
        show_archive = False
        while True:
            view = SceneView(
                current_mode="journal",
                journal=JournalView(
                    main_objective=self.state.current_objective,
                    side_objectives=self.state.side_objectives if show_archive else [],
                    notes=self.state.journal_notes if show_archive else [],
                ),
            )
            self.renderer.render(view)
            raw = self.renderer.get_input(
                "\nenter to close · 'more' to show past objectives > "
            ).strip().lower()
            if raw in {"", "close", "exit"}:
                break
            if raw in {"more", "m", "toggle"}:
                show_archive = not show_archive

    def _cmd_quit(self, _arg: str) -> None:
        if self.state.flags["in_town"]:
            self.renderer.show_system("\nYou stop on the road for a moment.")
        else:
            self.renderer.show_system("\nYou stay in the house a little longer.")
        self.state.running = False

    # ── Natural language fallback ─────────────────────────────────────────────

    def _handle_unknown(self, verb: str, arg: str) -> None:
        """
        Called when the verb is not in the command dispatch table.

        If exactly one NPC is present in the current location, treat the full
        input as a natural-language question directed at that NPC — so the
        player can type "What did Bob want?" or "Who is Nate?" without needing
        the explicit "ask mom" prefix.

        If zero or multiple NPCs are present, fall back to the standard error.
        """
        if self._handle_scene4_action(verb, arg):
            return

        npcs_here = [
            npc_id for npc_id, data in NPCS.items()
            if data["location"] == self.state.current_location
        ]
        if len(npcs_here) == 1:
            full_input = f"{verb} {arg}".strip()
            self._ask_natural(npcs_here[0], full_input)
            return
        self.renderer.show_system(f"I don't understand '{verb}'. Type 'help' for options.")

    def _ask_natural(self, npc_id: str, full_input: str) -> None:
        """Route a free-form input to the appropriate NPC ask handler."""
        if npc_id == "mother":
            before_told = self.state.flags.get("told_mom_plans", False)
            lines, hint = self.dialogue.ask_mom(self.state, full_input)
            dreamleaf_obj = self.objectives.objectives.get("find_dreamleaf", "")
            if (not before_told) and self.state.flags.get("told_mom_plans", False) \
                    and self.state.current_objective != dreamleaf_obj:
                self._set_objective("return_to_dome")
        elif npc_id == "bob":
            lines, hint = self.dialogue.ask_bob(self.state, full_input)
        else:
            lines, hint = self.dialogue.ask_town_npc(npc_id, full_input)
        if lines or hint:
            self.renderer.render(SceneView(
                current_mode="dialogue",
                dialogue_lines=lines or [],
                footer_hint=hint or "",
            ))

    # ── Location events ───────────────────────────────────────────────────────

    def _on_location_entered(self, location_id: str) -> None:
        if location_id == "living_room" and not self.state.flags["met_mother"]:
            self.state.flags["met_mother"] = True
            self.renderer.show_system("\nYour mom is here. She hears you come down.")
            self._set_objective("talk_to_mom")

        elif location_id == "front_door":
            if not self.state.flags["mom_talked"]:
                self.renderer.show_system(
                    "Something pulls you back. You haven't spoken to your mom yet."
                )
            else:
                self.renderer.show_system(
                    "The handle waits under your hand. Leaving is real now."
                )

    def _on_town_node_entered(self, node_id: str) -> None:
        # Track exploration for map fog-of-war
        if node_id not in self.state.discovered_locations:
            self.state.discovered_locations.append(node_id)

        if node_id == "keepers_dome" and not self.state.flags["dome_entered"]:
            self.state.flags["dome_entered"] = True
            self._scene2_hook()
            return

        if (
            node_id == "mystic_trail_overlook"
            and self.state.flags["codex_given"]
            and not self.state.flags["scene3_completed"]
        ):
            self._scene3_overlook_hook()

    def _scene3_overlook_hook(self) -> None:
        # Scene 3 — Lake Ambush at the Mystic Trail Overlook.
        # State mutations happen only AFTER a successful scripted capture.

        self.renderer.show_lines(
            [
                "",
                "The overlook is wrong before you crest it.",
                "Fog sits too heavy on the lake. The trail stones are slick with it.",
                "",
                "Nate is down against the ridge stone, one arm wrapped across his ribs.",
                "His Astari is curled beside him, breathing fast and shallow.",
                "",
                "He sees you. His eyes go wide.",
                "",
                "\"Run,\" he forces out. \"It's still here.\"",
            ]
        )

        run_scene_choice(self.state, "nate_ambush_response", renderer=self.renderer)

        self.renderer.show_lines(
            [
                "",
                "The fog at the waterline peels back.",
                "Something steps out of it — all pressure and wrong angles.",
                "Murkmind.",
            ]
        )

        run_scene_choice(self.state, "murkmind_pressure_response", renderer=self.renderer)

        self.renderer.show_lines(
            [
                "",
                "Murkmind crashes into you like a wave with a mind behind it.",
                "You take the hit, keep your feet, and keep Nate between you and the drop.",
                "When the pressure surges again, you trigger the Switch and force a seal window.",
                "The Cube catches. Barely.",
            ]
        )

        self.renderer.show_lines(
            [
                "",
                "The Cube settles on the stone, still warm from the seal.",
                "The pressure releases from the air all at once.",
                "",
                "Nate hasn't moved. His Astari is still curled beside him.",
                "Pulse there. Breathing. Not awake.",
            ]
        )

        run_scene_choice(self.state, "post_capture_priority", renderer=self.renderer)

        self.renderer.show_lines(
            [
                "",
                "You can't move him all the way back to town like this.",
                "You get your shoulder under his arm and drag him off the open overlook.",
                "",
                "Below the ridge, you find a shallow hollow screened by stone and low branches.",
                "Not safe. Just safer.",
            ]
        )

        self.state.flags["scene3_completed"] = True
        self.state.flags["scene4_started"] = True
        self.state.flags["nate_needs_rest"] = True
        self.state.flags["camp_setup_needed"] = True
        self.state.flags["survival_system_unlocked"] = True
        self.state.flags["camping_unlocked"] = True
        if find_owned(self.state, MURKMIND_SCENE3_INSTANCE_ID) is None:
            self.state.owned_astari.append(build_owned_murkmind())
        if self.state.active_astari_instance_id is None:
            self.state.active_astari_instance_id = MURKMIND_SCENE3_INSTANCE_ID
        self.town.get_node("mystic_trail_overlook")["visible_npcs"] = []
        self.state.current_location = "mystic_trail_safe_hollow"
        if "mystic_trail_safe_hollow" not in self.state.discovered_locations:
            self.state.discovered_locations.append("mystic_trail_safe_hollow")
        self._set_objective("stabilize_nate")
        self._scene4_camp_hook()

    def _scene4_camp_hook(self) -> None:
        self.renderer.show_lines(
            [
                "",
                "You lower Nate onto a bed of branches and old canvas scraps.",
                "His breathing is still uneven. Skin too cold. Pulse too thin.",
                "You're not getting him back to Iso Town tonight.",
                "",
                "Murkmind settles near the stones, angled toward the dark trail.",
                "Watching. Waiting.",
            ]
        )
        if not self.state.flags.get("survival_system_unlocked_intro_shown", False):
            self.state.flags["survival_system_unlocked_intro_shown"] = True

    def _handle_scene4_action(self, verb: str, arg: str) -> bool:
        if not self.state.flags.get("scene4_started") or self.state.flags.get("scene4_completed"):
            return False
        if self.state.current_location != "mystic_trail_safe_hollow":
            return False

        raw = f"{verb} {arg}".strip().lower()
        if raw == "gather water":
            self._scene4_gather_water()
            return True
        if raw == "prepare camp":
            self._scene4_prepare_camp()
            return True
        if raw == "light fire":
            self._scene4_light_fire()
            return True
        if raw in {"rest", "wait"}:
            self._scene4_rest()
            return True
        return False

    def _scene4_gather_water(self) -> None:
        if self.state.flags.get("water_secured"):
            self.renderer.show_system("You've already secured enough water for now.")
            return
        if not self.state.flags.get("murkmind_helped_find_water"):
            self.renderer.show_lines(
                [
                    "Murkmind drifts toward a narrow runoff line and goes still.",
                    "Upstream by the rocks, the water runs clearer.",
                ]
            )
            self.state.flags["murkmind_helped_find_water"] = True
        self.state.flags["water_secured"] = True
        self.state.thirst = max(0, self.state.thirst - 1)
        self.state.fatigue += 1
        self.renderer.show_system("You fill what you can and ration enough clean water for the night.")
        self._scene4_check_progress()

    def _scene4_prepare_camp(self) -> None:
        if self.state.flags.get("camp_secured"):
            self.renderer.show_system("The shelter is already as secure as it's going to get.")
            return
        if not self.state.flags.get("murkmind_helped_choose_camp"):
            self.renderer.show_lines(
                [
                    "Murkmind circles once above the hollow, then settles by a stone lip.",
                    "Less wind. Less line of sight from the ridge.",
                ]
            )
            self.state.flags["murkmind_helped_choose_camp"] = True
        self.state.flags["camp_secured"] = True
        self.state.hunger += 1
        self.state.fatigue += 1
        self.renderer.show_system("You brace branches, clear ground, and build rough cover for Nate.")
        self._scene4_check_progress()

    def _scene4_light_fire(self) -> None:
        if self.state.flags.get("campfire_lit"):
            self.renderer.show_system("The fire is already lit and controlled.")
            return
        self.state.flags["campfire_lit"] = True
        self.renderer.show_system("You coax a small fire to life in the old ring: warmth over stealth.")

    def _scene4_rest(self) -> None:
        if not self.state.flags.get("water_secured") or not self.state.flags.get("camp_secured"):
            self.state.flags["camp_handled_poorly"] = True
            self.renderer.show_system("Not yet. Nate needs water and real shelter first.")
            return
        if not self.state.flags.get("campfire_lit"):
            self.state.flags["camp_kept_dark"] = True
            self.renderer.show_lines(
                [
                    "You keep the hollow dark.",
                    "Murkmind's casing gives off a faint pulse, enough to watch Nate's breathing by.",
                ]
            )
        self.state.flags["camp_handled_carefully"] = True
        self.state.flags["nate_stable_enough_to_talk"] = True
        self.state.flags["camp_setup_needed"] = False
        self.state.fatigue = max(0, self.state.fatigue - 1)
        self.state.hunger += 1
        self.state.thirst += 1
        advance_time(self.state, 90)
        self._set_objective("wait_for_nate")
        self._scene4_trigger_nate_talk()

    def _scene4_check_progress(self) -> None:
        if self.state.flags.get("water_secured") and self.state.flags.get("camp_secured"):
            self.renderer.show_system("Nate is stable for now. Try 'rest' when you're ready to hold the night.")
            return
        missing = []
        if not self.state.flags.get("water_secured"):
            missing.append("water")
        if not self.state.flags.get("camp_secured"):
            missing.append("shelter")
        self.renderer.show_system(f"Still needed: {', '.join(missing)}.")

    def _scene4_trigger_nate_talk(self) -> None:
        if self.state.flags.get("nate_recovery_talk_complete"):
            return

        self.renderer.show_lines(
            [
                "",
                "Near dawn, Nate's breathing evens out.",
                "He opens one eye, then both, tracking the hollow before he focuses on you.",
                "",
                "\"...You stayed,\" he says.",
                "\"You were supposed to drag me out, not set up a whole camp.\"",
                "",
                "Murkmind shifts in the edge of your vision.",
                "Nate tenses, then exhales when it doesn't move on him.",
                "\"That thing's with you now?\"",
                "\"Keep it close. Respectful. It'll return the favor.\"",
            ]
        )

        if "Nate's Codex Parcel" in self.state.inventory:
            self.state.inventory.remove("Nate's Codex Parcel")
            self.state.flags["parcel_delivered_to_nate"] = True
            self.state.flags["codex_delivered"] = True
            self.state.flags["mom_blessing_available"] = True
            self.renderer.show_lines(
                [
                    "",
                    "You hand him the parcel from Bob.",
                    "Nate stares at it, then laughs once through his teeth.",
                    "\"My Codex. I thought Bob gave up on me.\"",
                    "He runs a thumb across the seal and goes quiet.",
                ]
            )

        self.renderer.show_lines(
            [
                "",
                "\"Saw Audri at the Dome?\" Nate asks without looking up.",
                "\"Don't answer. I can already see it on your face.\"",
            ]
        )
        audri_choice = run_scene_choice(self.state, "audri_interest_response", renderer=self.renderer)
        if audri_choice == "deflect":
            self.state.flags["audri_interest_deflected"] = True
        elif audri_choice == "stay_quiet":
            self.state.flags["audri_interest_silence"] = True
        elif audri_choice == "admit_it":
            self.state.flags["audri_interest_admitted"] = True

        self.renderer.show_lines(
            [
                "",
                "\"You remember that old day by the lake?\" Nate says.",
                "\"Before all this. You skipped stones, she sketched the waterline, and I lied about not being cold.\"",
                "He gives a tired grin that doesn't last.",
                "\"Point is — she doesn't care about big talk. She notices what you carry back.\"",
                "",
                "\"Jenn still runs that kickback table by the market's back awning,\" he adds.",
                "\"Dreamleaf moves fast there. Bring some in and she'll pay clean if it isn't bruised.\"",
                "",
                "\"But hear me: the Forbidden Trail warning signs are old, not wrong.\"",
                "\"Fog out there doesn't just hide things. It leans on your head. Makes good plans sloppy.\"",
                "Murkmind gives a low, almost disapproving thrum at the word forbidden.",
            ]
        )
        self.state.flags["audri_lake_lore_heard"] = True
        self.state.flags["dreamleaf_hint_received"] = True
        self.state.flags["jenn_kickback_seeded"] = True

        motivation_choice = run_scene_choice(self.state, "dreamleaf_motivation", renderer=self.renderer)
        if motivation_choice == "for_audri":
            self.state.flags["dreamleaf_goal_romanticized"] = True
        elif motivation_choice == "prove_something":
            self.state.flags["dreamleaf_goal_self_worth"] = True
        elif motivation_choice == "murkmind_training":
            self.state.flags["dreamleaf_goal_training"] = True

        self.renderer.show_lines(
            [
                "",
                "Nate leans back against the stone, exhausted.",
                "\"I'm not dead. That's your win for tonight.\"",
                "\"Now go get your miracle leaf and try not to become a story people tell wrong.\"",
            ]
        )

        self.state.flags["nate_needs_rest"] = False
        self.state.flags["nate_recovery_talk_complete"] = True
        self.state.flags["scene4_completed"] = True
        self._set_objective("find_dreamleaf")

    def _handle_fog_boundary_attempt(self) -> None:
        self.state.flags["saw_fog_boundary"] = True
        pursuing_dreamleaf = (
            self.state.flags.get("scene4_completed")
            or self.state.flags.get("dreamleaf_hint_received")
        )
        if pursuing_dreamleaf:
            self.renderer.show_system(
                "The fog wall holds. Dreamleaf is somewhere beyond it, "
                "but whatever waits past the boundary won't open for you yet."
            )
            return
        self.renderer.show_system(
            "The fog curls at the boundary like it's waiting for something. "
            "You have a partner now, but not a reason yet. Not the kind this place respects."
        )

    # ── House → Town transition ───────────────────────────────────────────────

    def _transition_to_town(self) -> None:
        """Player steps out of GP's House into town."""
        advance_time(self.state, 10)
        self.renderer.show_lines([
            "\n" + "─" * 40,
            f"You open the door, {self.state.player_name}.",
            "The street is quieter than you expected.",
            "The air is different out here — cooler, more honest.",
            "You don't look back at the house.",
            "─" * 40,
        ])

        self.state.flags["in_town"] = True
        self.state.current_location = "front_street"
        # Seed discovery with starting location
        if "front_street" not in self.state.discovered_locations:
            self.state.discovered_locations.append("front_street")

        # find_bob was already set during the Mom conversation —
        # do NOT override it with find_nate here.
        self.renderer.show_system(f"\n→ {self.state.current_objective}")

    # ── Scene 2 hook ─────────────────────────────────────────────────────────

    def _scene2_hook(self) -> None:
        """Scene 2 intro event when player first arrives at The Keeper's Dome."""
        self.renderer.render(SceneView(
            current_mode="dialogue",
            dialogue_lines=[
                "The Keeper's Dome sits low and round, set back from the street like it was built to listen more than be seen.",
                "The door is half-open. Voices carry through the gap — low, controlled.",
                "The kind of conversation that doesn't need to be loud to have weight.",
                "You step closer.",
                '"Come on in." Keeper Bob\'s voice, from inside. "I\'ve been holding something too long."',
            ],
        ))
        self._set_objective("enter_dome", added=True)
