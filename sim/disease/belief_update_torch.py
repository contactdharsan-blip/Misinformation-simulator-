from __future__ import annotations

from typing import Tuple

import torch

from sim.config import BeliefUpdateConfig


def update_beliefs(
    beliefs: torch.Tensor,
    exposure: torch.Tensor,
    trust_signal: torch.Tensor,
    social_proof: torch.Tensor,
    debunk_pressure: torch.Tensor,
    skepticism: torch.Tensor,
    match: torch.Tensor,
    exposure_memory: torch.Tensor,
    baseline: torch.Tensor,
    cfg: BeliefUpdateConfig,
    reactance_enabled: bool,
    reactance: torch.Tensor,
    strains: list | None = None,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Vectorized belief update with decay, repetition, and corrections."""
    exposure_memory = cfg.exposure_memory_decay * exposure_memory + (1 - cfg.exposure_memory_decay) * exposure

    p = torch.sigmoid(
        cfg.alpha * exposure_memory
        + cfg.beta * trust_signal
        + cfg.gamma * match
        + cfg.delta * social_proof
        - cfg.lambda_skepticism * skepticism.unsqueeze(1)
        - cfg.mu_debunk * debunk_pressure
    )

    correction = debunk_pressure
    if reactance_enabled:
        correction = correction * (1 - cfg.reactance_strength * reactance.unsqueeze(1))

    beliefs = beliefs + cfg.eta * p * (1 - beliefs) - cfg.rho * correction
    # Apply per-strain persistence-adjusted decay if strains provided,
    # otherwise fall back to global decay.
    if strains is not None:
        persistence = torch.tensor([getattr(s, "persistence", 0.0) for s in strains], device=beliefs.device, dtype=beliefs.dtype)
        decay_vec = cfg.belief_decay * (1.0 - persistence)
        beliefs = beliefs + decay_vec.unsqueeze(0) * (baseline - beliefs)
    else:
        beliefs = beliefs + cfg.belief_decay * (baseline - beliefs)
    beliefs = torch.clamp(beliefs, 0.0, 1.0)

    # CRITICAL: Check for truth conversion FIRST, before mutual exclusion
    # If someone has truth belief >= threshold, they convert to truth regardless of misinformation belief
    # This allows truth to convert misinformation believers over time
    protected_mask = torch.zeros(beliefs.shape[0], dtype=torch.bool, device=beliefs.device)
    if strains is not None and beliefs.shape[1] > 1:
        try:
            thresh = getattr(cfg, "truth_protection_threshold", None)
            if thresh is not None:
                truth_mask = torch.tensor([getattr(s, "is_true", False) for s in strains], device=beliefs.device, dtype=torch.bool)
                if truth_mask.any():
                    true_beliefs = beliefs[:, truth_mask]
                    max_true, arg = torch.max(true_beliefs, dim=1)
                    # Anyone with truth belief >= threshold converts to truth (even if they have misinformation)
                    protected = max_true >= float(thresh)
                    protected_mask = protected.clone()
                    if protected.any():
                        # For agents converting to truth, zero out ALL non-truth beliefs
                        non_truth_mask = ~truth_mask
                        indices = torch.nonzero(protected).squeeze(1)
                        if non_truth_mask.any() and len(indices) > 0:
                            beliefs[indices[:, None], non_truth_mask.unsqueeze(0).expand(len(indices), -1)] = 0.0
                        # Keep their truth belief value
                        truth_idx = torch.nonzero(truth_mask).squeeze(1)
                        if len(truth_idx) > 0:
                            chosen = truth_idx[arg[protected]]
                            beliefs[indices, chosen] = max_true[protected]
        except Exception:
            # be conservative on failures: skip protection
            pass

    # Optional hard mutual exclusion: keep only the strongest-belief claim per agent
    # IMPORTANT: Mutual exclusion does NOT apply to truth - truth can coexist or convert misinformation
    # Only apply mutual exclusion between non-truth claims, or if truth is not present
    if getattr(cfg, "mutual_exclusion_hard", False) and beliefs.shape[1] > 1:
        # Apply mutual exclusion only to non-protected agents
        non_protected = ~protected_mask
        if non_protected.any() and non_protected.sum() > 0:
            non_protected_indices = torch.nonzero(non_protected).squeeze(1)
            non_protected_beliefs = beliefs[non_protected_indices]
            
            if strains is not None:
                truth_mask = torch.tensor([getattr(s, "is_true", False) for s in strains], device=beliefs.device, dtype=torch.bool)
                if truth_mask.any():
                    # For non-protected agents, apply mutual exclusion ONLY to non-truth claims
                    # Truth beliefs are preserved and can continue to grow
                    non_truth_mask = ~truth_mask
                    if non_truth_mask.sum() > 1:  # Only if there are multiple non-truth claims
                        # Get non-truth beliefs for these agents
                        non_truth_beliefs = non_protected_beliefs[:, non_truth_mask]
                        # Find strongest non-truth belief per agent
                        max_non_truth_idx = torch.argmax(non_truth_beliefs, dim=1)
                        # Create mask to keep only strongest non-truth belief
                        non_truth_mask_tensor = torch.zeros_like(non_truth_beliefs)
                        non_truth_mask_tensor[torch.arange(non_truth_beliefs.shape[0]), max_non_truth_idx] = 1.0
                        # Apply mask to zero out weaker non-truth beliefs
                        non_protected_beliefs[:, non_truth_mask] = non_truth_beliefs * non_truth_mask_tensor
                    elif non_truth_mask.sum() == 1:
                        # Only one non-truth claim, no need for mutual exclusion
                        pass
                    # Truth beliefs are left unchanged - they can coexist and grow
                else:
                    # No truth claims, apply standard mutual exclusion to all claims
                    max_idx = torch.argmax(non_protected_beliefs, dim=1)
                    mask = torch.zeros_like(non_protected_beliefs)
                    mask[torch.arange(non_protected_beliefs.shape[0]), max_idx] = 1.0
                    non_protected_beliefs = non_protected_beliefs * mask
            else:
                # No strain info, apply standard mutual exclusion
                max_idx = torch.argmax(non_protected_beliefs, dim=1)
                mask = torch.zeros_like(non_protected_beliefs)
                mask[torch.arange(non_protected_beliefs.shape[0]), max_idx] = 1.0
                non_protected_beliefs = non_protected_beliefs * mask
            
            beliefs[non_protected_indices] = non_protected_beliefs

    return beliefs, exposure_memory
