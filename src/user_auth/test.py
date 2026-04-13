from pathlib import Path
_MODEL_CACHE_DIR = Path(__file__).parent.parent / "nlu" / "wake_word_detection" / "training" / "models"

run_dirs = sorted([d for d in _MODEL_CACHE_DIR.iterdir() if d.is_dir()], reverse=True)
            
if not run_dirs:
    raise FileNotFoundError("No trained models found.")

latest_run = run_dirs[0]
print(latest_run)