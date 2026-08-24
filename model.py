from pathlib import Path
import runpy
import joblib
import os


def main():
    script_path = Path(__file__).resolve().with_name("bank model.py")

    if not script_path.exists():
        raise FileNotFoundError(
            "Missing training script: 'bank model.py'. "
            "Please keep the model generator file in the project folder."
        )

    runpy.run_path(str(script_path), run_name="__main__")


if __name__ == "__main__":
    main()
