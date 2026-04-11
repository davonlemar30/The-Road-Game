"""Main game engine and command loop."""

from __future__ import annotations

from data.dialogue_data import MOTHER_SCENE1_PART1, MOTHER_SCENE1_PART2
from data.npcs import NPCS
from game.choices import run_scene_choice
from game.dialogue import DialogueManager
from game.choices import run_scene_choice
from game.display import (
    menu_choice,
    print_dialogue,
    print_hint,
    print_hud,
    print_status_screen,
    print_title_screen,
)
from game.map_renderer import render_map
from game.objectives import ObjectiveTracker
from game.parser import parse_command
from game.persistence import load_game, save_game
from game.state import GameState
from game.timekeeper import advance_time, format_time_label
from game.town import TownWorld
from game.world import World


class GameEngine:
    def __init__(self) -> None:
        self.state = GameState()
        self.world = World()
        self.town = TownWorld()
        self.objectives = ObjectiveTracker()
        self.dialogue = DialogueManager()

    def run(self) -> None:
        loaded = self._show_main_menu()
        if not loaded:
            self._show_intro()
            self._prompt_player_name()
            print(self.objectives.set_objective(self.state, "look_around"))
            print("\nType 'look' to take in your room.")

        while self.state.running:
            self._render_hud()
            raw = input("\n> ")
            verb, arg = parse_command(raw)
            self._handle_command(verb, arg)

    # ── Startup ──────────────────────────────────────────────────────────────

    def _show_intro(self) -> None:
        print(
            "\nYou wake where you've always been: "
            "waiting for movement to become a decision."
        )

    def _render_hud(self) -> None:
        location_name = self._current_location_name()
        print_hud(self.state, location_name)

    def _current_location_name(self) -> str:
        if self.state.flags["in_town"]:
            return self.town.get_node(self.state.current_location)["name"]
        return self.world.get_location(self.state.current_location)["name"]

    def _prompt_player_name(self) -> None:
        while not self.state.player_name:
            name = input("\nWhat is your name? ").strip()
            if name:
                self.state.player_name = name
            else:
                print("Please enter a name.")
        print(f"\nMorning, {self.state.player_name}.")

    # ── Command dispatch ─────────────────────────────────────────────────────

    def _handle_command(self, verb: str, arg: str) -> None:
        if not verb:
            if self.state.flags["in_town"]:
                print("Type a command. Try: look, go square, where, inspect door, talk bob, help.")
            else:
                print("Type a command. Try: look, go downstairs, inspect mirror, talk mom, help.")
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
            "save":      self._cmd_save,
            "load":      self._cmd_load,
            "help":      self._cmd_help,
            "objective": self._cmd_objective,
            "status":    self._cmd_status,
            "quit":      self._cmd_quit,
        }

        handler = handlers.get(verb)
        if handler is None:
            self._handle_unknown(verb, arg)
            return

        handler(arg)

    # ── Handlers ─────────────────────────────────────────────────────────────

    def _cmd_look(self, _arg: str) -> None:
        if self.state.flags["in_town"]:
            print(self.town.describe(self.state.current_location))
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
            print(desc)

    def _cmd_go(self, arg: str) -> None:
        if self.state.flags["in_town"]:
            self._cmd_go_town(arg)
        else:
            self._cmd_go_house(arg)

    def _cmd_go_house(self, arg: str) -> None:
        direction = arg.strip().lower()
        if not direction:
            print("Go where? Try: go downstairs  /  go kitchen  /  go front door  /  go out")
            return

        # Any exit that leads to "outside" in the front_door exits dict means
        # the player wants to leave the house — route to _transition_to_town.
        if self.state.current_location == "front_door":
            exits = self.world.get_location("front_door")["exits"]
            if exits.get(direction) == "outside":
                if not self.state.flags["mom_talked"]:
                    print(
                        "Something holds you at the threshold. "
                        "You haven't talked to your mom yet — not really."
                    )
                    print("Type 'talk mom' first.")
                    return
                self._transition_to_town()
                return

        success, result = self.world.move(self.state.current_location, direction)
        if not success:
            print(result)
            return

        self.state.current_location = result
        advance_time(self.state, 5)
        location_name = self.world.get_location(result)["name"]
        print(f"\nYou head to the {location_name}.")
        print("(Type 'look' to take in the room.)")
        self._on_location_entered(result)

    def _cmd_go_town(self, arg: str) -> None:
        target = arg.strip()
        if not target:
            print("Go where? Example: go square  /  go keeper's dome  /  go market")
            return

        # "go inside" / "go in" → treat as enter command at current location
        if target.lower() in {"inside", "in", "through", "through the door"}:
            self._cmd_enter("")
            return

        success, result = self.town.move_to(self.state.current_location, target)
        if not success:
            print(result)
            return

        self.state.current_location = result
        advance_time(self.state, 15)
        node_name = self.town.get_node(result)["name"]
        print(f"\nYou make your way to {node_name}.")
        print("(Type 'look' to take in your surroundings.)")
        self._on_town_node_entered(result)

    def _cmd_inspect(self, arg: str) -> None:
        if not arg:
            print("Inspect what? (example: inspect mirror)")
            return
        if self.state.flags["in_town"]:
            print(self.town.inspect(self.state.current_location, arg))
        else:
            print(self.world.inspect(self.state.current_location, arg))

    def _cmd_enter(self, arg: str) -> None:
        """Handle 'enter', 'open door', 'knock', 'go inside' in town."""
        if not self.state.flags["in_town"]:
            print("There's nothing to enter here.")
            return

        loc = self.state.current_location

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

                # ── Audri departure beat ──────────────────────────────────────
                # The room smells like ozone and old wood. Keeper Bob is at the
                # main worktable. A young woman stands near the far side.
                print_dialogue([
                    "The space inside the Dome smells like ozone, dried herbs, and old wood.",
                    "Keeper Bob is at the worktable, hands busy. He doesn't look up yet.",
                    "A young woman stands near the far side of the table.",
                    "She doesn't fill the room with noise. But the room feels different with her in it.",
                    'Bob\'s voice, steady: "All five Crests. You\'ve done this town proud."',
                    "The young woman nods once.",
                    '"I\'m staying in Iso Town for a bit," she says. "Rest. Prep. Then I\'m back on the road."',
                    'Bob: "The road doesn\'t wait."',
                    '"Neither do I."',
                ])
                print_dialogue([
                    "She turns to leave.",
                    "As she passes the threshold, she pauses.",
                    "Her eyes find yours — warm, curious. Just for a second.",
                    "Then she's gone, the door easing shut behind her.",
                    "The Dome feels too quiet. Like the air is deciding what to do now that she isn't in it.",
                ])

                # ── Keeper Bob + Codex ────────────────────────────────────────
                print_dialogue([
                    f'Keeper Bob finally turns to you. "Good timing," he says.',
                    '"I need a favor."',
                    "He reaches into the tray labeled PENDING and pulls out a small parcel.",
                    '"This keeps ending up right back where it started," he mutters.',
                    '"I\'ve been trying to get it to Nate for over a week."',
                    "He taps the tag with one finger.",
                    '"His Codex."',
                    "He watches your face, like he's waiting for you to object.",
                    '"You know that spot you two used to hang at? The overlook above the lake, on Mystic Trail?"',
                    '"Nate went out there last night and hasn\'t come back."',
                    "He holds the parcel out.",
                    '"Take it to him."',
                ])
                print_dialogue([
                    '"Be careful with it. Useful, but delicate."',
                    "His voice softens slightly. Not sentiment — patience.",
                    '"And... yeah. I\'ve got a second Codex back here."',
                    '"Just saying."',
                    "He doesn't push you toward it. He just lets that truth sit in the room.",
                    '"Mystic Trail is usually fine, but lately the path\'s been feeling off."',
                    '"So be careful."',
                ])
                run_scene_choice(self.state, "bob_codex_response")
                print(self.objectives.set_objective(self.state, "deliver_codex", added=True))
                print("\nType 'go mystic trail' to head out.")
                return

            # Post-delivery: Keeper Bob sends GP home for Scene 4 conversation
            if self.state.flags["codex_delivered"] and not self.state.flags["mom_blessing_available"]:
                self.state.flags["mom_blessing_available"] = True
                print_dialogue([
                    "Keeper Bob checks your face before he checks your hands.",
                    '"You found him."',
                    "Not a question.",
                    '"Good. Now go talk to your mom. Not tonight — now."',
                    '"Tell her where you\'re going and mean it."',
                    '"She already suspects. Don\'t let her sit with that."',
                    '"Come back after and we finish this."',
                ])
                print(self.objectives.set_objective(self.state, "mom_blessing"))
                return

            # Scene 4+ follow-up
            if self.state.flags["told_mom_plans"]:
                print_dialogue([
                    "Keeper Bob is at his workbench, back to you.",
                    "An Astari — small, watchful — sits on a perch near the window.",
                    "It turns its head before Bob does.",
                    '"Pick the one that picks you. That\'s always been my advice."',
                    '"The other one already knows you\'re here."',
                ])
                print("(Astari selection coming in the next build.)")
            else:
                print_dialogue([
                    "Keeper Bob looks up when you come in.",
                    '"When you\'ve had that talk at home, come back. Not before."',
                ])
            return

        # Generic response for other locations
        print("There's no door to enter here.")

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
            print("Talk to who? (example: talk mom)")
            return

        npc_id = self._resolve_npc_here(target)
        if npc_id is None:
            print(f"There's no one called '{target}' here.")
            return

        if npc_id == "mother":
            was_talked = self.state.flags["mom_talked"]
            lines, hint = self.dialogue.talk_to_mother(self.state)

            if not was_talked and self.state.flags["mom_talked"]:
                # ── First encounter: full split-scene flow ────────────────────
                # Part 1: greeting + "You sleep okay?"
                print_dialogue(MOTHER_SCENE1_PART1)
                # Player responds to the question — first interactive beat.
                run_scene_choice(self.state, "mom_sleep_response")
                # Part 2: Bob's visit, Nate news, Astari push.
                print_dialogue(MOTHER_SCENE1_PART2)
                # Nate stance and readiness stance choices.
                run_scene_choice(self.state, "mom_nate_response")
                run_scene_choice(self.state, "mom_readiness_response")
                print_hint("She's here if there's more on your mind.")
                print(self.objectives.set_objective(self.state, "find_bob", added=True))
                return

            # ── Subsequent visits ─────────────────────────────────────────────
            if lines:
                print_dialogue(lines)
            print_hint(hint)
            return

        elif npc_id == "bob":
            lines, hint = self.dialogue.talk_to_bob(self.state)
        else:
            lines, hint = self.dialogue.talk_to_town_npc(npc_id)

        print_dialogue(lines)
        print_hint(hint)

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
                    lines, hint = self.dialogue.ask_mom(self.state, topic)
                elif target == "bob":
                    lines, hint = self.dialogue.ask_bob(self.state, topic)
                else:
                    lines, hint = self.dialogue.ask_town_npc(target, topic)
                if lines:
                    print_dialogue(lines)
                print_hint(hint)
                return
            print("Ask who about that? (example: ask mom about bob)")
            return

        parts = arg.strip().split(maxsplit=1)
        if not parts:
            print("Ask who? (example: ask mom nate)")
            return

        target = parts[0].lower()
        topic = parts[1] if len(parts) > 1 else ""

        npc_id = self._resolve_npc_here(target)
        if npc_id is None:
            print(f"You don't see '{target}' to ask.")
            return

        if npc_id == "mother":
            lines, hint = self.dialogue.ask_mom(self.state, topic)
        elif npc_id == "bob":
            lines, hint = self.dialogue.ask_bob(self.state, topic)
        else:
            lines, hint = self.dialogue.ask_town_npc(npc_id, topic)
        if lines:
            print_dialogue(lines)
        print_hint(hint)

    def _cmd_browse(self, arg: str) -> None:
        if not self.state.flags["in_town"]:
            print("There's nothing to browse in here.")
            return
        ok, text = self.town.browse(self.state.current_location, arg.strip())
        print(text)

    def _cmd_buy(self, arg: str) -> None:
        item = arg.strip().lower()
        if self.state.current_location != "the_market":
            print("No one is selling that here.")
            return
        if not item:
            print("Buy what? (example: buy water flask)")
            return
        catalog = {
            "dried fruit pack": ("Dried Fruit Pack", 4),
            "fruit": ("Dried Fruit Pack", 4),
            "water flask": ("Clean Water Flask", 3),
            "flask": ("Clean Water Flask", 3),
        }
        if item not in catalog:
            print("That isn't on display. Try 'browse'.")
            return
        name, cost = catalog[item]
        if self.state.money < cost:
            print(f"You only have {self.state.money} gold. {name} costs {cost} gold.")
            return
        self.state.money -= cost
        self.state.inventory.append(name)
        print(f"You buy {name} for {cost} gold. ({self.state.money} gold left.)")

    def _cmd_where(self, _arg: str) -> None:
        if not self.state.flags["in_town"]:
            loc = self.world.get_location(self.state.current_location)
            exits = ", ".join(loc["exits"].keys())
            print(f"\nYou're in the {loc['name']}. Exits: {exits}")
            return

        node = self.town.get_node(self.state.current_location)
        nearby = self.town.neighbors_text(self.state.current_location)
        print(f"\nYou're at {node['name']}.")
        print(f"Nearby: {nearby}")

    def _cmd_map(self, _arg: str) -> None:
        if not self.state.flags["in_town"]:
            print("You're inside. Step outside first.")
            return
        if not self.state.flags["has_old_phone"]:
            print("You don't have anything to check a map on.")
            return
        if not self.state.flags["phone_unlocked"]:
            print("The phone is off. Type 'use phone' to turn it on.")
            return
        discovered = set(self.state.discovered_locations)
        print(render_map(self.state.current_location, discovered))

    def _cmd_use(self, arg: str) -> None:
        item = arg.strip().lower()
        if not item:
            print("Use what?")
            return

        if item in {"phone", "old phone", "mom's phone"}:
            self._use_phone()
            return

        print(f"You're not sure how to use '{item}'.")

    def _use_phone(self) -> None:
        if not self.state.flags["has_old_phone"]:
            print("You don't have a phone.")
            return

        if self.state.flags["phone_unlocked"]:
            print(
                "The phone's on. You have: map, field notes (locked), contacts (locked).\n"
                "Type 'map' to see ISO Town."
            )
            return

        # First unlock
        self.state.flags["phone_unlocked"] = True
        print(
            "\nThe phone powers on with a low hum. The screen is scratched but clear."
        )
        print(
            "There's a map of ISO Town, field notes locked behind a passphrase, "
            "and a contacts list that hasn't been updated in a while."
        )
        print("\nType 'map' to see where you are.")

    def _cmd_inventory(self, _arg: str) -> None:
        if not self.state.inventory:
            print(f"You're carrying nothing. Gold: {self.state.money}")
        else:
            print(f"You have ({self.state.money} gold):")
            for item in self.state.inventory:
                print(f"  - {item}")

    def _cmd_status(self, _arg: str) -> None:
        print_status_screen(self.state, self._current_location_name())

    def _cmd_save(self, _arg: str) -> None:
        if not self.state.player_name:
            print("Nothing to save yet.")
            return
        print(save_game(self.state))

    def _cmd_load(self, _arg: str) -> None:
        ok, result = load_game()
        if ok:
            self.state = result
            print(f"Save loaded. Welcome back, {self.state.player_name}.")
            print(f"Current objective: {self.state.current_objective}")
        else:
            print(result)

    def _cmd_help(self, _arg: str) -> None:
        print("\nCommands:")
        print("  look (or l)              — describe where you are")
        print("  where                    — quick location + nearby places")
        if self.state.flags["in_town"]:
            print("  go [place]               — travel by name (e.g. go square  /  go keeper's dome)")
        else:
            print("  go [room or direction]   — e.g. go downstairs  /  go kitchen  /  go out")
        print("  inspect [object]         — examine something here")
        print("  talk [npc]               — start a conversation  (e.g. talk mom)")
        print("  ask [npc] [topic]        — ask something specific (e.g. ask mom nate)")
        print("  browse [shop]            — view nearby stalls/shop stock")
        print("  buy [item]               — purchase a simple item if available")
        print("  ask about [topic]        — shorthand when only one NPC is present")
        print("  tell me about [topic]    — natural phrasing, same as ask about")
        print("  tell mom [your plan]     — e.g. 'tell mom i'm going' to commit to leaving")
        print("  inventory (or inv)       — show what you're carrying")
        print("  status                   — open player status hub")
        if self.state.flags["has_old_phone"]:
            print("  use phone                — open the old phone")
        if self.state.flags["phone_unlocked"]:
            print("  map                      — show ISO Town map")
        print("  objective                — show current objective")
        print("  save / load              — save or restore your progress")
        print("  help                     — show this list")
        print("  quit                     — exit the game")

    def _cmd_objective(self, _arg: str) -> None:
        if self.state.current_objective:
            print(f"Current objective: {self.state.current_objective}")
        else:
            print("No objective set.")
        print(f"Current time: {format_time_label(self.state)}")

    def _cmd_quit(self, _arg: str) -> None:
        if self.state.flags["in_town"]:
            print("\nYou stop on the road for a moment.")
        else:
            print("\nYou stay in the house a little longer.")
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
        npcs_here = [
            npc_id for npc_id, data in NPCS.items()
            if data["location"] == self.state.current_location
        ]
        if len(npcs_here) == 1:
            full_input = f"{verb} {arg}".strip()
            self._ask_natural(npcs_here[0], full_input)
            return
        print(f"I don't understand '{verb}'. Type 'help' for options.")

    def _ask_natural(self, npc_id: str, full_input: str) -> None:
        """Route a free-form input to the appropriate NPC ask handler."""
        if npc_id == "mother":
            lines, hint = self.dialogue.ask_mom(self.state, full_input)
        elif npc_id == "bob":
            lines, hint = self.dialogue.ask_bob(self.state, full_input)
        else:
            lines, hint = self.dialogue.ask_town_npc(npc_id, full_input)
        if lines:
            print_dialogue(lines)
        print_hint(hint)

    # ── Location events ───────────────────────────────────────────────────────

    def _on_location_entered(self, location_id: str) -> None:
        if location_id == "living_room" and not self.state.flags["met_mother"]:
            self.state.flags["met_mother"] = True
            print("\nYour mom is here, in her chair. She hears you come down.")
            print(self.objectives.set_objective(self.state, "talk_to_mom"))

        elif location_id == "front_door":
            if not self.state.flags["mom_talked"]:
                print("Something pulls you back. You haven't spoken to your mom yet.")
                print("Type 'go upstairs' to find her, or 'talk mom' if she's nearby.")
            else:
                print("The door is right there. Type 'go out' when you're ready.")

    def _on_town_node_entered(self, node_id: str) -> None:
        # Track exploration for map fog-of-war
        if node_id not in self.state.discovered_locations:
            self.state.discovered_locations.append(node_id)

        if node_id == "keepers_dome" and not self.state.flags["dome_entered"]:
            self.state.flags["dome_entered"] = True
            self._scene2_hook()
            return

        if (
            node_id == "mystic_trail"
            and self.state.flags["codex_given"]
            and not self.state.flags["codex_delivered"]
        ):
            self.state.flags["codex_delivered"] = True
            if "Nate's Codex Parcel" in self.state.inventory:
                self.state.inventory.remove("Nate's Codex Parcel")
            print("\nNate is exactly where he always is — perched at the overlook.")
            print('You hand over the parcel. He exhales. "So he finally sent it."')
            print('He nods back toward town. "Go see Bob. It\'s overdue."')
            print(self.objectives.set_objective(self.state, "return_to_dome"))

    # ── House → Town transition ───────────────────────────────────────────────

    def _transition_to_town(self) -> None:
        """Player steps out of GP's House into town."""
        advance_time(self.state, 10)
        print("\n" + "─" * 40)
        print(f"You open the door, {self.state.player_name}.")
        print("The street is quieter than you expected.")
        print("The air is different out here — cooler, more honest.")
        print("You don't look back at the house.")
        print("─" * 40)

        self.state.flags["in_town"] = True
        self.state.current_location = "front_street"
        # Seed discovery with starting location
        if "front_street" not in self.state.discovered_locations:
            self.state.discovered_locations.append("front_street")

        # find_bob was already set during the Mom conversation —
        # do NOT override it with find_nate here.
        # Remind the player of their current objective.
        print(f"\nObjective: {self.state.current_objective}")
        print("\nType 'look' to take in Front Street.")

    # ── Scene 2 hook ─────────────────────────────────────────────────────────

    def _scene2_hook(self) -> None:
        """Scene 2 intro event when player first arrives at The Keeper's Dome."""
        print_dialogue([
            "The Keeper's Dome sits low and round, set back from the street like it was built to listen more than be seen.",
            "The door is half-open. Voices carry through the gap — low, controlled.",
            "The kind of conversation that doesn't need to be loud to have weight.",
            "You step closer.",
            '"Come on in." Keeper Bob\'s voice, from inside. "I\'ve got something that can\'t wait."',
        ])
        print(self.objectives.set_objective(self.state, "enter_dome", added=True))
        print("\nType 'enter' to step inside.")
