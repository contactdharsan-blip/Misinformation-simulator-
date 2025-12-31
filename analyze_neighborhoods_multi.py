#!/usr/bin/env python3
"""Analyze adoption rates by neighborhood from simulation results with multiple claims."""

import pandas as pd
import numpy as np
from pathlib import Path
from sim.config import load_config
from sim.town.generator import generate_town
from sim.rng import RNGManager

def analyze_neighborhood_adoption(config_path: str, output_dir: str):
    """Analyze adoption rates by neighborhood."""
    # Load config
    cfg = load_config(config_path)
    
    # Regenerate town with same seed to get neighborhood assignments
    rng_manager = RNGManager(cfg.sim.seed, cfg.sim.deterministic)
    town = generate_town(
        rng_manager.numpy,
        cfg.sim.n_agents,
        cfg.town,
        cfg.traits,
        cfg.world,
        cfg.network,
    )
    
    # Load snapshots
    snapshots_path = Path(output_dir) / "belief_snapshots.parquet"
    if not snapshots_path.exists():
        snapshots_path = Path(output_dir) / "belief_snapshots.csv"
    
    if not snapshots_path.exists():
        print(f"Error: No snapshots file found at {snapshots_path}")
        return
    
    snapshots = pd.read_parquet(snapshots_path) if snapshots_path.suffix == '.parquet' else pd.read_csv(snapshots_path)
    
    # Add neighborhood IDs to snapshots
    snapshots['neighborhood_id'] = town.neighborhood_ids[snapshots['agent_id'].values]
    
    # Get neighborhood names and demographics
    neighborhood_info = {}
    if hasattr(cfg.town, 'neighborhood_specs') and cfg.town.neighborhood_specs:
        for idx, spec in enumerate(cfg.town.neighborhood_specs):
            name = spec.get('name', f'neighborhood_{idx}')
            demos = spec.get('demographics', {})
            edu = demos.get('college_educated', 0)
            income = demos.get('median_income', 0)
            neighborhood_info[idx] = {
                'name': name,
                'edu': edu,
                'income': income
            }
    else:
        for idx in range(town.neighborhoods):
            neighborhood_info[idx] = {
                'name': f'neighborhood_{idx}',
                'edu': 0,
                'income': 0
            }
    
    # Get claim columns
    claim_cols = [c for c in snapshots.columns if c.startswith('claim_')]
    
    # Get strain names
    strain_names = {}
    for i, col in enumerate(claim_cols):
        if i < len(cfg.strains):
            strain_names[i] = cfg.strains[i].name
        else:
            strain_names[i] = f'claim_{i}'
    
    adoption_threshold = cfg.sim.adoption_threshold
    
    print("\n" + "="*100)
    print("NEIGHBORHOOD ADOPTION ANALYSIS - MULTIPLE CLAIMS")
    print("="*100)
    
    # Analyze multiple days to see progression
    target_days = [0, 5, 10, 15, 20, 25]
    available_days = sorted(snapshots['day'].unique())
    target_days = [d for d in target_days if d in available_days]
    
    for claim_idx, claim_col in enumerate(claim_cols):
        claim_num = claim_col.split('_')[1]
        strain_name = strain_names.get(claim_idx, f'claim_{claim_num}')
        is_truth = claim_idx < len(cfg.strains) and getattr(cfg.strains[claim_idx], 'is_true', False)
        
        print(f"\n{'='*100}")
        print(f"CLAIM {claim_num}: {strain_name} ({'TRUTH' if is_truth else 'MISINFORMATION'})")
        print(f"{'='*100}")
        
        for day in target_days:
            day_data = snapshots[snapshots['day'] == day].copy()
            if day_data.empty:
                continue
            
            print(f"\n--- Day {day} ---")
            print(f"{'Neighborhood':<25} {'Edu':<8} {'Income':<12} {'Adoption':<12} {'Mean Belief':<15}")
            print("-" * 85)
            
            neighborhood_stats = []
            for nid in range(town.neighborhoods):
                n_mask = day_data['neighborhood_id'] == nid
                n_data = day_data[n_mask]
                
                if len(n_data) == 0:
                    continue
                
                beliefs = n_data[claim_col].values
                adopted = (beliefs >= adoption_threshold).sum()
                adoption_rate = adopted / len(n_data)
                mean_belief = beliefs.mean()
                
                info = neighborhood_info[nid]
                neighborhood_stats.append({
                    'neighborhood': info['name'],
                    'nid': nid,
                    'population': len(n_data),
                    'adoption_rate': adoption_rate,
                    'mean_belief': mean_belief,
                    'edu': info['edu'],
                    'income': info['income']
                })
                
                print(f"{info['name']:<25} {info['edu']:<8.2f} ${int(info['income']):<11} {adoption_rate:<12.4f} {mean_belief:<15.4f}")
            
            # Summary statistics
            if neighborhood_stats:
                stats_df = pd.DataFrame(neighborhood_stats)
                print(f"\n  Summary:")
                print(f"    Mean adoption: {stats_df['adoption_rate'].mean():.4f}")
                print(f"    Std adoption: {stats_df['adoption_rate'].std():.4f}")
                print(f"    Range: {stats_df['adoption_rate'].max() - stats_df['adoption_rate'].min():.4f}")
                
                # Compare high vs low education neighborhoods
                high_edu = stats_df[stats_df['edu'] > 0.6]
                low_edu = stats_df[stats_df['edu'] < 0.3]
                
                if len(high_edu) > 0 and len(low_edu) > 0:
                    print(f"    High-edu neighborhoods (edu > 0.6):")
                    print(f"      Mean adoption: {high_edu['adoption_rate'].mean():.4f}")
                    print(f"      Mean belief: {high_edu['mean_belief'].mean():.4f}")
                    print(f"    Low-edu neighborhoods (edu < 0.3):")
                    print(f"      Mean adoption: {low_edu['adoption_rate'].mean():.4f}")
                    print(f"      Mean belief: {low_edu['mean_belief'].mean():.4f}")
                    if not is_truth:
                        diff = low_edu['adoption_rate'].mean() - high_edu['adoption_rate'].mean()
                        print(f"    Difference (low-edu - high-edu): {diff:.4f}")
                        if abs(diff) > 0.05:
                            print(f"    ✓ Meaningful difference detected!")
                        elif stats_df['adoption_rate'].std() > 0.05:
                            print(f"    ✓ Neighborhoods show variation (std > 0.05)")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python analyze_neighborhoods_multi.py <config_path> <output_dir>")
        sys.exit(1)
    
    analyze_neighborhood_adoption(sys.argv[1], sys.argv[2])
