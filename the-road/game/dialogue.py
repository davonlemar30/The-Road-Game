"""Dialogue orchestration for NPC interactions."""

from data.dialogue_data import DIALOGUE_SEQUENCES


class DialogueManager:
    def __init__(self) -> None:
        self.sequences = DIALOGUE_SEQUENCES

    def run_sequence(self, sequence_key: str) -> list[str]:
        return self.sequences.get(sequence_key, [])

    def talk_to_mother(self, state) -> list[str]:
        lines: list[str] = []
        if not state.flags["heard_astari_warning"]:
            lines.extend(self.run_sequence("mother_intro"))
            state.flags["heard_astari_warning"] = True
            return lines

        if not state.flags["dialogue_completed"]:
            lines.extend(self.run_sequence("mother_full_talk"))
            state.flags["dialogue_completed"] = True
            state.flags["permission_granted"] = True
            if "running shoes" not in state.inventory:
                state.inventory.append("running shoes")
            return lines

        lines.extend(self.run_sequence("mother_after"))
        return lines
