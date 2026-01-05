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
    neighborhood_ids: Optional[np.ndarray] = None,
    neighborhood_education: Optional[Dict[int, float]] = None,
    neighborhood_income: Optional[Dict[int, float]] = None,
) -> Traits:
    personality = np.stack([
        _beta(rng, traits.personality.alpha, traits.personality.beta, n_agents)
        for _ in range(5)
    ], axis=1)

    # Base trait generation
    skepticism_base = _beta(rng, traits.cognitive.alpha, traits.cognitive.beta, n_agents)
    need_for_closure = _beta(rng, traits.cognitive.alpha, traits.cognitive.beta, n_agents)
    conspiratorial_tendency = _beta(rng, traits.cognitive.alpha, traits.cognitive.beta, n_agents)
    numeracy_base = _beta(rng, traits.cognitive.alpha, traits.cognitive.beta, n_agents)

    conformity_base = _beta(rng, traits.social.alpha, traits.social.beta, n_agents)
    status_seeking = _beta(rng, traits.social.alpha, traits.social.beta, n_agents)
    prosociality = _beta(rng, traits.social.alpha, traits.social.beta, n_agents)
    conflict_tolerance = _beta(rng, traits.social.alpha, traits.social.beta, n_agents)
    
    # Apply neighborhood-specific adjustments if available
    skepticism = skepticism_base.copy()
    numeracy = numeracy_base.copy()
    conformity = conformity_base.copy()
    
    if neighborhood_ids is not None and neighborhood_education is not None:
        # Higher education → higher skepticism and numeracy, lower conspiratorial tendency
        # Based on Pennycook & Rand (2021): education-belief correlation of -0.25
        for nid, edu_rate in neighborhood_education.items():
            mask = neighborhood_ids == nid
            if mask.any():
                # Education effect: stronger effect to achieve -0.25 correlation
                # Normalize education rate to [-1, 1] scale
                edu_normalized = (edu_rate - 0.3) / 0.5  # 0.3 (low) to 0.8 (high) -> -1 to +1
                # Stronger effects to match literature: -0.25 correlation means high-edu have ~25% lower belief
                skepticism[mask] = np.clip(skepticism[mask] + 0.25 * edu_normalized, 0.0, 1.0)
                numeracy[mask] = np.clip(numeracy[mask] + 0.3 * edu_normalized, 0.0, 1.0)
                conspiratorial_tendency[mask] = np.clip(conspiratorial_tendency[mask] - 0.25 * edu_normalized, 0.0, 1.0)
    
    if neighborhood_ids is not None and neighborhood_income is not None:
        # Higher income → lower conformity (more independent thinking)
        for nid, income in neighborhood_income.items():
            mask = neighborhood_ids == nid
            if mask.any():
                # Income effect: normalize income (e.g., 30k-110k range) and adjust conformity
                income_normalized = (income - 30000) / 80000  # Rough normalization
                income_normalized = np.clip(income_normalized, 0.0, 1.0)
                conformity[mask] = np.clip(conformity[mask] - 0.2 * (income_normalized - 0.5), 0.0, 1.0)

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
    neighborhood_ids: Optional[np.ndarray] = None,
    neighborhood_income: Optional[Dict[int, float]] = None,
    neighborhood_education: Optional[Dict[int, float]] = None,
) -> Trust:
    def jitter(base: float, size: int) -> np.ndarray:
        vals = rng.normal(loc=base, scale=world.trust_variance, size=size)
        return np.clip(vals, 0.0, 1.0).astype(np.float32)
    
    # Base trust values with jitter
    trust_gov = jitter(world.trust_baselines["gov"], n_agents)
    trust_church = jitter(world.trust_baselines["church"], n_agents)
    trust_local_news = jitter(world.trust_baselines["local_news"], n_agents)
    trust_national_news = jitter(world.trust_baselines["national_news"], n_agents)
    trust_friends = jitter(world.trust_baselines["friends"], n_agents)
    trust_outgroups = jitter(world.trust_baselines["outgroups"], n_agents)
    
    # Apply neighborhood-specific adjustments if available
    if neighborhood_ids is not None:
        if neighborhood_income is not None:
            # Higher income → higher trust in institutions (gov, media)
            for nid, income in neighborhood_income.items():
                mask = neighborhood_ids == nid
                if mask.any():
                    income_normalized = (income - 30000) / 80000
                    income_normalized = np.clip(income_normalized, 0.0, 1.0)
                    income_effect = (income_normalized - 0.5) * 0.25  # ±0.125 max effect
                    trust_gov[mask] = np.clip(trust_gov[mask] + income_effect, 0.0, 1.0)
                    trust_local_news[mask] = np.clip(trust_local_news[mask] + income_effect * 0.8, 0.0, 1.0)
                    trust_national_news[mask] = np.clip(trust_national_news[mask] + income_effect * 0.8, 0.0, 1.0)
        
        if neighborhood_education is not None:
            # Higher education → higher trust in media, lower trust in church
            for nid, edu_rate in neighborhood_education.items():
                mask = neighborhood_ids == nid
                if mask.any():
                    edu_effect = (edu_rate - 0.3) / 0.5  # Normalize: -1 to +1
                    trust_local_news[mask] = np.clip(trust_local_news[mask] + 0.1 * edu_effect, 0.0, 1.0)
                    trust_national_news[mask] = np.clip(trust_national_news[mask] + 0.1 * edu_effect, 0.0, 1.0)
                    trust_church[mask] = np.clip(trust_church[mask] - 0.15 * edu_effect, 0.0, 1.0)

    return Trust(
        trust_gov=trust_gov,
        trust_church=trust_church,
        trust_local_news=trust_local_news,
        trust_national_news=trust_national_news,
        trust_friends=trust_friends,
        trust_outgroups=trust_outgroups,
    )


def generate_media_diet(
    rng: np.random.Generator,
    n_agents: int,
    env: Dict[str, Any] | None = None,
    ages: np.ndarray | None = None,
    ethnicity: np.ndarray | None = None,
) -> MediaDiet:
    """Generate per-agent media channel weights with demographic biases.
    
    Biases (Pew Research findings):
    - Young (18-34): High TikTok/Instagram, low TV/Local News.
    - Seniors (65+): High TV/Local News, low TikTok.
    - Ethnicity: Specific platforms over-index in certain communities (e.g., WhatsApp in Hispanic/Latino).
    """
    if env and isinstance(env, dict):
        base_channels = []
        base_alphas = []

        # local outlets
        local = env.get("local_outlets")
        if local:
            base_channels.append("local_news")
            avg_reach = float(
                sum([sum(o.get("reach_by_group", {}).values()) / max(1, len(o.get("reach_by_group", {}))) for o in local]) / max(1, len(local))
            )
            base_alphas.append(max(0.2, avg_reach * 5.0))

        # common social platforms
        social = env.get("social_media_penetration") or {}
        for plat in ("facebook", "instagram", "tiktok", "whatsapp"):
            usage = social.get(plat)
            if usage and isinstance(usage, dict):
                avg = float(sum(usage.get("usage_by_group", {}).values()) / max(1, len(usage.get("usage_by_group", {})))) if isinstance(usage.get("usage_by_group"), dict) else 0.2
                base_channels.append(plat)
                base_alphas.append(max(0.2, avg * 5.0))

        if not base_channels:
            base_channels = ["local_social", "national_social", "tv", "local_news", "church"]
            base_alphas = [1.5, 1.2, 1.0, 1.3, 0.9]

        weights = np.zeros((n_agents, len(base_channels)), dtype=np.float32)
        
        # Apply demographic biases
        for i in range(n_agents):
            agent_alphas = list(base_alphas)
            
            # Age Bias
            if ages is not None:
                age = ages[i]
                if age < 35:
                    # Youth: +TikTok, +Instagram, -TV, -Local News
                    for idx, ch in enumerate(base_channels):
                        if ch in ("tiktok", "instagram"): agent_alphas[idx] *= 2.0
                        if ch in ("tv", "local_news"): agent_alphas[idx] *= 0.5
                elif age >= 65:
                    # Seniors: +TV, +Local News, --TikTok, -Instagram
                    for idx, ch in enumerate(base_channels):
                        if ch in ("tv", "local_news"): agent_alphas[idx] *= 2.0
                        if ch in ("tiktok"): agent_alphas[idx] *= 0.1
                        if ch in ("instagram"): agent_alphas[idx] *= 0.4
            
            # Ethnicity Bias (Subtle community penetration shifts)
            if ethnicity is not None:
                eth = ethnicity[i]
                if eth == 'hispanic':
                    # WhatsApp often over-indexes in Hispanic communities (connectivity to international fam)
                    for idx, ch in enumerate(base_channels):
                        if ch == "whatsapp": agent_alphas[idx] *= 1.5
                elif eth == 'black':
                    # High social media engagement for news
                    for idx, ch in enumerate(base_channels):
                        if ch in ("facebook", "tiktok"): agent_alphas[idx] *= 1.3
            
            # Stochasticity: unique diet for every agent
            weights[i] = rng.dirichlet([a + 0.1 for a in agent_alphas])
            
        return MediaDiet(channels=base_channels, weights=weights)

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
