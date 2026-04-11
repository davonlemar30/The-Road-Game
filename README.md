# The Road

**Alpha Build:** `v0.3.3-alpha.4`  
**Codename:** `canon-opening-pass`

A terminal-based narrative RPG about choice, connection, and quiet transformation at the edge of a changing world.

---

## Overview

**The Road** is a story-driven terminal RPG focused on exploration, conversation, and emotional progression. It blends authored narrative beats with player input in a text-first interface designed to feel intimate, readable, and reactive.

This build contains an **Act 1 intro vertical slice** that now reflects the current canon structure:

- Waking at GP’s house  
- Talking with Mom  
- Stepping into Iso Town  
- Finding **Keeper Bob** at the **Keeper’s Dome**  
- Receiving Nate’s Codex  
- Traveling to Mystic Trail  
- Returning to continue Act 1 progression  

Long-term, the project will expand into Astari bonding, combat, survival pressure, hidden narrative state, and deeper route-based progression.

---

## Current Build

This is the most stable and canon-aligned version of the **Act 1 intro vertical slice** so far.

### Included

- Player naming and intro flow  
- Save/load support with compatibility-safe state merging  
- House exploration with intentional `look` / `inspect` play  
- Room-based navigation (e.g. `go downstairs`, `go kitchen`)  
- Objective tracking and scene gating  
- Iso Town navigation and location discovery  
- Phone unlock and map access flow  
- Keeper’s Dome → Mystic Trail codex-delivery loop  
- Framed dialogue UI with paginated text  
- Stationary dialogue box rendering  
- Guided multiple-choice moments in key scenes (Mom, Bob)  
- Parser-backed follow-up questions (limited, stability-first)  
- Early hidden narrative-state system:
  - reputation  
  - disposition  
  - relationships  
  - choice history  
- Basic NPC interaction layer  
- Minimal shop/economy shell  

---

## What Changed in This Build

### Canon Alignment Pass
- Scene 1 now ends with **Find Keeper Bob** (correct story flow)  
- Opening progression now cleanly follows:
  - Bob → Dome → Codex → Mystic Trail  
- Removed legacy **Professor Bob / lab** wording  
- Standardized naming to **Keeper Bob / Keeper’s Dome**

### Dialogue & Flow Improvements
- Refined Mom conversation to better match current story tone  
- Improved choice coherence and emotional clarity  
- Reduced awkward or immersion-breaking responses  

### Navigation & UX
- Shifted early gameplay toward **room-based navigation**  
- Cleaner guidance and hinting throughout the opening  
- Reduced parser friction in critical early scenes  

---

## Core Design Philosophy

### Narrative First
Systems exist to support tone, characters, and story progression.

### Text With Presence
The terminal is part of the experience — pacing, framing, and readability are intentional.

### Curated Where It Matters
- Explicit choices for emotional/story beats  
- Parser input for exploration and curiosity  

### Modular Systems
The game is built to scale:
- data-driven dialogue and objectives  
- expandable state model  
- modular content files  
- future support for combat, survival, and Astari systems  

---

## Running the Game

### Standard
```bash
python the-road/main.py