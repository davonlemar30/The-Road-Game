"""Simple time-of-day helpers for The Road."""

from __future__ import annotations


def advance_time(state, minutes: int) -> None:
    """Advance world time by N minutes, carrying over day boundaries."""
    if minutes <= 0:
        return

    total = state.minutes_since_midnight + minutes
    day_gain, remainder = divmod(total, 24 * 60)
    state.minutes_since_midnight = remainder
    state.day += day_gain


def format_time_label(state) -> str:
    """Return a compact player-facing time string with day + block."""
    hour = state.minutes_since_midnight // 60
    minute = state.minutes_since_midnight % 60

    if 5 <= hour < 12:
        block = "Morning"
    elif 12 <= hour < 17:
        block = "Afternoon"
    elif 17 <= hour < 21:
        block = "Evening"
    else:
        block = "Night"

    return f"Day {state.day} • {hour:02d}:{minute:02d} ({block})"
