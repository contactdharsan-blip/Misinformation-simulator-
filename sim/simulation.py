from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import torch

from sim.config import MetricsConfig, SimulationConfig
from sim.disease.belief_update_torch import update_beliefs
from sim.disease.strains import cultural_matching_bonus
from sim.disease.exposure import (
    compute_institution_exposure,
    compute_social_exposure,
    compute_social_proof,
)
from sim.cognition.dual_process import (
    initialize_cognitive_states,
    compute_processing_mode,
    update_doubtful_state,
    update_cognitive_load,
    update_familiarity,
)
from sim.disease.sharing import compute_share_probabilities
from sim.disease.operator import load_operator
from sim.disease.strains import load_strains, mutate_strains
from sim.io.metadata import build_run_metadata
from sim.io.plots import (
    plot_adoption_by_age,
    plot_adoption_by_ethnicity,
    plot_adoption_curves,
    plot_belief_histogram,
    plot_polarization,
)
from sim.io.snapshot import collect_snapshot
from sim.metrics.metrics import compute_daily_metrics, compute_daily_metrics_torch
from sim.rng import RNGManager
from sim.town.generator import generate_town
from sim.world.institutions import update_trust
from sim.world.media import feed_injection
from sim.world.moderation import apply_moderation


@dataclass
class SimulationOutputs:
    metrics: pd.DataFrame
    snapshots: pd.DataFrame
    summary: Dict[str, float]


def resolve_device(device: str) -> torch.device:
    if device == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(device)


def claim_alignment(strains) -> List[float]:
    mapping = {
        "health_rumor": 0.5,
        "economic_panic": 0.55,
        "moral_spiral": 0.7,
        "tech_conspiracy": 0.6,
        "outsider_threat": 0.8,
    }
    return [mapping.get(s.topic, 0.55) for s in strains]


def detect_communities(
    src_idx: np.ndarray, dst_idx: np.ndarray, n_agents: int, cfg: MetricsConfig
) -> np.ndarray | None:
    if cfg.community_backend == "none" or n_agents > cfg.community_max_nodes:
        return None

    backend = cfg.community_backend
    if backend in ("auto", "igraph"):
        try:
            import igraph as ig

            graph = ig.Graph(n=n_agents, edges=list(zip(src_idx.tolist(), dst_idx.tolist())), directed=False)
            communities = graph.community_multilevel()
            return np.array(communities.membership, dtype=np.int32)
        except Exception:
            if backend == "igraph":
                return None

    try:
        import networkx as nx

        graph = nx.Graph()
        graph.add_nodes_from(range(n_agents))
        graph.add_edges_from(zip(src_idx.tolist(), dst_idx.tolist()))
        communities = nx.algorithms.community.greedy_modularity_communities(graph)
        labels = np.zeros(n_agents, dtype=np.int32)
        for cid, members in enumerate(communities):
            for node in members:
                labels[node] = cid
        return labels
    except Exception:
        return None


def run_simulation(cfg: SimulationConfig, out_dir: str | Path) -> SimulationOutputs:
    """Run the contagion simulation and write outputs to disk."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    device = resolve_device(cfg.sim.device)
    rng_manager = RNGManager(cfg.sim.seed, cfg.sim.deterministic)

    strains = load_strains(cfg.strains)
    if cfg.sim.n_claims and cfg.sim.n_claims != len(strains):
        if cfg.sim.n_claims < len(strains):
            strains = strains[: cfg.sim.n_claims]
        else:
            strains = strains + strains[: cfg.sim.n_claims - len(strains)]
    n_claims = len(strains)
    n_agents = cfg.sim.n_agents
    operator = load_operator(cfg.world.operator_enabled)

    metadata = build_run_metadata(cfg, device)
    with (out_dir / "run_metadata.json").open("w") as f:
        json.dump(metadata, f, indent=2)

    town = generate_town(
        rng_manager.numpy,
        n_agents,
        cfg.town,
        cfg.traits,
        cfg.world,
        cfg.network,
    )

    beliefs = torch.full(
        (n_agents, n_claims),
        fill_value=cfg.belief_update.baseline_belief,
        dtype=torch.float32,
        device=device,
    )
    seed_frac = cfg.sim.seed_fraction
    all_seeds = []
    for k in range(n_claims):
        seeds = rng_manager.numpy.choice(n_agents, size=max(1, int(seed_frac * n_agents)), replace=False)
        beliefs[seeds, k] = 0.85
        all_seeds.append(seeds)

    baseline = torch.full_like(beliefs, fill_value=cfg.belief_update.baseline_belief)
    exposure_memory = torch.zeros_like(beliefs)
    
    # Track SEDPNR states
    # E (Exposed): Individuals who met the trending misinformation
    exposed_mask = torch.zeros_like(beliefs, dtype=torch.bool)
    for k, seeds in enumerate(all_seeds):
        exposed_mask[seeds, k] = True
        
    # D (Doubtful): In cog_state.is_doubtful
    # R (Restrained): Individuals who lost interest in spreading
    share_count = torch.zeros_like(beliefs)
    restrained_mask = torch.zeros_like(beliefs, dtype=torch.bool)
    
    # Track which agents have ever adopted truth (for persistent protection)
    truth_adopters_mask = torch.zeros(n_agents, dtype=torch.bool, device=device)

    src_idx, dst_idx, weights = town.aggregate_edges
    edge_tensors = (
        torch.tensor(src_idx, device=device, dtype=torch.int64),
        torch.tensor(dst_idx, device=device, dtype=torch.int64),
        torch.tensor(weights, device=device, dtype=torch.float32),
    )
    neighbor_weight_sum = torch.tensor(town.neighbor_weight_sum, device=device, dtype=torch.float32)

    traits = {
        "skepticism": torch.tensor(town.traits.skepticism, device=device),
        "conformity": torch.tensor(town.traits.conformity, device=device),
        "status_seeking": torch.tensor(town.traits.status_seeking, device=device),
        "conflict_tolerance": torch.tensor(town.traits.conflict_tolerance, device=device),
    }

    emotions = {}
    if cfg.world.emotions_enabled and town.traits.emotions:
        emotions = {k: torch.tensor(v, device=device) for k, v in town.traits.emotions.items()}

    # Initialize cognitive states for dual-process architecture
    cog_state = initialize_cognitive_states(
        n_agents, n_claims, traits, cfg.dual_process, device
    )

    trust = {
        "trust_gov": torch.tensor(town.trust.trust_gov, device=device),
        "trust_church": torch.tensor(town.trust.trust_church, device=device),
        "trust_local_news": torch.tensor(town.trust.trust_local_news, device=device),
        "trust_national_news": torch.tensor(town.trust.trust_national_news, device=device),
        "trust_friends": torch.tensor(town.trust.trust_friends, device=device),
        "trust_outgroups": torch.tensor(town.trust.trust_outgroups, device=device),
    }
    media_diet = torch.tensor(town.media_diet.weights, device=device)

    ideology = torch.tensor(town.ideology, device=device)
    alignment_targets = torch.tensor(claim_alignment(strains), device=device)
    match = 1 - torch.abs(ideology.unsqueeze(1) - alignment_targets.unsqueeze(0))

    # Pre-compute ages_tensor for sharing probabilities
    ages_tensor = torch.tensor(town.demographics.age, device=device, dtype=torch.float32)

    adoption_threshold = cfg.sim.adoption_threshold
    communities = detect_communities(src_idx, dst_idx, n_agents, cfg.metrics)
    if communities is None:
        if cfg.metrics.include_neighborhood_clusters:
            combined_clusters = town.neighborhood_ids
        else:
            combined_clusters = np.arange(n_agents, dtype=np.int32)
    else:
        if cfg.metrics.include_neighborhood_clusters:
            combined_clusters = town.neighborhood_ids * 1000 + communities
        else:
            combined_clusters = communities
    if not cfg.metrics.cluster_penetration_enabled:
        combined_clusters = None
    cluster_sizes = pd.DataFrame(
        {
            "cluster_id": combined_clusters,
            "neighborhood_id": town.neighborhood_ids,
        }
    )
    cluster_summary = (
        cluster_sizes.groupby("cluster_id")
        .agg(size=("cluster_id", "count"), neighborhood_id=("neighborhood_id", "first"))
        .reset_index()
    )
    cluster_summary.to_csv(out_dir / "community_sizes.csv", index=False)

    metrics_rows: List[Dict[str, float]] = []
    snapshots: List[pd.DataFrame] = []
    prev_beliefs = beliefs.clone()
    prev_new_adopters = torch.zeros(n_claims, device=device, dtype=beliefs.dtype)

    if device.type == "cuda":
        torch.set_float32_matmul_precision("high")
        if cfg.sim.use_tf32:
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True

    prev_grad = torch.is_grad_enabled()
    torch.set_grad_enabled(False)
    for day in range(cfg.sim.n_steps):
        strains = mutate_strains(strains, rng_manager.numpy)

        world_effective = cfg.world
        if cfg.world.intervention_day is not None and day >= cfg.world.intervention_day:
            world_effective = cfg.world.model_copy()
            if cfg.world.intervention_type == "moderation":
                world_effective.moderation_strictness = min(
                    1.0, cfg.world.moderation_strictness * (1 + cfg.world.intervention_strength)
                )
            elif cfg.world.intervention_type == "debunk":
                world_effective.debunk_intensity = min(
                    1.0, cfg.world.debunk_intensity * (1 + cfg.world.intervention_strength)
                )

        # Apply sharing fatigue (restrained state)
        # Reducing share probability for agents who have shared too much
        restrained_penalty = torch.where(restrained_mask, 0.1, 1.0)
        
        share_probs_pos, share_probs_neg = compute_share_probabilities(
            beliefs, traits, emotions, cfg.sharing, world_effective, strains, 
            sedpnr_cfg=cfg.sedpnr, exposed_mask=exposed_mask, doubtful_mask=cog_state.is_doubtful, ages=ages_tensor
        )
        share_probs_pos = share_probs_pos * restrained_penalty
        # Negative sharing also fatigues but perhaps slower
        share_probs_neg = share_probs_neg * (0.5 + 0.5 * restrained_penalty)

        share_probs_pos, share_probs_neg, warnings = apply_moderation(
            share_probs_pos, share_probs_neg, strains, world_effective, cfg.moderation
        )

        shares_pos = torch.bernoulli(share_probs_pos, generator=rng_manager.torch(device))
        shares_neg = torch.bernoulli(share_probs_neg, generator=rng_manager.torch(device))
        
        # Total shares for exposure calculation
        shares = shares_pos + shares_neg
        
        # Update share counts and restrained state (SEDPNR lambda transition)
        share_count = share_count + shares_pos + 0.5 * shares_neg
        
        # P/N -> R (lambda_p, lambda_n): Probabilistic transition to Restrained state
        lambda_p_mask = (shares_pos > 0.5) & (~restrained_mask) & (torch.rand(restrained_mask.shape, device=device) < cfg.sedpnr.lambda_p)
        lambda_n_mask = (shares_neg > 0.5) & (~restrained_mask) & (torch.rand(restrained_mask.shape, device=device) < cfg.sedpnr.lambda_n)
        
        # Agents become 'Restrained' either via lambda probability or threshold fatigue
        restrained_mask = restrained_mask | (share_count >= 3.0) | lambda_p_mask | lambda_n_mask

        social_exposure = compute_social_exposure(shares, edge_tensors, n_agents)
        social_proof = compute_social_proof(
            beliefs, edge_tensors, neighbor_weight_sum, cfg.belief_update.social_proof_threshold
        )

        institution_exposure, debunk_pressure = compute_institution_exposure(
            media_diet, trust, strains, world_effective
        )
        feed_exposure = feed_injection(media_diet, strains, world_effective)

        total_exposure = social_exposure + institution_exposure + feed_exposure
        
        # Transition S -> E (alpha): Only some people with exposure actually enter 'Exposed' state
        # In SEDPNR, this represents individuals who 'met' the misinformation but didn't critically assess it
        new_exposure = (total_exposure > 1e-4) & (~exposed_mask) & (~restrained_mask)
        if new_exposure.any():
            alpha_mask = torch.rand(new_exposure.shape, device=device) < cfg.sedpnr.alpha
            exposed_mask = exposed_mask | (new_exposure & alpha_mask)

        # Transition E -> D (gamma): Exposed individuals move to Doubtful state
        e_to_d_mask = exposed_mask & (~cog_state.is_doubtful) & (torch.rand(exposed_mask.shape, device=device) < cfg.sedpnr.gamma)
        cog_state.is_doubtful = cog_state.is_doubtful | e_to_d_mask

        # Recovery Transitions (mu_e, mu_d): Returning to Susceptible state
        # This occurs due to interest loss or fact-checking reinforcement
        mu_e_mask = exposed_mask & (torch.rand(exposed_mask.shape, device=device) < cfg.sedpnr.mu_e)
        exposed_mask = exposed_mask & (~mu_e_mask)
        
        mu_d_mask = cog_state.is_doubtful & (torch.rand(exposed_mask.shape, device=device) < cfg.sedpnr.mu_d)
        cog_state.is_doubtful = cog_state.is_doubtful & (~mu_d_mask)

        total_exposure = operator.apply(total_exposure)

        inst_trust = (
            trust["trust_gov"]
            + trust["trust_church"]
            + trust["trust_local_news"]
            + trust["trust_national_news"]
        ) / 4.0
        trust_signal = (
            social_exposure * trust["trust_friends"].unsqueeze(1)
            + institution_exposure * inst_trust.unsqueeze(1)
            + feed_exposure * trust["trust_friends"].unsqueeze(1)
        )
        denom = total_exposure + 1e-6
        trust_signal = trust_signal / denom

        debunk_pressure = debunk_pressure + warnings.unsqueeze(0) * (
            0.5 + traits["skepticism"].unsqueeze(1)
        ) * trust["trust_local_news"].unsqueeze(1)

        # Calculate cultural matching bonus for identity-relevant strains
        cultural_match = None
        if strains is not None and hasattr(town, 'cultural_groups'):
            cultural_groups_tensor = torch.tensor(town.cultural_groups, device=device, dtype=torch.long)
            cultural_match = cultural_matching_bonus(strains, cultural_groups_tensor, device)

        # Update cognitive states before belief update
        update_doubtful_state(cog_state, beliefs, cfg.dual_process)
        update_familiarity(cog_state, total_exposure, cfg.dual_process)
        
        # Determine processing mode (S1 vs S2)
        # Identity threat here is approximated by ideological mismatch
        identity_threat = 1.0 - match
        processing_mode = compute_processing_mode(
            cog_state, total_exposure, identity_threat, cfg.dual_process
        )

        beliefs, exposure_memory = update_beliefs(
            beliefs,
            total_exposure,
            trust_signal,
            social_proof,
            debunk_pressure,
            traits["skepticism"],
            match,
            exposure_memory,
            baseline,
            cfg.belief_update,
            world_effective.reactance_enabled,
            traits["conflict_tolerance"],
            strains,
            cultural_match,
            processing_mode=processing_mode,
        )
        
        # Track agents who have adopted truth (belief >= threshold)
        # Truth protection: gradually reduce misinformation beliefs (not instant zeroing)
        # This allows for more realistic spread patterns and misinformation retention
        if strains is not None:
            truth_mask = torch.tensor([getattr(s, "is_true", False) for s in strains], device=device, dtype=torch.bool)
            if truth_mask.any():
                true_beliefs = beliefs[:, truth_mask]
                max_true = torch.max(true_beliefs, dim=1)[0]
                new_truth_adopters = (max_true >= cfg.sim.adoption_threshold) & ~truth_adopters_mask
                truth_adopters_mask = truth_adopters_mask | new_truth_adopters
                
                # For agents who have adopted truth, gradually decay misinformation beliefs
                # Decay rate: 0.15 per day (reduces misinformation by 15% per day, not instant zero)
                if truth_adopters_mask.any():
                    non_truth_mask = ~truth_mask
                    if non_truth_mask.any():
                        truth_adopter_indices = torch.nonzero(truth_adopters_mask).squeeze(1)
                        if len(truth_adopter_indices) > 0:
                            non_truth_cols = torch.nonzero(non_truth_mask).squeeze(1)
                            # Gradual decay: multiply by 0.92 per day (8% reduction)
                            # This allows misinformation to persist longer, creating more realistic retention
                            decay_rate = 0.92  # 8% reduction per day (slower decay)
                            beliefs[truth_adopter_indices[:, None], non_truth_cols.unsqueeze(0).expand(len(truth_adopter_indices), -1)] *= decay_rate

        # Update cognitive load based on processing intensity
        update_cognitive_load(cog_state, total_exposure)
        
        trust = update_trust(trust, beliefs, debunk_pressure, world_effective)

        # Save snapshots at intervals, day 0, 25, and the final day
        snapshot_interval = getattr(cfg.sim, "snapshot_interval", 30)
        is_final_day = (day == cfg.sim.n_steps - 1)
        should_snapshot = (
            cfg.output.save_snapshots 
            and (day == 0 or day == 25 or (day + 1) % snapshot_interval == 0 or is_final_day)
        )
        if should_snapshot:
            belief_cpu = beliefs.detach().cpu().numpy()
            frame = pd.DataFrame(belief_cpu, columns=[f"claim_{i}" for i in range(n_claims)])
            frame.insert(0, "agent_id", np.arange(n_agents))
            collect_snapshot(snapshots, day, frame)

        if cfg.metrics.use_gpu_metrics:
            daily_metrics, prev_new_adopters = compute_daily_metrics_torch(
                day,
                beliefs,
                prev_beliefs,
                trust,
                adoption_threshold,
                combined_clusters,
                prev_new_adopters,
                cfg.metrics.cluster_penetration_enabled,
            )
        else:
            belief_cpu = beliefs.detach().cpu().numpy()
            prev_cpu = prev_beliefs.detach().cpu().numpy()
            trust_cpu = {k: v.detach().cpu().numpy() for k, v in trust.items()}
            daily_metrics, prev_new_adopters_cpu = compute_daily_metrics(
                day,
                belief_cpu,
                prev_cpu,
                trust_cpu,
                adoption_threshold,
                combined_clusters,
                prev_new_adopters.detach().cpu().numpy(),
                cfg.metrics.cluster_penetration_enabled,
            )
            prev_new_adopters = torch.tensor(prev_new_adopters_cpu, device=device, dtype=beliefs.dtype)
        metrics_rows.extend(daily_metrics)
        prev_beliefs = beliefs.clone()

    torch.set_grad_enabled(prev_grad)

    metrics_df = pd.DataFrame(metrics_rows)
    snapshots_df = pd.concat(snapshots, ignore_index=True) if snapshots else pd.DataFrame()

    summary = build_summary(metrics_df, cfg.sim.n_steps, cfg.world.intervention_day)

    # Track strain names for plotting (initial strains, mutations tracked separately)
    initial_strain_names = [s.name for s in load_strains(cfg.strains)[:n_claims]]
    
    # Save strain information for reference
    strain_info = {
        "initial_strains": initial_strain_names,
        "note": "Mutations create new strains but are not tracked as separate claims due to fixed tensor size"
    }
    with (out_dir / "strain_info.json").open("w") as f:
        json.dump(strain_info, f, indent=2)

    if cfg.output.save_plots:
        plots_dir = out_dir / "plots"
        plots_dir.mkdir(exist_ok=True)
        
        # Target day for all plots: use the actual max day reached
        target_day = int(metrics_df["day"].max())
        
        # Filter metrics to target_day
        metrics_filtered = metrics_df[metrics_df["day"] <= target_day].copy()
        
        # Generate all plots up to target_day
        plot_adoption_curves(metrics_filtered, plots_dir, strain_names=initial_strain_names, max_day=target_day)
        plot_polarization(metrics_filtered, plots_dir, strain_names=initial_strain_names, max_day=target_day)
        
        if not snapshots_df.empty:
            # Get snapshot at day 25 (or closest)
            available_days = sorted(snapshots_df["day"].unique())
            if available_days:
                plot_day = min(available_days, key=lambda x: abs(x - target_day))
                day_snapshot = snapshots_df[snapshots_df["day"] == plot_day]
                plot_belief_histogram(day_snapshot.drop(columns=["day", "agent_id"]), plots_dir, plot_day)
                
                # Get demographic data
                ages = pd.Series(town.demographics.age)
                ethnicity = None
                if town.demographics.ethnicity is not None:
                    ethnicity = pd.Series(town.demographics.ethnicity)
                
                # Plot adoption by age over time (line graph)
                try:
                    plot_adoption_by_age(
                        snapshots_df,  # Use all snapshots for time series
                        ages,
                        adoption_threshold,
                        plots_dir,
                        target_day,
                        strain_names=initial_strain_names,
                    )
                except Exception as e:
                    logging.warning(f"Failed to plot adoption by age: {e}")
                
                # Plot adoption by ethnicity over time (line graph, if available)
                if ethnicity is not None:
                    try:
                        plot_adoption_by_ethnicity(
                            snapshots_df,  # Use all snapshots for time series
                            ethnicity,
                            adoption_threshold,
                            plots_dir,
                            target_day,
                            strain_names=initial_strain_names,
                        )
                    except Exception as e:
                        logging.warning(f"Failed to plot adoption by ethnicity: {e}")

    metrics_df.to_csv(out_dir / "daily_metrics.csv", index=False)
    if cfg.output.save_snapshots and not snapshots_df.empty:
        try:
            snapshots_df.to_parquet(out_dir / "belief_snapshots.parquet", index=False)
        except ImportError:
            logging.warning("pyarrow not available; saving snapshots as CSV.")
            snapshots_df.to_csv(out_dir / "belief_snapshots.csv", index=False)

    with (out_dir / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    return SimulationOutputs(metrics=metrics_df, snapshots=snapshots_df, summary=summary)


def build_summary(metrics: pd.DataFrame, steps: int, intervention_day: int | None) -> Dict[str, float]:
    summary: Dict[str, float] = {}
    for claim in sorted(metrics["claim"].unique()):
        subset = metrics[metrics["claim"] == claim]
        peak_idx = subset["adoption_fraction"].idxmax()
        peak_day = int(subset.loc[peak_idx, "day"])
        summary[f"claim_{claim}_peak_day"] = peak_day
        summary[f"claim_{claim}_peak_adoption"] = float(subset.loc[peak_idx, "adoption_fraction"])
        summary[f"claim_{claim}_final_adoption"] = float(subset.iloc[-1]["adoption_fraction"])
        summary[f"claim_{claim}_final_polarization"] = float(subset.iloc[-1]["polarization"])
        if intervention_day is not None:
            pre = subset[(subset["day"] >= max(intervention_day - 30, 0)) & (subset["day"] < intervention_day)]
            post = subset[(subset["day"] >= intervention_day) & (subset["day"] <= intervention_day + 30)]
            if not pre.empty and not post.empty:
                effect = float(post["adoption_fraction"].mean() - pre["adoption_fraction"].mean())
            else:
                effect = 0.0
            summary[f"claim_{claim}_intervention_effect"] = effect
        else:
            summary[f"claim_{claim}_intervention_effect"] = 0.0
    summary["steps"] = steps
    return summary
