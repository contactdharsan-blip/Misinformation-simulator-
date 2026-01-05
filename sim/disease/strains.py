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
    0: White/Anglo, 1: Hispanic/Latino, 2: Black/African American, 3: Asian/Other
    """
    name_lower = strain_name.lower()
    
    # White/Anglo targeting
    if any(k in name_lower for k in ['white_', 'anglo', 'conservative', 'patriot', 'traditional', 'economic_anxiety']):
        return 0
    # Hispanic/Latino targeting
    if any(k in name_lower for k in ['hispanic_', 'latino', 'immigration', 'border', 'family_values', 'catholic']):
        return 1
    # Black/African American targeting
    if any(k in name_lower for k in ['black_', 'systemic', 'justice', 'disparity', 'civil_rights', 'urban']):
        return 2
    # Asian/Other targeting
    if any(k in name_lower for k in ['asian_', 'model_minority', 'cultural_erosion', 'discrimination', 'foreign']):
        return 3
    
    return None

def cultural_matching_bonus(strains: List[Strain], cultural_groups: torch.Tensor, device: torch.device) -> torch.Tensor:
    """Calculate cultural matching bonus with stochastic differentiation."""
    n_agents = cultural_groups.shape[0]
    n_strains = len(strains)
    
    cultural_bonus_strength = 0.30
    group_identity_strength = torch.tensor([0.25, 0.35, 0.40, 0.30], device=device)
    
    matching = torch.zeros((n_agents, n_strains), device=device, dtype=torch.float32)
    
    # Add tiny stochastic noise per group/strain to avoid "exactly identical" results
    # even when there's no specific targeting (Identity variation)
    noise = torch.randn((4, n_strains), device=device) * 0.02
    
    for strain_idx, strain in enumerate(strains):
        target_group = strain_cultural_target(strain.name)
        
        # Base stochastic differentiation for everyone (background interest variation)
        for g in range(4):
            group_mask = (cultural_groups == g)
            if group_mask.any():
                matching[group_mask, strain_idx] += noise[g, strain_idx]
        
        if target_group is not None:
            target_mask = (cultural_groups == target_group)
            if target_mask.any():
                identity_factor = group_identity_strength[target_group]
                bonus = cultural_bonus_strength * identity_factor
                matching[target_mask, strain_idx] += bonus
    
    return torch.clamp(matching, -0.1, 0.5)


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
