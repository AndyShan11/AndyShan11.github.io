"""Regenerate static publication posters from the semantic scenes.

The animation generator is the single visual source of truth, so a later
poster-only build cannot restore the retired decorative figures.
"""

from generate_publication_animations import PAPER_DIR, SCENES


def main() -> None:
    for name, renderer in SCENES:
        output = PAPER_DIR / f"{name}.png"
        renderer(.90).save(output, optimize=True)
        print(f"{output.name}: {output.stat().st_size / 1024:.0f} KiB")


if __name__ == "__main__":
    main()
