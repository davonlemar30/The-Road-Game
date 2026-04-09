"""Main game engine and command loop."""

from data.npcs import NPCS
from game.dialogue import DialogueManager
from game.display import print_dialogue, print_hint
from game.objectives import ObjectiveTracker
from game.parser import parse_command
from game.persistence import load_game, save_game
from game.state import GameState
from game.world import World


class GameEngine:
    def __init__(self) -> None:
        self.state = GameState()
        self.world = World()
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
            print("Type a command. Try: look, go south, inspect mirror, talk mom, help.")
            return

        handlers = {
            "look":      self._cmd_look,
            "go":        self._cmd_go,
            "inspect":   self._cmd_inspect,
            "talk":      self._cmd_talk,
            "ask":       self._cmd_ask,
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
        print(self.world.describe_location(self.state.current_location))

    def _cmd_go(self, arg: str) -> None:
        direction = arg.strip().lower()
        if not direction:
            print("Go where? Example: go south")
            return

        if self.state.current_location == "front_door" and direction == "out":
            if not self.state.flags["permission_granted"]:
                print(
                    "Something holds you at the threshold. "
                    "You don't feel ready to go — not yet."
                )
                return
            self._end_game()
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

    def _cmd_inspect(self, arg: str) -> None:
        if not arg:
            print("Inspect what? (example: inspect mirror)")
            return
        print(self.world.inspect(self.state.current_location, arg))

    def _cmd_talk(self, arg: str) -> None:
        target = arg.strip().lower()
        if not target:
            print("Talk to who? (example: talk mom)")
            return

        mother_data = NPCS["mother"]
        if target not in mother_data["aliases"]:
            print(f"There's no one called '{target}' here.")
            return

        if self.state.current_location != mother_data["location"]:
            print("Your mom isn't here.")
            return

        was_talked = self.state.flags["mom_talked"]
        lines, hint = self.dialogue.talk_to_mother(self.state)
        print_dialogue(lines)
        print_hint(hint)

        # Set objective only on the first completed conversation
        if not was_talked and self.state.flags["mom_talked"]:
            print(self.objectives.set_objective(self.state, "find_nate", added=True))

    def _cmd_ask(self, arg: str) -> None:
        parts = arg.strip().split(maxsplit=1)
        if not parts:
            print("Ask who? (example: ask mom nate)")
            return

        target = parts[0].lower()
        topic = parts[1] if len(parts) > 1 else ""

        mother_data = NPCS["mother"]
        if target not in mother_data["aliases"]:
            print(f"You don't see '{target}' to ask.")
            return

        if self.state.current_location != mother_data["location"]:
            print("Your mom isn't here.")
            return

        lines, hint = self.dialogue.ask_mom(self.state, topic)
        if lines:
            print_dialogue(lines)
        print_hint(hint)

    def _cmd_inventory(self, _arg: str) -> None:
        if not self.state.inventory:
            print("You're not carrying anything.")
        else:
            print("You have:")
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
        print("  look (or l)              — describe the room and exits")
        print("  go [direction]           — north / south / east / west / out")
        print("  inspect [object]         — examine something in the room")
        print("  talk [npc]               — start a conversation  (e.g. talk mom)")
        print("  ask [npc] [topic]        — ask something specific (e.g. ask mom nate)")
        print("  ask about [topic]        — shorthand when only one NPC is present")
        print("  tell me about [topic]    — natural phrasing, same as ask about")
        print("  inventory (or inv)       — show what you're carrying")
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
        print("\nYou stay in the house a little longer.")
        self.state.running = False

    # ── Location events ───────────────────────────────────────────────────────

    def _on_location_entered(self, location_id: str) -> None:
        if location_id == "living_room" and not self.state.flags["met_mother"]:
            self.state.flags["met_mother"] = True
            print("\nYour mom is here, in her chair. She hears you come down.")
            print(self.objectives.set_objective(self.state, "talk_to_mom"))

        elif location_id == "front_door" and self.state.flags["permission_granted"]:
            print("The door is unlocked. You can go out whenever you're ready.")

    # ── Scene end ─────────────────────────────────────────────────────────────

    def _end_game(self) -> None:
        print("\n" + "─" * 40)
        print(f"You open the door, {self.state.player_name}.")
        print("The street is quieter than you expected.")
        print("The air is different out here — cooler, more honest.")
        print("You don't look back at the house.")
        print("The road is uncertain.")
        print("But it is finally yours to walk.")
        print("─" * 40)
        print("\n=== END OF SCENE ONE ===\n")
        self.state.running = False
