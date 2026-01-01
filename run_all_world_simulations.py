#!/usr/bin/env python3
"""
Run simulations for all world configs and save to test_outputs folder.

This script runs each world configuration and organizes outputs by world type.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

# World configs to run
WORLD_CONFIGS = [
    ("world_baseline", "configs/world_baseline.yaml"),
    ("world_high_trust_gov", "configs/world_high_trust_gov.yaml"),
    ("world_low_trust_gov", "configs/world_low_trust_gov.yaml"),
    ("world_strong_moderation", "configs/world_strong_moderation.yaml"),
    ("world_collapsed_local_media", "configs/world_collapsed_local_media.yaml"),
    ("world_high_religion_hub", "configs/world_high_religion_hub.yaml"),
    ("world_outrage_algorithm", "configs/world_outrage_algorithm.yaml"),
    ("world_phoenix", "configs/world_phoenix.yaml"),
    ("world_phoenix_multi_misinformation", "configs/world_phoenix_multi_misinformation.yaml"),
    ("world_phoenix_truth_random", "configs/world_phoenix_truth_random.yaml"),
]

# Phoenix configs (smaller for testing)
PHOENIX_CONFIGS = [
    ("phoenix_with_misinfo", "configs/world_phoenix_with_misinfo.yaml"),
    ("phoenix_test", "configs/world_phoenix_test.yaml"),
]

def run_simulation(name: str, config_path: str, output_dir: Path):
    """Run a single simulation."""
    output_path = output_dir / name
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*80}")
    print(f"Running: {name}")
    print(f"Config: {config_path}")
    print(f"Output: {output_path}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "sim", "run", "--config", config_path, "--out", str(output_path)],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ {name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {name} failed with error:")
        print(e.stderr)
        return False

def main():
    """Run all simulations."""
    output_base = Path("test_outputs")
    output_base.mkdir(exist_ok=True)
    
    # Create timestamped directory for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_base / f"world_simulations_{timestamp}"
    run_dir.mkdir(exist_ok=True)
    
    print("="*80)
    print("RUNNING ALL WORLD SIMULATIONS")
    print("="*80)
    print(f"Output directory: {run_dir}")
    print(f"Total configs: {len(WORLD_CONFIGS) + len(PHOENIX_CONFIGS)}")
    print()
    
    results = {}
    
    # Run standard world configs
    print("\n" + "="*80)
    print("STANDARD WORLD CONFIGS")
    print("="*80)
    for name, config_path in WORLD_CONFIGS:
        success = run_simulation(name, config_path, run_dir)
        results[name] = success
    
    # Run Phoenix configs (smaller, faster)
    print("\n" + "="*80)
    print("PHOENIX CONFIGS")
    print("="*80)
    for name, config_path in PHOENIX_CONFIGS:
        success = run_simulation(name, config_path, run_dir)
        results[name] = success
    
    # Summary
    print("\n" + "="*80)
    print("SIMULATION SUMMARY")
    print("="*80)
    successful = sum(1 for v in results.values() if v)
    failed = len(results) - successful
    
    print(f"Total simulations: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"\nResults saved to: {run_dir}")
    
    if failed > 0:
        print("\nFailed simulations:")
        for name, success in results.items():
            if not success:
                print(f"  - {name}")
    
    # Create summary file
    summary_path = run_dir / "simulation_summary.txt"
    with open(summary_path, 'w') as f:
        f.write("Simulation Run Summary\n")
        f.write("="*80 + "\n")
        f.write(f"Run timestamp: {timestamp}\n")
        f.write(f"Total simulations: {len(results)}\n")
        f.write(f"Successful: {successful}\n")
        f.write(f"Failed: {failed}\n\n")
        f.write("Results:\n")
        for name, success in results.items():
            status = "✓" if success else "✗"
            f.write(f"  {status} {name}\n")
    
    print(f"\n✓ Summary saved to: {summary_path}")

if __name__ == "__main__":
    main()
