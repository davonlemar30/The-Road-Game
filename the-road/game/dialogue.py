"""Dialogue orchestration for NPC interactions."""

from data.dialogue_data import (
    MOTHER_AFTER,
    MOTHER_SCENE1,
    MOTHER_SCENE1_PROMPT,
    MOM_QA,
)


class DialogueManager:
    def talk_to_mother(self, state) -> list[str]:
        """Primary talk interaction with Mom."""
        if not state.flags["mom_talked"]:
            state.flags["mom_talked"] = True
            state.flags["permission_granted"] = True
            return list(MOTHER_SCENE1) + [MOTHER_SCENE1_PROMPT]

        return list(MOTHER_AFTER)

    def ask_mom(self, state, topic: str) -> list[str]:
        """
        Handle 'ask mom <topic>' commands.

        Topic can be a top-level key ("nate", "astari", "outside", "bob")
        or a subquestion key ("nate trail", "astari bond", etc.).
        Returns the answer lines, or an error message if topic not found.
        """
        if not state.flags["met_mother"]:
            return ["Your mom isn't here."]
        if not state.flags["mom_talked"]:
            return [
                "She looks up, but you haven't really spoken yet.",
                "Try 'talk mom' first.",
            ]

        topic = topic.strip().lower()
        if not topic:
            return [
                "Ask her about what?",
                "  ask mom nate | ask mom astari | ask mom outside | ask mom bob",
            ]

        # Look up exact match first
        entry = MOM_QA.get(topic)
        if entry:
            lines = list(entry["answer"])
            if topic not in state.questions_asked:
                state.questions_asked.append(topic)
                lines.append(f"\n  Follow-up questions: {entry['hint']}")
            return lines

        # Try subquestion lookup (e.g. "nate trail")
        for parent_key, parent in MOM_QA.items():
            followups = parent.get("followups", {})
            if topic in followups:
                return list(followups[topic])

        # Fuzzy: check if the topic starts with a known parent key
        for parent_key in MOM_QA:
            if topic.startswith(parent_key + " "):
                sub = topic[len(parent_key) + 1:]
                followups = MOM_QA[parent_key].get("followups", {})
                full_key = f"{parent_key} {sub}"
                if full_key in followups:
                    return list(followups[full_key])

        return [
            f'She doesn\'t seem to have much to say about "{topic}".',
            "  ask mom nate | ask mom astari | ask mom outside | ask mom bob",
        ]
