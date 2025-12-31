#!/usr/bin/env python3
"""Analyze adoption rates by neighborhood from simulation results."""

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
    
    # Get neighborhood names if available
    neighborhood_names = {}
    if hasattr(cfg.town, 'neighborhood_specs') and cfg.town.neighborhood_specs:
        for idx, spec in enumerate(cfg.town.neighborhood_specs):
            neighborhood_names[idx] = spec.get('name', f'neighborhood_{idx}')
    else:
        for idx in range(town.neighborhoods):
            neighborhood_names[idx] = f'neighborhood_{idx}'
    
    # Analyze adoption by neighborhood
    adoption_threshold = cfg.sim.adoption_threshold
    
    print("\n" + "="*80)
    print("NEIGHBORHOOD ADOPTION ANALYSIS")
    print("="*80)
    
    # Focus on day 25 (as per the plots)
    target_day = 25
    day_data = snapshots[snapshots['day'] == target_day].copy()
    
    if day_data.empty:
        print(f"No data for day {target_day}")
        available_days = sorted(snapshots['day'].unique())
        if available_days:
            target_day = available_days[-1]
            day_data = snapshots[snapshots['day'] == target_day].copy()
            print(f"Using day {target_day} instead")
    
    # Get claim columns (exclude day, agent_id, neighborhood_id)
    claim_cols = [c for c in day_data.columns if c.startswith('claim_')]
    
    for claim_col in claim_cols:
        claim_num = claim_col.split('_')[1]
        print(f"\n--- Claim {claim_num} (Day {target_day}) ---")
        print(f"{'Neighborhood':<30} {'Population':<12} {'Adoption Rate':<15} {'Mean Belief':<15}")
        print("-" * 80)
        
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
            
            name = neighborhood_names.get(nid, f'neighborhood_{nid}')
            neighborhood_stats.append({
                'neighborhood': name,
                'nid': nid,
                'population': len(n_data),
                'adoption_rate': adoption_rate,
                'mean_belief': mean_belief
            })
            
            print(f"{name:<30} {len(n_data):<12} {adoption_rate:<15.4f} {mean_belief:<15.4f}")
        
        # Summary statistics
        if neighborhood_stats:
            stats_df = pd.DataFrame(neighborhood_stats)
            print("\nSummary:")
            print(f"  Mean adoption rate: {stats_df['adoption_rate'].mean():.4f}")
            print(f"  Std adoption rate: {stats_df['adoption_rate'].std():.4f}")
            print(f"  Min adoption rate: {stats_df['adoption_rate'].min():.4f} ({stats_df.loc[stats_df['adoption_rate'].idxmin(), 'neighborhood']})")
            print(f"  Max adoption rate: {stats_df['adoption_rate'].max():.4f} ({stats_df.loc[stats_df['adoption_rate'].idxmax(), 'neighborhood']})")
            print(f"  Range: {stats_df['adoption_rate'].max() - stats_df['adoption_rate'].min():.4f}")
            
            # Check if differences are meaningful
            if stats_df['adoption_rate'].std() > 0.05:
                print("\n✓ Neighborhoods show meaningful differences in adoption rates!")
            else:
                print("\n⚠ Neighborhoods still show similar adoption rates (std < 0.05)")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python analyze_neighborhoods.py <config_path> <output_dir>")
        sys.exit(1)
    
    analyze_neighborhood_adoption(sys.argv[1], sys.argv[2])
