"""Dialogue orchestration for NPC interactions."""

from __future__ import annotations

from data.dialogue_data import (
    MOTHER_AFTER,
    MOTHER_SCENE1,
    MOTHER_SCENE1_HINT,
    MOM_BLESSING,
    MOM_BLESSING_HINT,
    MOM_QA,
)
from data.town_npcs_data import TOWN_NPC_DIALOGUE

# Words stripped from the front of a topic before lookup.
# Lets "ask mom about nate" and "ask mom nate" resolve identically.
_TOPIC_FILLERS = ("about ", "regarding ", "on ", "the ")

# Topics that trigger the mom's blessing + phone handoff.
# Any of these phrases means the player is committing to going out.
_PLAN_TOPICS = {
    "plan", "go", "going", "leave", "leaving", "i'm going", "im going",
    "i'll go", "ill go", "forbidden", "forbidden trail", "trail",
    "i'm ready", "im ready", "ready", "let's go", "lets go", "astrali", "astari",
}

_ASTRALI_ALIASES = {"astari", "astrali"}


def _strip_topic_fillers(topic: str) -> str:
    for filler in _TOPIC_FILLERS:
        if topic.startswith(filler):
            topic = topic[len(filler):]
    return topic.strip()


class DialogueManager:
    def _normalize_topic(self, topic: str) -> str:
        cleaned = _strip_topic_fillers(topic.strip().lower())
        if cleaned in _ASTRALI_ALIASES:
            return "astari"
        if cleaned.startswith("astari "):
            cleaned = "astrali " + cleaned[len("astari "):]
        return cleaned

    def talk_to_mother(self, state) -> tuple:
        """
        Primary 'talk mom' interaction.
        Returns (dialogue_lines, hint_text).
        hint_text is an empty string when there is nothing extra to show.
        """
        if not state.flags["mom_talked"]:
            state.flags["mom_talked"] = True
            # permission_granted is NOT set here — player must tell mom their plan first
            return list(MOTHER_SCENE1), MOTHER_SCENE1_HINT

        if state.flags["told_mom_plans"]:
            return ['She nods toward the door. "Go while you still mean it."'], ""

        return list(MOTHER_AFTER), ""

    def talk_to_bob(self, state) -> tuple:
        if not state.flags["codex_given"]:
            return (
                [
                    '"You made it. Good." Bob gestures at a wrapped parcel on the bench.',
                    '"Nate\'s been chasing trail anomalies. I need this Codex in his hands, not on my shelf."',
                    '"Take it to Mystic Trail. He\'ll be near the overlook if he\'s anywhere."',
                ],
                "(ask him about: nate  •  codex  •  astrali)",
            )
        if state.flags["codex_delivered"] and not state.flags["mom_blessing_available"]:
            return (
                [
                    '"You found him? Good."',
                    '"Before anything else: go talk to your mom. Then come back and we do this right."',
                ],
                "",
            )
        return (
            ['"You know the sequence: family first, then the bond. We\'re close."'],
            "(ask him about: astrali  •  trail)",
        )

    def ask_bob(self, state, topic: str) -> tuple:
        topic = self._normalize_topic(topic)
        answers = {
            "nate": [
                '"Nate was mapping the Mystic-Forbidden split. He said the Field felt noisy lately."',
                '"He doesn\'t always know when to stop. That\'s why I asked you."',
            ],
            "codex": [
                '"It\'s a calibrated field guide. Not just notes — it helps stabilize route decisions."',
                '"Nate should have had his copy a week ago."',
            ],
            "trail": [
                '"Mystic is manageable. Forbidden is not, not without a bonded Astrali."',
            ],
            "astari": [
                '"Astrali choose as much as we do. I can guide the process, not force it."',
                '"Come back after you handle home. Half-commitments get people hurt."',
            ],
        }
        if topic in answers:
            return answers[topic], ""
        return ['"Keep it simple: Nate first, then we handle your bond."'], ""

    def talk_to_town_npc(self, npc_id: str) -> tuple:
        info = TOWN_NPC_DIALOGUE.get(npc_id)
        if not info:
            return ["They nod, but don't have much to add right now."], ""
        return list(info["talk"]), info.get("hint", "")

    def ask_town_npc(self, npc_id: str, topic: str) -> tuple:
        info = TOWN_NPC_DIALOGUE.get(npc_id)
        if not info:
            return ["They shrug. Nothing useful."], ""
        topic = self._normalize_topic(topic)
        if topic in info.get("topics", {}):
            return list(info["topics"][topic]), ""
        return [f'"Not sure about {topic}. Try asking someone closer to it."'], info.get("hint", "")

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

        topic = self._normalize_topic(topic)

        # ── Blessing trigger: player commits to going ─────────────────────────
        if topic in _PLAN_TOPICS and not state.flags["mom_blessing_available"]:
            return (
                [
                    "She studies you for a moment.",
                    '"If this is about leaving, talk to Bob first. Then come back and tell me."',
                ],
                "",
            )

        if topic in _PLAN_TOPICS and not state.flags["told_mom_plans"]:
            state.flags["told_mom_plans"] = True
            state.flags["permission_granted"] = True
            state.flags["has_old_phone"] = True
            if "Old phone (Mom's)" not in state.inventory:
                state.inventory.append("Old phone (Mom's)")
            return list(MOM_BLESSING), MOM_BLESSING_HINT

        if topic in _PLAN_TOPICS and state.flags["told_mom_plans"]:
            return ['She nods at the door. "You already know. Go."'], ""

        if not topic:
            return [], "(ask her about: bob said  •  nate  •  astrali  •  dangerous)"

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
            "(ask her about: bob said  •  nate  •  astrali  •  dangerous)",
        )
