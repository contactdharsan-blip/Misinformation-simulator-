from __future__ import annotations

from typing import Dict, List, Tuple

import torch

from sim.config import SharingConfig, WorldConfig, SEDPNRConfig
from sim.disease.strains import Strain


def compute_share_probabilities(
    beliefs: torch.Tensor,
    traits: Dict[str, torch.Tensor],
    emotions: Dict[str, torch.Tensor],
    sharing_cfg: SharingConfig,
    world_cfg: WorldConfig,
    strains: List[Strain],
    sedpnr_cfg: SEDPNRConfig,
    exposed_mask: torch.Tensor,
    doubtful_mask: torch.Tensor,
    ages: torch.Tensor | None = None,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Compute per-agent share probabilities for each claim.
    
    Returns:
        (prob_positive, prob_negative): Dual-channel sharing probabilities.
    """
    base = torch.full_like(beliefs, fill_value=sharing_cfg.base_share_rate)
    
    # Positive sharing (believing and spreading)
    logit_pos = torch.log(base / (1 - base))
    logit_pos = logit_pos + sharing_cfg.belief_sensitivity * (beliefs - 0.5)

    # Negative sharing (debunking, criticizing, or warning)
    # Driven by skepticism and low belief
    logit_neg = torch.log(base / (1 - base))
    logit_neg = logit_neg + sharing_cfg.belief_sensitivity * (0.5 - beliefs)
    logit_neg = logit_neg + 2.0 * traits["skepticism"].unsqueeze(1)
    logit_pos = logit_pos + sharing_cfg.status_sensitivity * traits["status_seeking"].unsqueeze(1)
    logit_pos = logit_pos + sharing_cfg.conformity_sensitivity * traits["conformity"].unsqueeze(1)
    
    logit_neg = logit_neg + sharing_cfg.status_sensitivity * traits["status_seeking"].unsqueeze(1)
    
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
        logit_pos = logit_pos + torch.log(age_multiplier).unsqueeze(1)
        logit_neg = logit_neg + torch.log(age_multiplier).unsqueeze(1)

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
        logit_pos = logit_pos + sharing_cfg.emotion_sensitivity * emotion_score
        
        # Negative sharing is also driven by anger/fear (outrage at the rumor)
        logit_neg = logit_neg + sharing_cfg.emotion_sensitivity * (fear * 0.5 + anger * 0.8)

    violation = torch.tensor([s.violation_risk for s in strains], device=beliefs.device, dtype=beliefs.dtype)
    moderation_penalty = sharing_cfg.moderation_risk_sensitivity * violation * world_cfg.moderation_strictness
    logit_pos = logit_pos - moderation_penalty
    logit_pos = logit_pos - world_cfg.platform_friction
    
    logit_neg = logit_neg - world_cfg.platform_friction

    probs_pos = torch.sigmoid(logit_pos)
    probs_neg = torch.sigmoid(logit_neg)
    
    # Apply per-strain virality multiplier
    virality = torch.tensor([s.virality for s in strains], device=beliefs.device, dtype=beliefs.dtype)
    probs_pos = probs_pos * virality.unsqueeze(0)
    probs_neg = probs_neg * (0.5 + 0.5 * virality.unsqueeze(0))
    
    # SEDPNR Beta Scaling (Transitions E -> P/N and D -> P/N)
    # Only Exposed or Doubtful agents share
    # beta_pos_e, beta_neg_e for Exposed
    # beta_pos_d, beta_neg_d for Doubtful
    
    # Initialize combined beta masks
    beta_pos = torch.zeros_like(probs_pos)
    beta_neg = torch.zeros_like(probs_neg)
    
    # Exposed agents
    beta_pos = torch.where(exposed_mask, sedpnr_cfg.beta_pos_e, beta_pos)
    beta_neg = torch.where(exposed_mask, sedpnr_cfg.beta_neg_e, beta_neg)
    
    # Doubtful agents (Doubtful mask overrides Exposed mask as it's a more specific state)
    beta_pos = torch.where(doubtful_mask, sedpnr_cfg.beta_pos_d, beta_pos)
    beta_neg = torch.where(doubtful_mask, sedpnr_cfg.beta_neg_d, beta_neg)
    
    # Apply beta scaling
    probs_pos = probs_pos * beta_pos
    probs_neg = probs_neg * beta_neg
    
    return torch.clamp(probs_pos, 0.0, 1.0), torch.clamp(probs_neg, 0.0, 1.0)

