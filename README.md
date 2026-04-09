# The Road

A terminal-based narrative RPG focused on survival, choice, and connection in a collapsing world.

---

## 🧭 Overview

**The Road** is a text-based, story-driven RPG where players explore a grounded, emotional journey through a post-collapse world. The experience blends:

- Narrative exploration
- Player-driven dialogue
- Light survival mechanics
- Emerging systems (Astari, bonding, traits)

The game is designed as an **open-ended terminal experience**, where player input and interpretation shape progression.

---

## 🎮 Current State (Phase 1 – Scene One)

The current build represents a **playable vertical slice** of Scene One.

### Features

- ✅ Player naming + intro flow
- ✅ Exploration-based navigation
- ✅ Intentional `look` system (no auto-description)
- ✅ Dynamic objective tracking
- ✅ Fully implemented Mom interaction system:
  - Narrative dialogue
  - Topic-based questioning (`ask mom ...`)
  - Flexible input parsing
- ✅ Dialogue UI system:
  - Distinct formatting for NPC vs system text
  - Controlled pacing for readability
- ✅ Save / Load system (JSON-based)
- ✅ Clean progression gating (permission to leave)

---

## 🧠 Core Design Philosophy

The Road is built on three pillars:

### 1. Player Intent > UI Prompts
The system favors natural input over rigid menus:# The Road

A terminal-based narrative RPG focused on survival, choice, and connection in a collapsing world.

---

## 🧭 Overview

**The Road** is a text-based, story-driven RPG where players explore a grounded, emotional journey through a post-collapse world. The experience blends:

- Narrative exploration
- Player-driven dialogue
- Light survival mechanics
- Emerging systems (Astari, bonding, traits)

The game is designed as an **open-ended terminal experience**, where player input and interpretation shape progression.

---

## 🎮 Current State (Phase 1 – Scene One)

The current build represents a **playable vertical slice** of Scene One.

### Features

- ✅ Player naming + intro flow
- ✅ Exploration-based navigation
- ✅ Intentional `look` system (no auto-description)
- ✅ Dynamic objective tracking
- ✅ Fully implemented Mom interaction system:
  - Narrative dialogue
  - Topic-based questioning (`ask mom ...`)
  - Flexible input parsing
- ✅ Dialogue UI system:
  - Distinct formatting for NPC vs system text
  - Controlled pacing for readability
- ✅ Save / Load system (JSON-based)
- ✅ Clean progression gating (permission to leave)

---

## 🧠 Core Design Philosophy

The Road is built on three pillars:

### 1. Player Intent > UI Prompts
The system favors natural input over rigid menus:
ask mom nate
ask about astari
tell me about the outside

---

### 2. Narrative First
Every system supports the story — not the other way around.

Dialogue, environment, and progression are all designed to feel:
- grounded
- emotional
- intentional

---

### 3. Modular Systems
The architecture is designed to scale without rewrites:

- Engine logic separated from content
- Dialogue, locations, and objectives are data-driven
- Systems like combat, survival, and Astari can be layered in later

---

## 🕹️ Controls

### Movement
go north / south / east / west

### Exploration
look
inspect [object]

### Dialogue
talk mom
ask mom nate
ask about astari
tell me about bob

### System
inventory
save
load
help
quit

---

## 💾 Save System

- Saves are stored locally in:
saves/save.json

- The game will prompt to load an existing save on startup.

---

## 🧪 Running the Game

```bash
python the-road/main.py

🧱 Project Structure
the-road/
├── main.py
├── game/
│   ├── engine.py
│   ├── parser.py
│   ├── state.py
│   ├── dialogue.py
│   ├── display.py
│   ├── persistence.py
├── data/
│   ├── locations.py
│   ├── dialogue_data.py
│   ├── objectives_data.py
│   ├── npcs.py

🔮 Next Steps
Planned expansions:
Scene 2: Professor Bob + Lab
Scene 3: Nate + Mystic Trail
Scene 4: Running shoes + deeper progression
Inventory improvements (descriptions, use effects)
Expanded NPC system (multi-character interaction)
Combat + survival systems
Astari bonding system

⚠️ Notes
This project is in active development
Systems are intentionally minimal but scalable
Focus is currently on solidifying core experience before expansion

🧑‍💻 Author
Davon Gass

🛣️ Vision
The goal of The Road is to create a deep, evolving text-based RPG where:
choices matter
systems emerge over time
and the player’s journey feels personal and grounded