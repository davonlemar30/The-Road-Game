"""Main game engine and command loop."""

from data.npcs import NPCS
from game.dialogue import DialogueManager
from game.objectives import ObjectiveTracker
from game.parser import parse_command
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
        self._prompt_player_name()
        print(self.objectives.set_objective(self.state, "look_around"))
        print(self.world.describe_location(self.state.current_location))

        while self.state.running:
            raw = input("\n> ")
            verb, arg = parse_command(raw)
            self._handle_command(verb, arg)

    def _show_intro(self) -> None:
        print("=== THE ROAD ===")
        print("Prologue: STILL HERE")
        print("You wake where you've always been: waiting for movement to become a decision.")

    def _prompt_player_name(self) -> None:
        while not self.state.player_name:
            name = input("What is your name? ").strip()
            if name:
                self.state.player_name = name
            else:
                print("Please enter a name.")
        print(f"\nMorning, {self.state.player_name}.")

    def _handle_command(self, verb: str, arg: str) -> None:
        if not verb:
            print("Type a command. Try: look, go south, inspect mirror, talk mother, help.")
            return

        handlers = {
            "look": self._cmd_look,
            "go": self._cmd_go,
            "inspect": self._cmd_inspect,
            "talk": self._cmd_talk,
            "help": self._cmd_help,
            "objective": self._cmd_objective,
            "quit": self._cmd_quit,
        }

        handler = handlers.get(verb)
        if handler is None:
            print("I don't understand that command. Type 'help' for options.")
            return

        handler(arg)

    def _cmd_look(self, _arg: str) -> None:
        print(self.world.describe_location(self.state.current_location))

    def _cmd_go(self, arg: str) -> None:
        direction = arg.strip().lower()
        if not direction:
            print("Go where? Example: go south")
            return

        if self.state.current_location == "front_door" and direction == "out":
            if not self.state.flags["permission_granted"]:
                print("The lock holds. You are not ready to leave yet.")
                return
            self._end_game()
            return

        success, result = self.world.move(self.state.current_location, direction)
        if not success:
            print(result)
            return

        self.state.current_location = result
        print(self.world.describe_location(self.state.current_location))
        self._on_location_entered(result)

    def _cmd_inspect(self, arg: str) -> None:
        if not arg:
            print("Inspect what?")
            return
        print(self.world.inspect(self.state.current_location, arg))

    def _cmd_talk(self, arg: str) -> None:
        target = arg.strip().lower()
        if not target:
            print("Talk to who?")
            return

        mother_data = NPCS["mother"]
        if target not in mother_data["aliases"]:
            print("You don't see them here.")
            return

        if self.state.current_location != mother_data["location"]:
            print("Your mother isn't here.")
            return

        lines = self.dialogue.talk_to_mother(self.state)
        for line in lines:
            print(line)

        if self.state.flags["met_mother"] and not self.state.flags["objective_find_nate_added"]:
            print(self.objectives.set_objective(self.state, "find_nate", added=True))
            self.state.flags["objective_find_nate_added"] = True
            print(self.objectives.set_objective(self.state, "talk_to_mom"))

        if self.state.flags["dialogue_completed"]:
            print(self.objectives.set_objective(self.state, "prepare_to_leave"))
            print(self.objectives.set_objective(self.state, "leave_house"))

    def _cmd_help(self, _arg: str) -> None:
        print("Available commands:")
        print("  look")
        print("  go [direction] (north/south/east/west/out)")
        print("  inspect [object]  (alias: examine [object])")
        print("  talk [target]")
        print("  objective")
        print("  help")
        print("  quit")

    def _cmd_objective(self, _arg: str) -> None:
        if self.state.current_objective:
            print(f"Current objective: {self.state.current_objective}")
        else:
            print("No current objective.")

    def _cmd_quit(self, _arg: str) -> None:
        print("You stay in the house a little longer.")
        self.state.running = False

    def _on_location_entered(self, location_id: str) -> None:
        if location_id == "living_room":
            if not self.state.flags["met_mother"]:
                print("Your mother sits by the TV, listening without turning around.")
                self.state.flags["met_mother"] = True
                print(self.objectives.set_objective(self.state, "find_nate", added=True))
                self.state.flags["objective_find_nate_added"] = True
                print(self.objectives.set_objective(self.state, "talk_to_mom"))
        elif location_id == "front_door" and self.state.flags["permission_granted"]:
            print("The lock is disengaged. You can go out when you're ready.")

    def _end_game(self) -> None:
        print("\nYou open the door and step into the morning air.")
        print("The road is uncertain, but it is finally yours to walk.")
        print("=== END OF PHASE 1 PROTOTYPE ===")
        self.state.running = False
