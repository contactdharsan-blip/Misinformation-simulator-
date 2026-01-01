from __future__ import annotations

from typing import Dict, List

import torch

from sim.config import SharingConfig, WorldConfig
from sim.disease.strains import Strain


def compute_share_probabilities(
    beliefs: torch.Tensor,
    traits: Dict[str, torch.Tensor],
    emotions: Dict[str, torch.Tensor],
    sharing_cfg: SharingConfig,
    world_cfg: WorldConfig,
    strains: List[Strain],
    ages: torch.Tensor | None = None,
) -> torch.Tensor:
    """Compute per-agent share probabilities for each claim.
    
    Based on Guess et al. (2019): Older adults (65+) share 7x more than young adults.
    """
    base = torch.full_like(beliefs, fill_value=sharing_cfg.base_share_rate)
    logit = torch.log(base / (1 - base))

    logit = logit + sharing_cfg.belief_sensitivity * (beliefs - 0.5)
    logit = logit + sharing_cfg.status_sensitivity * traits["status_seeking"].unsqueeze(1)
    logit = logit + sharing_cfg.conformity_sensitivity * traits["conformity"].unsqueeze(1)
    
    # Age-based sharing multiplier (Guess et al., 2019: 65+ share 7x more than 18-29)
    if ages is not None:
        # Create age multipliers: 65+ = 7x, 55-64 = 4x, 35-54 = 2x, 18-34 = 1x, <18 = 0.5x
        age_multiplier = torch.ones_like(ages, dtype=beliefs.dtype)
        age_multiplier[ages < 18] = 0.5  # Children share less
        age_multiplier[(ages >= 18) & (ages < 35)] = 1.0  # Young adults baseline
        age_multiplier[(ages >= 35) & (ages < 55)] = 2.0  # Middle-aged
        age_multiplier[(ages >= 55) & (ages < 65)] = 4.0  # Older adults
        age_multiplier[ages >= 65] = 7.0  # Seniors (65+) share 7x more (Guess et al., 2019)
        # Apply age multiplier to logit scale (additive on logit = multiplicative on probability)
        logit = logit + torch.log(age_multiplier).unsqueeze(1)

    if emotions:
        fear = emotions["fear"].unsqueeze(1)
        anger = emotions["anger"].unsqueeze(1)
        hope = emotions["hope"].unsqueeze(1)
        weights = torch.tensor(
            [[s.emotional_profile.get("fear", 0.0),
              s.emotional_profile.get("anger", 0.0),
              s.emotional_profile.get("hope", 0.0)] for s in strains],
            device=beliefs.device,
            dtype=beliefs.dtype,
        )
        emotion_score = fear * weights[:, 0] + anger * weights[:, 1] + hope * weights[:, 2]
        logit = logit + sharing_cfg.emotion_sensitivity * emotion_score

    violation = torch.tensor([s.violation_risk for s in strains], device=beliefs.device, dtype=beliefs.dtype)
    moderation_penalty = sharing_cfg.moderation_risk_sensitivity * violation * world_cfg.moderation_strictness
    logit = logit - moderation_penalty
    logit = logit - world_cfg.platform_friction

    probs = torch.sigmoid(logit)
    # Apply per-strain virality multiplier (allows truth to spread slower)
    virality = torch.tensor([s.virality for s in strains], device=beliefs.device, dtype=beliefs.dtype)
    probs = probs * virality.unsqueeze(0)
    return torch.clamp(probs, 0.0, 1.0)

