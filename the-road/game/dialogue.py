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

# ── Natural-language synonym maps ─────────────────────────────────────────────
# Maps individual words → canonical topic slugs.
# Used as a last-resort fallback when exact and partial matching both fail.
# The resolver scans input left-to-right and returns the first match found,
# so word order determines priority in ambiguous phrases.

_MOM_SYNONYMS: dict[str, str] = {
    # → bob / bob sub-topics
    "bob":          "bob",
    "professor":    "bob",
    "keeper":       "bob",
    # → bob said (what happened / the situation)
    "happened":     "bob said",
    "situation":    "bob said",
    "happening":    "bob said",
    "visit":        "bob said",
    "morning":      "bob said",
    # → nate
    "nate":         "nate",
    # → nate trouble
    "trouble":      "nate trouble",
    "worried":      "nate trouble",
    "worry":        "nate trouble",
    "wrong":        "nate trouble",
    "problem":      "nate trouble",
    # → nate trail
    "trail":        "nate trail",
    "mystic":       "nate trail",
    # → forbidden trail (blessing trigger handled separately)
    "forbidden":    "forbidden trail",
    # → astari / sub-topics
    "astari":       "astari",
    "astrali":      "astari",
    "companion":    "astari",
    "bond":         "astrali bond",
    "bonding":      "astrali bond",
    "bonded":       "astrali bond",
    # → dangerous
    "dangerous":    "dangerous",
    "danger":       "dangerous",
    "safe":         "dangerous",
    "safety":       "dangerous",
    "risk":         "dangerous",
    # → outside / sub-topics
    "outside":      "outside",
    "world":        "outside",
    "roads":        "outside",
    "crests":       "outside crests",
    "crest":        "outside crests",
    "collapse":     "outside collapse",
}

_BOB_SYNONYMS: dict[str, str] = {
    # → nate
    "nate":         "nate",
    # → codex
    "codex":        "codex",
    "parcel":       "codex",
    "package":      "codex",
    "notes":        "codex",
    "guide":        "codex",
    # → trail
    "trail":        "trail",
    "mystic":       "trail",
    "forbidden":    "trail",
    "path":         "trail",
    # → astari
    "astari":       "astari",
    "astrali":      "astari",
    "bond":         "astari",
    "bonding":      "astari",
    "attunement":   "astari",
    "companion":    "astari",
    # → field
    "field":        "field",
    "noisy":        "field",
    "noise":        "field",
}


def _keyword_match(raw: str, synonyms: dict[str, str]) -> str | None:
    """
    Scan a free-form phrase word-by-word for the first synonym key match.

    Strips common punctuation before tokenizing so inputs like "Who is Bob?"
    and "What's wrong with Nate?" resolve correctly without the parser having
    already cleaned them.

    Returns the canonical topic slug, or None if no word matches.
    """
    cleaned = raw.lower()
    for ch in '".,!?;:-()':
        cleaned = cleaned.replace(ch, " ")
    for word in cleaned.split():
        if word in synonyms:
            return synonyms[word]
    return None


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

        mom_rel = state.relationships.get("mom", 0)
        if "mom_nate_dismissive" in state.choice_history or "mom_readiness_defensive" in state.choice_history:
            return ['She folds her arms. "You\'re still deciding what kind of promise you meant."'], ""
        if mom_rel >= 2:
            return ['Her voice softens. "I see you trying. Keep moving."'], ""
        if state.disposition <= -1:
            return ['She gives you a steady look. "Careful is fine. Frozen isn\'t."'], ""

        return list(MOTHER_AFTER), ""

    def talk_to_bob(self, state) -> tuple:
        if not state.flags["codex_given"]:
            return (
                [
                    "He's at the workbench when you walk in. Doesn't turn around right away — finishing something, the way he always is.",
                    '"Give me a second."',
                    "A moment passes. He sets down what he's holding and turns.",
                    '"Glad you came. I thought about coming back by your place — then decided to wait and see if you\'d come on your own."',
                    "A pause. Like he's checking something off.",
                    '"Nate\'s been reading the Mystic-Forbidden split. Running his own logs, asking questions I didn\'t have clean answers to. Then three days ago he stopped showing."',
                    '"Last thing he borrowed was this Codex."',
                    "He picks up a wrapped parcel from the bench — carefully bound, heavier than it looks.",
                    '"It\'s a field calibration guide. Helps you read the terrain when the Trail gets loud. Nate needs it. He went out without it and that\'s on me."',
                    '"Take it to him. He\'ll be at the overlook if he\'s anywhere."',
                    "He holds your eye a beat longer than is comfortable.",
                    '"And when you get back — we finish your attunement. Not a suggestion."',
                ],
                "(ask him about: nate  •  codex  •  trail  •  astrali  •  the field)",
            )
        if state.flags["codex_given"] and not state.flags["codex_delivered"]:
            reminder = '"Nate needs that Codex. Get it to the overlook and come back."'
            if "bob_codex_accept_cleanly" in state.choice_history:
                reminder = '"You said you\'d run it over. I trust that. Go."'
            elif "bob_codex_ask_urgency" in state.choice_history:
                reminder = '"You wanted urgency. Here it is: every hour out there matters."'
            elif "bob_codex_why_me" in state.choice_history:
                reminder = '"Still wondering why you? Carry it anyway. Answers come on the road."'
            return (
                [
                    '"You still have it."',
                    "Not accusing. Just noting.",
                    reminder,
                ],
                "",
            )
        if state.flags["codex_delivered"] and not state.flags["mom_blessing_available"]:
            return (
                [
                    '"You found him."',
                    "Not a question. He can tell by the way you walked in.",
                    '"Good."',
                    '"Now go talk to your mom. Not tonight — now. Tell her where you\'re going."',
                    '"She already suspects. Don\'t let her sit with that."',
                    '"Then come back here and we do this right."',
                ],
                "",
            )
        return (
            [
                '"You talked to your mom?"',
                "A beat. He reads your face.",
                '"Then we\'re ready. Let\'s not waste it."',
            ],
            "(ask him about: astrali  •  trail  •  the field)",
        )

    def ask_bob(self, state, topic: str) -> tuple:
        topic = self._normalize_topic(topic)
        answers = {
            "nate": [
                '"Nate was reading the Field — patterns in how the Trail shifts, which stretches go quiet when they shouldn\'t."',
                '"That\'s not usual work for someone his age. But Nate\'s not usual."',
                '"He had a theory about the Forbidden stretch. Wouldn\'t give me the whole of it."',
                '"That should have been my first sign."',
            ],
            "codex": [
                '"A Codex is a calibration record — built to your Astari\'s reading, tuned over time."',
                '"Out on the Trail, the Field can blur. Directions feel right when they\'re wrong. A Codex keeps you honest."',
                '"Nate\'s copy is annotated — his Astari helped him map three routes this year."',
                '"Without it he\'s navigating on instinct alone. That\'s survivable. Barely."',
            ],
            "trail": [
                '"Mystic is readable. Most people can manage it with a half-bonded partner."',
                '"Forbidden is different. The Field is dense there — loud. It pushes back in ways that feel personal."',
                '"People have gone in without a bonded Astari. Some came back changed. Some didn\'t come back."',
            ],
            "astari": [
                "He's quiet for a moment. Not hesitating — choosing.",
                '"The bond isn\'t something I can hand you. What I can do is set the conditions."',
                '"An Astari reads your field first. Decides if there\'s something worth committing to."',
                '"Most of the time, the answer is yes. But they need you actually present for it."',
                '"Half your attention doesn\'t bond anything."',
                '"Finish what you\'re doing for Nate. Come back here and be here. We\'ll go from there."',
            ],
            "field": [
                '"The Field is what the Trail moves through. What everything moves through."',
                '"Think of it as the current underneath — most people feel it without knowing what it is."',
                '"An Astari can read it clearly. A bonded pair even more so."',
                '"When the Field gets noisy, something\'s shifted. Could be weather. Could be something worse."',
                '"Right now it\'s noisy. That\'s all I\'ll say."',
            ],
        }
        if topic in answers:
            return answers[topic], ""

        # Natural language fallback — keyword scan.
        resolved = _keyword_match(topic, _BOB_SYNONYMS)
        if resolved and resolved in answers:
            return answers[resolved], ""

        return ['"Nate first. Your bond after. Everything else can wait."'], ""

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
            return [
                "She looks at you.",
                '"Something on your mind?"',
            ], ""

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

        # ── Natural language fallback — keyword scan ──────────────────────────
        resolved = _keyword_match(topic, _MOM_SYNONYMS)
        if resolved:
            entry = MOM_QA.get(resolved)
            if entry:
                lines = list(entry["answer"])
                hint = entry["hint"] if resolved not in state.questions_asked else ""
                if resolved not in state.questions_asked:
                    state.questions_asked.append(resolved)
                return lines, hint
            for parent in MOM_QA.values():
                if resolved in parent.get("followups", {}):
                    return list(parent["followups"][resolved]), ""

        # ── True fallback — nothing matched ───────────────────────────────────
        return (
            [
                '"Mm?"',
                "She looks at you a moment.",
                '"I\'m not sure what you\'re asking. Try saying it a different way."',
            ],
            "",
        )
