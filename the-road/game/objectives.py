"""Objective update helpers."""

from data.objectives_data import OBJECTIVES


class ObjectiveTracker:
    def __init__(self) -> None:
        self.objectives = OBJECTIVES

    def set_objective(self, state, key: str, *, added: bool = False) -> str:
        text = self.objectives[key]
        state.current_objective = text
        label = "OBJECTIVE ADDED" if added else "OBJECTIVE UPDATED"
        return f"\n{label}: {text}"
