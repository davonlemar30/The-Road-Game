"""Main game engine and command loop."""

from data.npcs import NPCS
from game.dialogue import DialogueManager
from game.display import print_dialogue, print_hint
from game.map_renderer import render_map
from game.objectives import ObjectiveTracker
from game.parser import parse_command
from game.persistence import load_game, save_game
from game.state import GameState
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
        self._show_intro()

        loaded = self._offer_load()
        if not loaded:
            self._prompt_player_name()
            print(self.objectives.set_objective(self.state, "look_around"))
            print("\nType 'look' to take in your surroundings.")

        while self.state.running:
            raw = input("\n> ")
            verb, arg = parse_command(raw)
            self._handle_command(verb, arg)

    # ── Startup ──────────────────────────────────────────────────────────────

    def _show_intro(self) -> None:
        print("=" * 40)
        print("          THE ROAD")
        print("   Prologue: STILL HERE")
        print("=" * 40)
        print(
            "\nYou wake where you've always been: "
            "waiting for movement to become a decision."
        )

    def _offer_load(self) -> bool:
        """Ask if player wants to load. Returns True if a save was loaded."""
        import os
        from game.persistence import SAVE_FILE

        if not os.path.exists(SAVE_FILE):
            return False

        answer = input("\nA save file exists. Load it? (y/n): ").strip().lower()
        if answer in {"y", "yes"}:
            ok, result = load_game()
            if ok:
                self.state = result
                print(f"\nWelcome back, {self.state.player_name}.")
                print(f"Current objective: {self.state.current_objective}")
                print("\nType 'look' to get your bearings.")
                return True
            else:
                print(f"Could not load save: {result}")
        return False

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
                print("Type a command. Try: look, go south, inspect mirror, talk mom, help.")
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
            "quit":      self._cmd_quit,
        }

        handler = handlers.get(verb)
        if handler is None:
            print(f"I don't understand '{verb}'. Type 'help' for options.")
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
            print("Go where? Example: go south")
            return

        if self.state.current_location == "front_door" and direction == "out":
            if not self.state.flags["mom_talked"]:
                print(
                    "Something holds you at the threshold. "
                    "You haven't talked to your mom yet — not really."
                )
                print("(Talk to her. Tell her where you're going.)")
                return
            self._transition_to_town()
            return

        success, result = self.world.move(self.state.current_location, direction)
        if not success:
            print(result)
            return

        self.state.current_location = result
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

            # Scene 2 setup: Bob gives Nate's Codex after the intro event
            if not self.state.flags["codex_given"]:
                self.state.flags["codex_given"] = True
                if "Nate's Codex Parcel" not in self.state.inventory:
                    self.state.inventory.append("Nate's Codex Parcel")
                print("\nThe door opens the rest of the way and Bob waves you in.")
                print("Audri is already by the equipment table, speaking quietly with him.")
                print("She glances at you once — measuring, unreadable — then returns to the route map.")
                print()
                print('Bob rubs his forehead. "Good timing. I need a favor."')
                print('He presses a wrapped parcel into your hands. "Nate\'s Codex. Get it to him at Mystic Trail."')
                print('He pats a second Codex on the shelf. "That one can wait until you\'re really ready."')
                print(self.objectives.set_objective(self.state, "deliver_codex"))
                print("\n(Type 'go mystic trail' to look for Nate.)")
                return

            # Post-delivery: Bob sends GP home for Scene 4 conversation
            if self.state.flags["codex_delivered"] and not self.state.flags["mom_blessing_available"]:
                self.state.flags["mom_blessing_available"] = True
                print("\nBob checks your face before he checks your hands.")
                print('"Good. You found Nate." He nods toward the town. "Now go talk to your mom."')
                print('"No half-steps. Come back after that conversation and we\'ll continue."')
                print(self.objectives.set_objective(self.state, "mom_blessing"))
                return

            # Scene 4+ follow-up
            print("\nThe door is open. You step inside.")
            print("─" * 40)
            print("Professor Bob is at his workbench, back to you.")
            if self.state.flags["told_mom_plans"]:
                print("An Astari — small, watchful — sits on a perch near the window.")
                print("Bob doesn't look up immediately.")
                print('  "Pick the one that picks you. That\'s always been my advice."')
                print('  "The other one already knows you\'re here."')
                print("(Starter selection is still in progress.)")
            else:
                print('Bob says, "When you\'ve had that talk at home, come back."')
            print("─" * 40)
            return

        if loc == "the_market":
            print("You drift along the stalls. Try 'browse' to check what vendors have.")
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
                print_dialogue(lines)
                print_hint(hint)
                print(self.objectives.set_objective(self.state, "find_bob", added=True))
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
            print(f"You only have {self.state.money} tokens. {name} costs {cost}.")
            return
        self.state.money -= cost
        self.state.inventory.append(name)
        print(f"You buy {name} for {cost} tokens. ({self.state.money} tokens left.)")

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
            print(f"You're carrying nothing. Tokens: {self.state.money}")
        else:
            print(f"You have ({self.state.money} tokens):")
            for item in self.state.inventory:
                print(f"  - {item}")

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
            print("  go [place]               — travel to a nearby location by name")
            print("                             (e.g. go square  /  go keeper's dome)")
        else:
            print("  go [direction]           — north / south / east / west / out")
        print("  inspect [object]         — examine something here")
        print("  talk [npc]               — start a conversation  (e.g. talk mom)")
        print("  ask [npc] [topic]        — ask something specific (e.g. ask mom nate)")
        print("  browse [shop]            — view nearby stalls/shop stock")
        print("  buy [item]               — purchase a simple item if available")
        print("  ask about [topic]        — shorthand when only one NPC is present")
        print("  tell me about [topic]    — natural phrasing, same as ask about")
        print("  tell mom [your plan]     — e.g. 'tell mom i'm going' to commit to leaving")
        print("  inventory (or inv)       — show what you're carrying")
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

    def _cmd_quit(self, _arg: str) -> None:
        if self.state.flags["in_town"]:
            print("\nYou stop on the road for a moment.")
        else:
            print("\nYou stay in the house a little longer.")
        self.state.running = False

    # ── Location events ───────────────────────────────────────────────────────

    def _on_location_entered(self, location_id: str) -> None:
        if location_id == "living_room" and not self.state.flags["met_mother"]:
            self.state.flags["met_mother"] = True
            print("\nYour mom is here, in her chair. She hears you come down.")
            print(self.objectives.set_objective(self.state, "talk_to_mom"))

        elif location_id == "front_door" and self.state.flags["told_mom_plans"]:
            print("The door is unlocked. Type 'go out' when you're ready.")
        elif location_id == "front_door" and not self.state.flags["mom_talked"]:
            print("You stand at the door. Something tells you to talk to your mom first.")

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

        if self.state.flags["has_old_phone"]:
            print("\n(The phone is off. Type 'use phone' to turn it on.)")
        if not self.state.flags["codex_given"]:
            print(self.objectives.set_objective(self.state, "find_bob", added=True))
        else:
            print(self.objectives.set_objective(self.state, "find_nate", added=True))
        print("\nType 'look' to take in Front Street.")

    # ── Scene 2 hook ─────────────────────────────────────────────────────────

    def _scene2_hook(self) -> None:
        """Scene 2 intro event when player first arrives at The Keeper's Dome."""
        print("\n" + "─" * 40)
        print("The Dome is low and round, set back from everything else.")
        print("The door is barely open. Voices carry from inside — Bob's, and someone unfamiliar.")
        print()
        print("You catch a glimpse of Audri by the equipment table before she disappears deeper in.")
        print('Bob calls out, "Come in. I\'ve got something for Nate."')
        print("─" * 40)
        print(self.objectives.set_objective(self.state, "deliver_codex", added=True))
        print("\n(Type 'look' to take in the Dome. Type 'enter' or 'open door' to step inside.)")
