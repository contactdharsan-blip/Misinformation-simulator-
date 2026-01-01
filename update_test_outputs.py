#!/usr/bin/env python3
"""
Update test_outputs folder with new simulation runs based on literature-aligned parameters.

This script:
1. Runs key simulations with literature-aligned parameters
2. Organizes outputs in test_outputs/
3. Creates comparison analysis between old and new runs
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json

# Key simulations to run for testing literature alignment
KEY_SIMULATIONS = [
    {
        "name": "baseline_literature_aligned",
        "config": "configs/world_baseline.yaml",
        "description": "Baseline simulation with literature-aligned parameters"
    },
    {
        "name": "phoenix_literature_aligned",
        "config": "configs/world_phoenix_with_misinfo.yaml",
        "description": "Phoenix simulation with truth + 3 misinformation claims"
    },
    {
        "name": "high_trust_literature_aligned",
        "config": "configs/world_high_trust_gov.yaml",
        "description": "High trust government scenario"
    },
    {
        "name": "strong_moderation_literature_aligned",
        "config": "configs/world_strong_moderation.yaml",
        "description": "Strong moderation scenario"
    },
]

def run_simulation(name: str, config_path: str, output_dir: Path):
    """Run a simulation and return success status."""
    output_path = output_dir / name
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Running: {name}")
    print(f"  Config: {config_path}")
    print(f"  Output: {output_path}")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "sim", "run", "--config", config_path, "--out", str(output_path)],
            capture_output=True,
            text=True,
            check=True,
            timeout=3600  # 1 hour timeout
        )
        print(f"  ✓ Completed successfully\n")
        return True, output_path
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timed out after 1 hour\n")
        return False, None
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed: {e.stderr[:200]}\n")
        return False, None

def analyze_literature_alignment(output_path: Path):
    """Analyze if simulation results align with literature predictions."""
    try:
        import pandas as pd
        
        metrics_path = output_path / "daily_metrics.csv"
        if not metrics_path.exists():
            return None
        
        metrics = pd.read_csv(metrics_path)
        
        # Check for misinformation claims (claim != 0 or check strain_info)
        strain_info_path = output_path / "strain_info.json"
        is_misinfo = {}
        if strain_info_path.exists():
            with open(strain_info_path) as f:
                strain_info = json.load(f)
                for i, strain_name in enumerate(strain_info.get("initial_strains", [])):
                    # Check if it's truth or misinformation
                    is_misinfo[i] = "truth" not in strain_name.lower() and "official" not in strain_name.lower()
        
        analysis = {
            "output_path": str(output_path),
            "total_days": int(metrics["day"].max() + 1),
            "claims": sorted(metrics["claim"].unique().tolist()),
        }
        
        # Analyze each claim
        for claim in sorted(metrics["claim"].unique()):
            claim_data = metrics[metrics["claim"] == claim]
            final = claim_data.iloc[-1]
            
            claim_analysis = {
                "final_adoption": float(final["adoption_fraction"]),
                "peak_adoption": float(claim_data["adoption_fraction"].max()),
                "peak_day": int(claim_data.loc[claim_data["adoption_fraction"].idxmax(), "day"]),
                "final_mean_belief": float(final["mean_belief"]),
            }
            
            # Check if matches literature targets
            # Roozenbeek et al. (2020): 20-35% adoption for misinformation
            if is_misinfo.get(claim, True):
                if 0.20 <= claim_analysis["final_adoption"] <= 0.35:
                    claim_analysis["matches_literature"] = "✓ Adoption rate in target range (20-35%)"
                else:
                    claim_analysis["matches_literature"] = f"⚠ Adoption rate {claim_analysis['final_adoption']:.1%} outside target range"
            
            # Cinelli et al. (2020): Peak around 21 ± 7 days
            if 14 <= claim_analysis["peak_day"] <= 28:
                claim_analysis["peak_timing"] = "✓ Peak timing matches literature (21 ± 7 days)"
            else:
                claim_analysis["peak_timing"] = f"⚠ Peak at day {claim_analysis['peak_day']} (target: 21 ± 7)"
            
            analysis[f"claim_{claim}"] = claim_analysis
        
        return analysis
    except Exception as e:
        return {"error": str(e)}

def main():
    """Run key simulations and update test_outputs."""
    output_base = Path("test_outputs")
    output_base.mkdir(exist_ok=True)
    
    # Create literature-aligned runs directory
    lit_dir = output_base / "literature_aligned_runs"
    lit_dir.mkdir(exist_ok=True)
    
    print("="*80)
    print("UPDATING TEST OUTPUTS WITH LITERATURE-ALIGNED SIMULATIONS")
    print("="*80)
    print(f"Output directory: {lit_dir}")
    print(f"Simulations to run: {len(KEY_SIMULATIONS)}")
    print()
    
    results = {}
    analyses = {}
    
    for sim_config in KEY_SIMULATIONS:
        name = sim_config["name"]
        config_path = sim_config["config"]
        description = sim_config["description"]
        
        print(f"\n{description}")
        print("-" * 80)
        
        success, output_path = run_simulation(name, config_path, lit_dir)
        results[name] = {
            "success": success,
            "output_path": str(output_path) if output_path else None,
            "description": description
        }
        
        if success and output_path:
            # Analyze literature alignment
            analysis = analyze_literature_alignment(output_path)
            if analysis:
                analyses[name] = analysis
    
    # Create summary report
    summary_path = lit_dir / "literature_alignment_summary.json"
    summary = {
        "run_timestamp": datetime.now().isoformat(),
        "simulations": results,
        "analyses": analyses,
        "literature_targets": {
            "adoption_rate_range": "20-35% (Roozenbeek et al., 2020)",
            "peak_timing": "21 ± 7 days (Cinelli et al., 2020)",
            "spread_ratio": "6x false vs true (Vosoughi et al., 2018)",
            "age_sharing_ratio": "7x for 65+ vs 18-29 (Guess et al., 2019)",
            "correction_effectiveness": "25% ± 8% (Walter & Tukachinsky, 2020)",
        }
    }
    
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    successful = sum(1 for r in results.values() if r["success"])
    print(f"Successful simulations: {successful}/{len(KEY_SIMULATIONS)}")
    print(f"Results saved to: {lit_dir}")
    print(f"Summary saved to: {summary_path}")
    
    if analyses:
        print("\nLiterature Alignment Analysis:")
        for name, analysis in analyses.items():
            if "error" not in analysis:
                print(f"\n{name}:")
                for key, value in analysis.items():
                    if key.startswith("claim_"):
                        print(f"  {key}:")
                        for k, v in value.items():
                            if isinstance(v, str) and ("✓" in v or "⚠" in v):
                                print(f"    {k}: {v}")

if __name__ == "__main__":
    main()
