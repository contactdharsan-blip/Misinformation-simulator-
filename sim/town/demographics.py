from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from sim.config import TraitConfig, TownConfig, WorldConfig


@dataclass
class Demographics:
    age: np.ndarray
    education_level: np.ndarray
    occupation: np.ndarray
    ethnicity: np.ndarray | None = None  # Ethnicity labels: 'white', 'hispanic', 'black', 'asian', 'other'


@dataclass
class Traits:
    personality: np.ndarray
    skepticism: np.ndarray
    need_for_closure: np.ndarray
    conspiratorial_tendency: np.ndarray
    numeracy: np.ndarray
    conformity: np.ndarray
    status_seeking: np.ndarray
    prosociality: np.ndarray
    conflict_tolerance: np.ndarray
    emotions: Dict[str, np.ndarray]
    credibility: np.ndarray


@dataclass
class Trust:
    trust_gov: np.ndarray
    trust_church: np.ndarray
    trust_local_news: np.ndarray
    trust_national_news: np.ndarray
    trust_friends: np.ndarray
    trust_outgroups: np.ndarray


@dataclass
class MediaDiet:
    channels: List[str]
    weights: np.ndarray


def _beta(rng: np.random.Generator, alpha: float, beta: float, size: int) -> np.ndarray:
    return rng.beta(alpha, beta, size=size).astype(np.float32)


def generate_demographics(
    rng: np.random.Generator,
    n_agents: int,
    town: TownConfig,
) -> Demographics:
    children = int(n_agents * town.children_fraction)
    seniors = int(n_agents * town.senior_fraction)
    adults = n_agents - children - seniors

    ages = np.concatenate([
        rng.integers(0, 18, size=children),
        rng.integers(18, 65, size=adults),
        rng.integers(65, town.max_age + 1, size=seniors),
    ])
    rng.shuffle(ages)

    education_levels = rng.integers(0, len(town.education_levels), size=n_agents)
    occupation = rng.integers(0, len(town.occupation_types), size=n_agents)
    return Demographics(age=ages.astype(np.int32), education_level=education_levels, occupation=occupation)


def generate_traits(
    rng: np.random.Generator,
    n_agents: int,
    traits: TraitConfig,
    emotions_enabled: bool,
    ages: Optional[np.ndarray] = None,
) -> Traits:
    personality = np.stack([
        _beta(rng, traits.personality.alpha, traits.personality.beta, n_agents)
        for _ in range(5)
    ], axis=1)

    skepticism = _beta(rng, traits.cognitive.alpha, traits.cognitive.beta, n_agents)
    need_for_closure = _beta(rng, traits.cognitive.alpha, traits.cognitive.beta, n_agents)
    conspiratorial_tendency = _beta(rng, traits.cognitive.alpha, traits.cognitive.beta, n_agents)
    numeracy = _beta(rng, traits.cognitive.alpha, traits.cognitive.beta, n_agents)

    conformity = _beta(rng, traits.social.alpha, traits.social.beta, n_agents)
    status_seeking = _beta(rng, traits.social.alpha, traits.social.beta, n_agents)
    prosociality = _beta(rng, traits.social.alpha, traits.social.beta, n_agents)
    conflict_tolerance = _beta(rng, traits.social.alpha, traits.social.beta, n_agents)

    emotions = {}
    if emotions_enabled:
        emotions = {
            "fear": _beta(rng, traits.emotion.alpha, traits.emotion.beta, n_agents),
            "anger": _beta(rng, traits.emotion.alpha, traits.emotion.beta, n_agents),
            "hope": _beta(rng, traits.emotion.alpha, traits.emotion.beta, n_agents),
        }
    # Compute age-based credibility factor (0..1). If ages provided, scale credibility by age.
    if ages is not None:
        # Relative credibility: map each agent's age to its percentile rank in the population
        # so credibility is higher for agents older than their peers and lower for younger agents.
        ages_arr = ages.astype(np.float32)
        # ranks: 0..n-1 where larger means older relative to others
        ranks = np.argsort(np.argsort(ages_arr))
        denom = max(1, len(ranks) - 1)
        norm_rank = ranks.astype(np.float32) / float(denom)
        credibility = 0.2 + 0.75 * norm_rank
        credibility = np.clip(credibility, 0.2, 0.95).astype(np.float32)
    else:
        # fallback: sample credibility from Beta distribution centered around 0.6
        credibility = _beta(rng, 2.0, 1.5, n_agents)

    return Traits(
        personality=personality,
        skepticism=skepticism,
        need_for_closure=need_for_closure,
        conspiratorial_tendency=conspiratorial_tendency,
        numeracy=numeracy,
        conformity=conformity,
        status_seeking=status_seeking,
        prosociality=prosociality,
        conflict_tolerance=conflict_tolerance,
        emotions=emotions,
        credibility=credibility,
    )


def generate_trust(
    rng: np.random.Generator,
    n_agents: int,
    world: WorldConfig,
) -> Trust:
    def jitter(base: float) -> np.ndarray:
        vals = rng.normal(loc=base, scale=world.trust_variance, size=n_agents)
        return np.clip(vals, 0.0, 1.0).astype(np.float32)

    return Trust(
        trust_gov=jitter(world.trust_baselines["gov"]),
        trust_church=jitter(world.trust_baselines["church"]),
        trust_local_news=jitter(world.trust_baselines["local_news"]),
        trust_national_news=jitter(world.trust_baselines["national_news"]),
        trust_friends=jitter(world.trust_baselines["friends"]),
        trust_outgroups=jitter(world.trust_baselines["outgroups"]),
    )


def generate_media_diet(
    rng: np.random.Generator,
    n_agents: int,
    env: Dict[str, Any] | None = None,
) -> MediaDiet:
    """Generate per-agent media channel weights. If `env` is provided use rough averages from it.

    The function is intentionally simple: when a `media_environment` dict is provided
    (as in the Phoenix example), we build channels from available social platforms and
    local outlets and sample per-agent preferences from a Dirichlet with concentration
    parameters derived from average usage/reach values.
    """
    if env and isinstance(env, dict):
        channels = []
        alphas = []

        # local outlets
        local = env.get("local_outlets")
        if local:
            channels.append("local_news")
            # average reach across outlets -> modest alpha
            avg_reach = float(
                sum([sum(o.get("reach_by_group", {}).values()) / max(1, len(o.get("reach_by_group", {}))) for o in local]) / max(1, len(local))
            )
            alphas.append(max(0.2, avg_reach * 5.0))

        # common social platforms
        social = env.get("social_media_penetration") or {}
        for plat in ("facebook", "instagram", "tiktok", "whatsapp"):
            usage = social.get(plat)
            if usage and isinstance(usage, dict):
                # average across groups
                avg = float(sum(usage.get("usage_by_group", {}).values()) / max(1, len(usage.get("usage_by_group", {})))) if isinstance(usage.get("usage_by_group"), dict) else 0.2
                channels.append(plat)
                alphas.append(max(0.2, avg * 5.0))

        if not channels:
            channels = ["local_social", "national_social", "tv", "local_news", "church"]
            weights = rng.dirichlet([1.5, 1.2, 1.0, 1.3, 0.9], size=n_agents).astype(np.float32)
            return MediaDiet(channels=channels, weights=weights)

        # sample per-agent weights from Dirichlet with small jitter
        alphas = [a + 0.5 for a in alphas]
        weights = rng.dirichlet(alphas, size=n_agents).astype(np.float32)
        return MediaDiet(channels=channels, weights=weights)

    # fallback default
    channels = ["local_social", "national_social", "tv", "local_news", "church"]
    weights = rng.dirichlet([1.5, 1.2, 1.0, 1.3, 0.9], size=n_agents).astype(np.float32)
    return MediaDiet(channels=channels, weights=weights)


def ideology_proxy(traits: Traits, trust: Trust) -> np.ndarray:
    raw = (
        0.2 * traits.conspiratorial_tendency
        + 0.2 * (1 - traits.numeracy)
        + 0.15 * traits.conformity
        + 0.15 * (1 - trust.trust_outgroups)
        + 0.15 * trust.trust_church
        + 0.15 * (1 - trust.trust_national_news)
    )
    return np.clip(raw, 0.0, 1.0).astype(np.float32)
