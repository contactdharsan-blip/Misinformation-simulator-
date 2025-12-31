from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import torch

from sim.config import StrainConfig


@dataclass
class Strain:
    name: str
    topic: str
    memeticity: float
    emotional_profile: Dict[str, float]
    falsifiability: float
    stealth: float
    mutation_rate: float
    violation_risk: float
    is_true: bool = False
    # How contagious / likely people are to share this claim
    virality: float = 1.0
    # Persistence reduces per-step belief decay (0.0 = no effect)
    persistence: float = 0.0


def default_strains() -> List[Strain]:
    return [
        Strain(
            name="silver_river",
            topic="health_rumor",
            memeticity=0.55,
            emotional_profile={"fear": 0.6, "anger": 0.2, "hope": 0.2},
            falsifiability=0.7,
            stealth=0.4,
            mutation_rate=0.05,
            violation_risk=0.3,
            virality=1.0,
            persistence=0.0,
        ),
        Strain(
            name="market_shiver",
            topic="economic_panic",
            memeticity=0.6,
            emotional_profile={"fear": 0.5, "anger": 0.3, "hope": 0.2},
            falsifiability=0.6,
            stealth=0.45,
            mutation_rate=0.04,
            violation_risk=0.35,
        ),
        Strain(
            name="temple_echo",
            topic="moral_spiral",
            memeticity=0.5,
            emotional_profile={"fear": 0.3, "anger": 0.4, "hope": 0.3},
            falsifiability=0.5,
            stealth=0.55,
            mutation_rate=0.06,
            violation_risk=0.4,
        ),
        Strain(
            name="signal_fog",
            topic="tech_conspiracy",
            memeticity=0.58,
            emotional_profile={"fear": 0.2, "anger": 0.5, "hope": 0.3},
            falsifiability=0.65,
            stealth=0.5,
            mutation_rate=0.05,
            violation_risk=0.45,
        ),
        Strain(
            name="border_whisper",
            topic="outsider_threat",
            memeticity=0.62,
            emotional_profile={"fear": 0.4, "anger": 0.4, "hope": 0.2},
            falsifiability=0.55,
            stealth=0.5,
            mutation_rate=0.04,
            violation_risk=0.5,
            virality=1.0,
            persistence=0.0,
        ),
    ]


def strain_cultural_target(strain_name: str) -> int | None:
    """
    Determine which cultural group a strain targets based on its name.
    
    Returns:
        0: White/Anglo culture
        1: Hispanic/Latino culture  
        2: Black/African American culture
        3: Asian/Other culture
        None: No specific cultural targeting
    """
    name_lower = strain_name.lower()
    
    # White/Anglo targeting strains
    if any(keyword in name_lower for keyword in ['white_', 'anglo', 'conservative', 'patriot', 'traditional']):
        return 0
    
    # Hispanic/Latino targeting strains
    if any(keyword in name_lower for keyword in ['hispanic_', 'latino', 'immigration', 'border', 'family_values']):
        return 1
    
    # Black/African American targeting strains
    if any(keyword in name_lower for keyword in ['black_', 'systemic', 'justice', 'disparity']):
        return 2
    
    # Asian/Other targeting strains
    if any(keyword in name_lower for keyword in ['asian_', 'model_minority', 'cultural_erosion', 'discrimination']):
        return 3
    
    return None  # No specific cultural targeting


def cultural_matching_bonus(strains: List[Strain], cultural_groups: torch.Tensor, device: torch.device) -> torch.Tensor:
    """
    Calculate cultural matching bonus for belief updates.
    
    Agents receive a susceptibility bonus when exposed to strains that target their cultural group.
    
    Based on research showing identity-protective cognition increases susceptibility to 
    identity-relevant misinformation by 20-40% (Kahan et al., 2013; Pennycook et al., 2020).
    
    Parameters:
        strains: List of strain objects
        cultural_groups: Tensor of shape (n_agents,) with cultural group IDs
        device: Torch device
        
    Returns:
        Tensor of shape (n_agents, n_strains) with matching bonuses
    """
    n_agents = cultural_groups.shape[0]
    n_strains = len(strains)
    
    # Base cultural matching parameters from literature
    # Identity-relevant claims increase susceptibility by 25-35%
    cultural_bonus_strength = 0.30  # 30% increase in susceptibility
    
    # Different groups have different baseline identity strength
    # Based on research showing varying levels of identity salience across demographics
    group_identity_strength = torch.tensor([
        0.25,  # White/Anglo - moderate identity salience
        0.35,  # Hispanic/Latino - higher identity salience due to immigration experiences
        0.40,  # Black/African American - high identity salience due to historical discrimination
        0.30   # Asian/Other - moderate identity salience
    ], device=device)
    
    # Initialize matching matrix
    matching = torch.zeros((n_agents, n_strains), device=device, dtype=torch.float32)
    
    for strain_idx, strain in enumerate(strains):
        target_group = strain_cultural_target(strain.name)
        if target_group is not None:
            # Agents in the target group get the cultural bonus
            target_mask = (cultural_groups == target_group)
            if target_mask.any():
                # Apply identity strength modulation
                identity_factor = group_identity_strength[target_group]
                bonus = cultural_bonus_strength * identity_factor
                matching[target_mask, strain_idx] = bonus
    
    return matching


def load_strains(strain_cfgs: List[StrainConfig] | None) -> List[Strain]:
    if not strain_cfgs:
        return default_strains()
    strains = []
    for cfg in strain_cfgs:
        strains.append(
            Strain(
                name=cfg.name,
                topic=cfg.topic,
                memeticity=cfg.memeticity,
                emotional_profile=cfg.emotional_profile,
                falsifiability=cfg.falsifiability,
                stealth=cfg.stealth,
                mutation_rate=cfg.mutation_rate,
                violation_risk=cfg.violation_risk,
                is_true=getattr(cfg, "is_true", False),
                virality=getattr(cfg, "virality", 1.0),
                persistence=getattr(cfg, "persistence", 0.0),
            )
        )
    return strains


def mutate_strains(strains: List[Strain], rng) -> List[Strain]:
    mutated = []
    for strain in strains:
        if rng.random() < strain.mutation_rate:
            stealth = min(1.0, max(0.0, strain.stealth + rng.normal(0, 0.05)))
            falsifiability = min(1.0, max(0.1, strain.falsifiability - rng.normal(0, 0.03)))
            mutated.append(
                Strain(
                    name=strain.name + "_m",
                    topic=strain.topic,
                    memeticity=strain.memeticity,
                    emotional_profile=strain.emotional_profile,
                    falsifiability=falsifiability,
                    stealth=stealth,
                    mutation_rate=strain.mutation_rate,
                    violation_risk=strain.violation_risk,
                    virality=strain.virality,
                    persistence=strain.persistence,
                )
            )
        else:
            mutated.append(strain)
    return mutated
