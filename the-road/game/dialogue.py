"""Dialogue orchestration for NPC interactions."""

from __future__ import annotations

from data.dialogue_data import (
    MOTHER_AFTER,
    MOTHER_SCENE1,
    MOTHER_SCENE1_HINT,
    MOM_QA,
)

# Words stripped from the front of a topic before lookup.
# Lets "ask mom about nate" and "ask mom nate" resolve identically.
_TOPIC_FILLERS = ("about ", "regarding ", "on ", "the ")


def _strip_topic_fillers(topic: str) -> str:
    for filler in _TOPIC_FILLERS:
        if topic.startswith(filler):
            topic = topic[len(filler):]
    return topic.strip()


class DialogueManager:

    def talk_to_mother(self, state) -> tuple:
        """
        Primary 'talk mom' interaction.
        Returns (dialogue_lines, hint_text).
        hint_text is an empty string when there is nothing extra to show.
        """
        if not state.flags["mom_talked"]:
            state.flags["mom_talked"] = True
            state.flags["permission_granted"] = True
            return list(MOTHER_SCENE1), MOTHER_SCENE1_HINT

        return list(MOTHER_AFTER), ""

    def ask_mom(self, state, topic: str) -> tuple:
        """
        Handle 'ask mom <topic>' commands.
        Returns (answer_lines, follow_up_hint).

        Accepts both full commands and natural-language fragments:
          "about nate", "nate", "nate trail", "trail" (if unambiguous), etc.
        """
        if not state.flags["met_mother"]:
            return ["Your mom isn't here."], ""

        if not state.flags["mom_talked"]:
            return [
                "She looks up, but you haven't really spoken yet.",
                "Try 'talk mom' first.",
            ], ""

        topic = _strip_topic_fillers(topic.strip().lower())

        if not topic:
            return [], "(ask her about: nate  •  astari  •  outside  •  bob)"

        # ── Exact top-level match ─────────────────────────────────────────────
        entry = MOM_QA.get(topic)
        if entry:
            lines = list(entry["answer"])
            hint = entry["hint"] if topic not in state.questions_asked else ""
            if topic not in state.questions_asked:
                state.questions_asked.append(topic)
            return lines, hint

        # ── Exact subquestion match ───────────────────────────────────────────
        for parent in MOM_QA.values():
            followups = parent.get("followups", {})
            if topic in followups:
                return list(followups[topic]), ""

        # ── Partial subquestion: "trail" matches "nate trail" if unambiguous ──
        matches = []
        for parent_key, parent in MOM_QA.items():
            for sub_key, sub_lines in parent.get("followups", {}).items():
                if sub_key.endswith(" " + topic) or sub_key == topic:
                    matches.append((sub_key, sub_lines))

        if len(matches) == 1:
            return list(matches[0][1]), ""
        if len(matches) > 1:
            options = "  •  ".join(k for k, _ in matches)
            return [], f"(be more specific: {options})"

        # ── No match ─────────────────────────────────────────────────────────
        return (
            [f'She doesn\'t have much to say about "{topic}".'],
            "(ask her about: nate  •  astari  •  outside  •  bob)",
        )
