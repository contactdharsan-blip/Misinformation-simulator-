import os
import subprocess
import sys
from pathlib import Path

def main():
    config_dir = Path("configs")
    output_base = Path("test_outputs/nuance_batch_run")
    # Clean up old inconsistent batch run to ensure fresh plots
    if output_base.exists():
        import shutil
        shutil.rmtree(output_base)
    output_base.mkdir(parents=True, exist_ok=True)

    configs = [f for f in config_dir.glob("*.yaml")]
    print(f"Found {len(configs)} configurations.")

    for config_path in configs:
        name = config_path.stem
        output_path = output_base / name
        print(f"\nRunning simulation for: {name}")
        
        # running with --steps 20
        cmd = [
            sys.executable, "-m", "sim", "run",
            "--config", str(config_path),
            "--out", str(output_path),
            "--steps", "20"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"Successfully completed {name}")
        except subprocess.CalledProcessError as e:
            print(f"Error running {name}: {e}")

if __name__ == "__main__":
    main()
