from pathlib import Path

from src.hcc827_use_case import run_hcc827_use_case


if __name__ == "__main__":
    output_dir = run_hcc827_use_case(Path(__file__).resolve().parent)
    print(f"HCC827 use case outputs written to: {output_dir}")
