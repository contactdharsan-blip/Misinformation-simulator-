from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from sim.config import NetworkConfig, TownConfig, TraitConfig, WorldConfig
from sim.town.demographics import (
    Demographics,
    MediaDiet,
    Traits,
    Trust,
    generate_demographics,
    generate_media_diet,
    generate_traits,
    generate_trust,
    ideology_proxy,
)
from sim.town.networks import build_networks


@dataclass
class Town:
    n_agents: int
    neighborhoods: int
    neighborhood_coords: np.ndarray
    neighborhood_ids: np.ndarray
    household_ids: np.ndarray
    workplace_ids: np.ndarray
    school_ids: np.ndarray
    church_ids: np.ndarray
    demographics: Demographics
    traits: Traits
    trust: Trust
    media_diet: MediaDiet
    ideology: np.ndarray
    cultural_groups: np.ndarray  # Cultural group IDs (0=white, 1=hispanic, 2=black, 3=asian/other)
    networks: Dict[str, np.ndarray]
    aggregate_edges: Tuple[np.ndarray, np.ndarray, np.ndarray]
    neighbor_weight_sum: np.ndarray


def assign_groups(
    rng: np.random.Generator, n_agents: int, mean_size: float, std_size: float | None = None
) -> np.ndarray:
    if std_size is None:
        std_size = mean_size * 0.3
    sizes = np.maximum(1, rng.normal(loc=mean_size, scale=std_size, size=n_agents).astype(int))
    group_ids = np.empty(n_agents, dtype=np.int32)
    gid = 0
    idx = 0
    while idx < n_agents:
        size = int(np.clip(sizes[gid % len(sizes)], 1, n_agents - idx))
        group_ids[idx : idx + size] = gid
        gid += 1
        idx += size
    rng.shuffle(group_ids)
    return group_ids


def generate_town(
    rng: np.random.Generator,
    n_agents: int,
    town_cfg: TownConfig,
    trait_cfg: TraitConfig,
    world_cfg: WorldConfig,
    network_cfg: NetworkConfig,
) -> Town:
    """Create synthetic town demographics, traits, and multilayer networks."""
    # If explicit neighborhood specs are provided (city-specific), use those
    if getattr(town_cfg, "neighborhood_specs", None):
        specs = town_cfg.neighborhood_specs
        neighborhoods = len(specs)
        # Simple coords layout for specified neighborhoods
        coords = np.array([[i, 0] for i in range(neighborhoods)], dtype=np.float32)

        # assign agents to neighborhoods according to provided populations (if present)
        pops = [s.get("population", 1) for s in specs]
        total = float(sum(pops)) or 1.0
        probs = [p / total for p in pops]
        neighborhood_ids = rng.choice(np.arange(neighborhoods), size=n_agents, p=probs)
    else:
        # Optionally auto-scale number of neighborhoods based on population
        if getattr(town_cfg, "auto_scale_neighborhoods", False):
            target = max(1, int(getattr(town_cfg, "target_neighborhood_size", 400)))
            neighborhoods = max(1, int(round(n_agents / float(target))))
        else:
            neighborhoods = town_cfg.n_neighborhoods

        # derive a simple grid that fits the number of neighborhoods
        grid_rows, grid_cols = town_cfg.neighborhood_grid
        # if the configured grid is too small for computed neighborhoods, expand it
        if grid_rows * grid_cols < neighborhoods:
            import math

            grid_cols = int(math.ceil(math.sqrt(neighborhoods)))
            grid_rows = int(math.ceil(neighborhoods / float(grid_cols)))

        coords = np.array(
            [(r, c) for r in range(grid_rows) for c in range(grid_cols)], dtype=np.float32
        )[:neighborhoods]

        neighborhood_ids = rng.integers(0, neighborhoods, size=n_agents)
    household_ids = assign_groups(
        rng, n_agents, town_cfg.household_size_mean, town_cfg.household_size_std
    )
    workplace_ids = assign_groups(rng, n_agents, town_cfg.workplace_size_mean)
    school_ids = assign_groups(rng, n_agents, town_cfg.school_size_mean)

    church_ids = np.full(n_agents, -1, dtype=np.int32)
    attendees = np.where(rng.random(n_agents) < town_cfg.church_attendance_rate)[0]
    if attendees.size:
        assigned = assign_groups(rng, attendees.size, town_cfg.church_size_mean)
        church_ids[attendees] = assigned

    demographics = generate_demographics(rng, n_agents, town_cfg)
    ages = demographics.age
    
    # Assign ethnicity based on neighborhood demographics if available
    ethnicity = None
    if getattr(town_cfg, "neighborhood_specs", None) and len(neighborhood_ids) > 0:
        specs = town_cfg.neighborhood_specs
        ethnicity_labels = ['white', 'hispanic', 'black', 'asian', 'other']
        ethnicity = np.empty(n_agents, dtype=object)
        
        # Assign ethnicity per neighborhood (vectorized for efficiency)
        for neighborhood_idx in range(len(specs)):
            spec = specs[neighborhood_idx]
            eth_dist = spec.get("demographics", {}).get("ethnicity", {})
            if eth_dist:
                # Get agents in this neighborhood
                neighborhood_mask = neighborhood_ids == neighborhood_idx
                n_in_neighborhood = neighborhood_mask.sum()
                
                if n_in_neighborhood > 0:
                    # Sample ethnicity based on neighborhood distribution
                    eth_probs = np.array([eth_dist.get(eth, 0.0) for eth in ethnicity_labels], dtype=np.float32)
                    # Normalize probabilities
                    total = eth_probs.sum()
                    if total > 0:
                        eth_probs = eth_probs / total
                        # Sample ethnicity for all agents in this neighborhood at once
                        sampled_ethnicities = rng.choice(ethnicity_labels, size=n_in_neighborhood, p=eth_probs)
                        ethnicity[neighborhood_mask] = sampled_ethnicities
                    else:
                        ethnicity[neighborhood_mask] = 'white'  # Default
                else:
                    # No agents in this neighborhood, skip
                    pass
            else:
                # No ethnicity distribution, assign default
                neighborhood_mask = neighborhood_ids == neighborhood_idx
                ethnicity[neighborhood_mask] = 'white'
        
        # Fill any remaining agents with default
        mask = ethnicity == None  # noqa: E711
        if mask.any():
            ethnicity[mask] = 'white'
        
        # Update demographics with ethnicity
        demographics.ethnicity = ethnicity
    
    # Assign cultural groups based on neighborhood cultural composition
    cultural_groups = np.zeros(n_agents, dtype=np.int32)
    if getattr(town_cfg, "neighborhood_specs", None) and len(neighborhood_ids) > 0:
        specs = town_cfg.neighborhood_specs
        for neighborhood_idx in range(len(specs)):
            spec = specs[neighborhood_idx]
            cultural_comp = spec.get("cultural_composition", [0.25, 0.25, 0.25, 0.25])  # Default equal distribution
            if cultural_comp and len(cultural_comp) == 4:
                # Get agents in this neighborhood
                neighborhood_mask = neighborhood_ids == neighborhood_idx
                n_in_neighborhood = neighborhood_mask.sum()
                
                if n_in_neighborhood > 0:
                    # Normalize cultural composition probabilities
                    comp_probs = np.array(cultural_comp, dtype=np.float32)
                    comp_probs = comp_probs / comp_probs.sum()
                    
                    # Sample cultural groups for agents in this neighborhood
                    sampled_groups = rng.choice(4, size=n_in_neighborhood, p=comp_probs)
                    cultural_groups[neighborhood_mask] = sampled_groups
    # If no neighborhood specs or cultural composition not provided, assign based on ethnicity
    elif ethnicity is not None:
        # Map ethnicity to cultural groups
        ethnicity_to_group = {
            'white': 0,
            'hispanic': 1, 
            'black': 2,
            'asian': 3,
            'other': 3  # Asian/other combined
        }
        for i in range(n_agents):
            cultural_groups[i] = ethnicity_to_group.get(ethnicity[i], 0)
    
    # Extract neighborhood-specific parameters for trait/trust differentiation
    neighborhood_education = None
    neighborhood_income = None
    if getattr(town_cfg, "neighborhood_specs", None) and len(neighborhood_ids) > 0:
        specs = town_cfg.neighborhood_specs
        neighborhood_education = {}
        neighborhood_income = {}
        for neighborhood_idx in range(len(specs)):
            spec = specs[neighborhood_idx]
            demos = spec.get("demographics", {})
            # Extract education rate (college_educated fraction)
            edu_rate = demos.get("college_educated")
            if edu_rate is not None:
                neighborhood_education[neighborhood_idx] = float(edu_rate)
            # Extract median income
            income = demos.get("median_income")
            if income is not None:
                neighborhood_income[neighborhood_idx] = float(income)
    
    traits = generate_traits(
        rng, n_agents, trait_cfg, world_cfg.emotions_enabled, ages,
        neighborhood_ids=neighborhood_ids if getattr(town_cfg, "neighborhood_specs", None) else None,
        neighborhood_education=neighborhood_education,
        neighborhood_income=neighborhood_income,
    )
    trust = generate_trust(
        rng, n_agents, world_cfg,
        neighborhood_ids=neighborhood_ids if getattr(town_cfg, "neighborhood_specs", None) else None,
        neighborhood_income=neighborhood_income,
        neighborhood_education=neighborhood_education,
    )
    # Allow world-level media environment to influence media diet if provided
    media_env = getattr(world_cfg, "media_environment", None)
    media_diet = generate_media_diet(rng, n_agents, media_env)
    ideology = ideology_proxy(traits, trust)

    networks, aggregate_edges, neighbor_weight_sum = build_networks(
        rng,
        n_agents,
        neighborhood_ids,
        coords,
        household_ids,
        workplace_ids,
        school_ids,
        church_ids,
        ideology,
        network_cfg,
    )

    return Town(
        n_agents=n_agents,
        neighborhoods=neighborhoods,
        neighborhood_coords=coords,
        neighborhood_ids=neighborhood_ids,
        household_ids=household_ids,
        workplace_ids=workplace_ids,
        school_ids=school_ids,
        church_ids=church_ids,
        demographics=demographics,
        traits=traits,
        trust=trust,
        media_diet=media_diet,
        ideology=ideology,
        cultural_groups=cultural_groups,
        networks=networks,
        aggregate_edges=aggregate_edges,
        neighbor_weight_sum=neighbor_weight_sum,
    )
