from __future__ import annotations

from typing import List, Tuple

import torch

from sim.config import ModerationConfig, WorldConfig
from sim.disease.strains import Strain


def apply_moderation(
    share_probs_pos: torch.Tensor,
    share_probs_neg: torch.Tensor,
    strains: List[Strain],
    world_cfg: WorldConfig,
    moderation_cfg: ModerationConfig,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Apply moderation to sharing probabilities.
    
    Moderation suppressed positive shares (misinformation spread) but generally
    allows negative shares (debunking/warnings).
    """
    risk = torch.tensor(
        [s.violation_risk * (1 - s.stealth) for s in strains],
        device=share_probs_pos.device,
        dtype=share_probs_pos.dtype,
    )
    strictness = world_cfg.moderation_strictness
    downrank = 1 - moderation_cfg.downrank_effect * strictness * risk
    warning = moderation_cfg.warning_effect * strictness * risk

    adjusted_pos = share_probs_pos * downrank
    
    return (
        adjusted_pos.clamp(0.0, 1.0),
        share_probs_neg.clamp(0.0, 1.0),
        warning
    )
