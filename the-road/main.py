"""Entry point for The Road Phase 1 prototype."""

from game.engine import GameEngine


def main() -> None:
    engine = GameEngine()
    engine.run()


if __name__ == "__main__":
    main()
