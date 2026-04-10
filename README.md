# The Road

**Alpha Build:** `v0.3.2-alpha.3`
**Codename:** `alpha-intro-pass-01`

A terminal-based narrative RPG about choice, connection, and quiet transformation at the edge of a changing world.

---

## Overview

**The Road** is a story-driven terminal RPG focused on exploration, conversation, and emotional progression. It blends authored narrative beats with player input in a text-first interface designed to feel intimate, readable, and reactive.

This build contains an **Act 1 intro vertical slice** that covers:
- Waking at GP’s house
- Talking with Mom
- Stepping into Iso Town
- Finding Professor Bob at the Keeper’s Dome
- Delivering Nate’s Codex parcel to Mystic Trail
- Returning to continue Act 1 progression

Long-term, the project will expand into Astari bonding, combat, survival pressure, hidden narrative state, and deeper route-based progression. For now, the focus is on making the opening strong, coherent, and replayable.

---

## Current Build

This is the most complete version of the **Act 1 intro vertical slice** so far.

### Included

- Player naming and intro flow
- Save/load support with compatibility-safe state merging
- House exploration with intentional `look` / `inspect` play
- GP’s bedroom and house interactables
- Objective tracking and scene gating
- Iso Town navigation across multiple connected locations
- Fog-of-war style location discovery tracking
- Phone unlock and map access flow
- Keeper’s Dome / Mystic Trail codex-delivery loop
- Framed dialogue UI with paginated text
- Stationary dialogue box rendering in supported terminals
- Guided multiple-choice moments in key Mom/Bob scenes
- Parser-backed follow-up questions where reliable
- Early hidden narrative-state support:
  - reputation
  - disposition
  - relationship memory
  - choice history
- Basic town NPC interactions and guidance
- Minimal shop/economy shell

---

## What This Build Focuses On

This alpha centers on three priorities:

### 1. Conversation Feel
The intro leans into curated dialogue during emotionally important scenes (especially with Mom and Bob). The goal is for major beats to feel authored and coherent, not mechanically brittle.

### 2. A Stronger Opening Flow
The playable slice now carries the player from home, through town, to Bob, to Nate, and back again with clearer objectives and stronger scene gating.

### 3. Better Terminal UX
Dialogue presentation is more distinct from system text, and the intro is easier to test and replay.

---

## Core Design Philosophy

### Narrative First
Systems exist to support tone, characters, and story progression.

### Text With Presence
The game is terminal-based, but the interface is treated as part of the experience. Dialogue framing, pacing, and navigation are designed to feel intentional.

### Curated Where It Matters
The game uses a hybrid approach:
- explicit choices for emotional or story-driving moments
- parser/free-form input where exploration and curiosity make sense

### Modular Systems
Content and systems are built to scale:
- data-driven dialogue and objectives
- expandable state model
- modular content files
- room to layer in combat, survival, and Astari systems later

---

## Running the Game

### Standard
```bash
python the-road/main.py


Quick Start
./play.sh


play.sh is included as a simple launcher to make repeated testing easier.


Controls


Movement
go north
go south
go east
go west
go out
enter


Exploration
look
inspect [object]
where
map


Conversation
talk mom
talk bob
ask mom nate
ask mom astari
ask bob codex
ask bob trail


System
inventory
objective
save
load
help
quit


Conversation Model


The current build uses a hybrid conversation structure.



Guided Choices
Major emotional or story-significant moments use explicit choices. This is currently strongest in the opening Mom/Bob scenes.



Parser Follow-Ups
When the game can support it reliably, the player can still ask follow-up questions using commands like:

ask mom nate
ask mom bob said
ask bob trail
ask bob astari


The parser is still evolving. In this build, reliability is favored over breadth.



Save System


Saves are stored locally at:

saves/save.json


On startup, the game detects an existing save and prompts the player to load it. Save data is designed to merge older saves safely with newer state fields when possible.



Project Structure


the-road/
├── main.py
├── game/
│   ├── engine.py
│   ├── parser.py
│   ├── state.py
│   ├── dialogue.py
│   ├── display.py
│   ├── persistence.py
│   ├── town.py
│   ├── map_renderer.py
│   └── choices.py
├── data/
│   ├── locations.py
│   ├── dialogue_data.py
│   ├── choices_data.py
│   ├── objectives_data.py
│   ├── npcs.py
│   ├── town_locations.py
│   └── town_npcs_data.py
├── saves/
└── play.sh


Current Playable Slice


The current vertical slice roughly covers:

GP wakes up at home
The player explores the house
A conversation with Mom establishes Nate / Bob / Astari pressure
The player leaves for Iso Town
Town navigation opens
The player reaches the Keeper’s Dome
Bob sets the codex handoff in motion
The player reaches Mystic Trail and delivers the parcel
The player returns to continue progression toward the next scene gate


Not Implemented Yet


Planned, but not fully built:

starter selection as a full playable system
dedicated battle loop
Astari combat actions and move resolution
capture resolution in gameplay
bond progression systems in active play
survival pressures
deeper Bob conversation pass
broader natural-language conversation handling
richer inventory and item use
expanded town/world content beyond the current slice


Next Planned Focus


Bob Conversation Pass
unify talk bob and enter scene flow
strengthen Bob’s narrative weight
improve attunement / codex / Nate framing
keep the opening feeling authored and cohesive


Status


This project is in active alpha development. The current priority is quality of the opening experience, including:

cleaner conversation
stronger scene flow
tighter UX
better foundations for future systems


Author


Davon Gass



Vision


The Road aims to become a deep terminal RPG where:

the player’s choices carry emotional weight
systems emerge gradually instead of all at once
the story feels personal, grounded, and strange in the right ways
the interface stays simple, while the experience grows rich

