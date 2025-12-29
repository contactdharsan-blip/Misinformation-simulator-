#!/usr/bin/env python3
"""
Single test runner that updates results in place.
Each run overwrites the previous results in runs/test/
"""

import subprocess
import sys
from pathlib import Path

def run_test():
    """Run the simulation and update results in runs/test/"""
    config = "configs/world_phoenix_truth_random.yaml"
    output_dir = "runs/test"
    
    # Default parameters
    seed = 42
    steps = 200
    n_agents = 1000
    
    # Allow command line overrides
    if len(sys.argv) > 1:
        seed = int(sys.argv[1])
    if len(sys.argv) > 2:
        steps = int(sys.argv[2])
    if len(sys.argv) > 3:
        n_agents = int(sys.argv[3])
    
    cmd = [
        sys.executable, "-m", "sim", "run",
        "--config", config,
        "--seed", str(seed),
        "--steps", str(steps),
        "--n", str(n_agents),
        "--out", output_dir
    ]
    
    print("=" * 70)
    print("Running Simulation Test")
    print("=" * 70)
    print(f"Config: {config}")
    print(f"Output: {output_dir}")
    print(f"Seed: {seed}")
    print(f"Steps: {steps}")
    print(f"Agents: {n_agents}")
    print("=" * 70)
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    if result.returncode == 0:
        print("\n" + "=" * 70)
        print("Simulation completed successfully!")
        print(f"Results saved to: {output_dir}/")
        print("=" * 70)
        
        # Show summary
        summary_path = Path(output_dir) / "summary.json"
        if summary_path.exists():
            import json
            with open(summary_path) as f:
                summary = json.load(f)
            print("\nSummary:")
            for key, value in summary.items():
                if "adoption" in key:
                    print(f"  {key}: {value:.1%}")
                elif "day" in key:
                    print(f"  {key}: {int(value)}")
                else:
                    print(f"  {key}: {value:.3f}")
    else:
        print("\nSimulation failed!")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
