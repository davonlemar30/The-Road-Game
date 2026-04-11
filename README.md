v0.3.4-alpha.6 — DIALOGUE-MODE-PASS

Build label: v0.3.4-alpha.6
Codename: DIALOGUE-MODE-PASS

Summary of changes

What was removed

mom_readiness_response — fully excised. Deleted from choices_data.py. Call removed from engine._cmd_talk. Dead history-flag reference (mom_readiness_defensive) cleaned from dialogue.py. Zero orphaned references remain across any file. This beat had no support in the Scene 1 canon spec and was adding friction between the Nate response and the exit.

What was added

game/dialogue_session.py — new file, the Dialogue Mode framework

Beat — data class: lines: list[str] + optional choice_id: str
DialogueSession — runner: takes npc_name, ordered beats, optional closing_hint; prints a header rule, iterates beats, prints footer rule; returns {choice_id: selected_option_id} for every resolved choice
_npc_header() / _npc_footer() — visual boundary: ─── Your Mom ──────────────────────────────────── / ────────────────────────────────────────────────────────
Idempotency is handled by run_scene_choice inside each beat — sessions are safe to re-enter

data/choices_data.py — audri_who_choice (new)

Fires after Bob's "Good timing. I need a favor." — per Scene 2 canon's [Player Dialogue Choice] beat
Three options: who_was_that (Bob identifies Audri — all five Crests, finished a full circuit), focus_forward (skip it, get rep +1 with Bob), stay_quiet_dome
History flags: asked_about_audri, skipped_audri_question, stayed_quiet_dome

Files touched


How Dialogue Mode works

Every major NPC conversation now runs through DialogueSession. The player sees a named header rule when entering conversation and a closing rule when leaving it — clear visual separation from parser output. Inside the session, beats play in order: NPC lines display in the existing typewriter dialogue box, then an optional choice box appears. The session collects all choices and returns them. The parser (ask mom nate, ask bob codex, etc.) still works at any time — it bypasses the session and responds inline, as secondary/optional flavor.

─── Your Mom ────────────────────────────────────────────────────────────────────
┌──────────────────────────────────────────────────────────────────────────────┐
│ "Mornin', baby."                                                             │
│ She's at the counter...                                                      │
│ "You sleep okay?"                                                            │
│   ■ Enter                                                                    │
└──────────────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────────────┐
│ [1]  Slept fine. Yeah.                                                       │
│ [2]  Not really.                                                             │
│ [3]  [Stay quiet]                                                            │
│   ◆ Choose                                                                   │
└──────────────────────────────────────────────────────────────────────────────┘
[ ... Part 2 + Nate choice plays ... ]
She's here if there's more on your mind.
────────────────────────────────────────────────────────────────────────────────

Which NPCs/scenes now use Dialogue Mode


All three town NPCs get the header/footer wrapper automatically — no per-NPC code needed.

Parser behavior intentionally preserved

ask mom [topic] — still works, still returns lines directly (no session wrapper)
ask bob [topic] — still works
ask about [topic] — still works (shorthand when only one NPC present)
Natural language fallback (_handle_unknown) — still works
tell mom [plan] — still triggers blessing flow, still works

Tests run

14 smoke checks:

All imports clean
2–4. mom_readiness_response removed from choices_data, engine, dialogue (including dead ref)
audri_who_choice present, 3 options, correct IDs
bob_codex_response intact
DialogueSession.run() executes beats and returns choice results
GameEngine instantiates
No stale readiness refs in any file
SCENE_CHOICES data integrity (all options have id + text)
Mom scene content (sleep line in PART1, Keeper Bob in PART2)
Objective chain intact (all 6 objectives)
Engine source contains DialogueSession, Beat(PART1), Beat(PART2), audri_who_choice
No duplicate imports in engine.py

Result: 14/14 passed

Known limitations

ask mom/bob responses are not wrapped in a session — intentional, they're secondary parser lookups, not curated beats. They still use print_dialogue + print_hint directly.
Bob's talk_to_bob() path (before entering the Dome) returns a single-beat monologue — it's functional but not yet broken into sub-beats with internal choices. That would be a Scene 2 refinement task.
The audri_who_choice history flag asked_about_audri isn't yet used for reactive dialogue later (e.g. Bob referencing that you asked). Planting the flag now makes that easy to add.

Recommended next task

Scene 1 Bedroom Enrichment Pass — The Post-Alpha Test 4 notes specifically called out the bedroom feeling too plain and the computer/notes interactables being a strong opportunity for character establishment. The canon spec lists: TV+console, computer with half-finished research, loose Astari notes. Making those inspectable and giving them real text is the next highest-value, lowest-risk improvement to the opening slice before the next test build.