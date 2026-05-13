from pathlib import Path

from src.presentation_assets import build_presentation_assets


if __name__ == "__main__":
    output_dir = build_presentation_assets(Path(__file__).resolve().parent)
    print(f"Presentation assets written to: {output_dir}")
