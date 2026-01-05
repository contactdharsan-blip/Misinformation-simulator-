from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Literal

import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator, ConfigDict


# Emotion presets based on research literature
# Sources: Vosoughi et al. (2018), Guess et al. (2019), Roozenbeek et al. (2020), 
#          Lewandowsky et al. (2012), Zannettou et al. (2018)

# 5 Core Misinformation Presets (based on literature)
MISINFORMATION_PRESETS = [
    # 1. Fear-Panic (Vosoughi et al., 2018; Guess et al., 2019)
    # High fear drives sharing, typical of health scares and economic panic
    {
        "name": "fear_panic",
        "fear": 0.65,
        "anger": 0.25,
        "hope": 0.10,
        "description": "Panic-inducing misinformation (health scares, economic collapse)"
    },
    
    # 2. Anger-Outrage (Vosoughi et al., 2018)
    # High anger drives viral sharing, typical of conspiracy theories and political misinformation
    {
        "name": "anger_outrage",
        "fear": 0.30,
        "anger": 0.60,
        "hope": 0.10,
        "description": "Outrage-inducing misinformation (conspiracy theories, political attacks)"
    },
    
    # 3. Balanced Negative (Meta-analysis of misinformation studies)
    # Typical misinformation profile with balanced fear/anger
    {
        "name": "balanced_negative",
        "fear": 0.50,
        "anger": 0.40,
        "hope": 0.10,
        "description": "Balanced negative emotions (typical misinformation)"
    },
    
    # 4. Conspiracy Theory (Lewandowsky et al., 2012)
    # High anger, moderate fear, very low hope - characteristic of conspiracy theories
    {
        "name": "conspiracy",
        "fear": 0.40,
        "anger": 0.55,
        "hope": 0.05,
        "description": "Conspiracy theory profile (deep state narratives, unfalsifiable claims)"
    },
    
    # 5. Stealth Misinformation (Zannettou et al., 2018)
    # Moderate emotions that evade detection and moderation
    {
        "name": "stealth_moderate",
        "fear": 0.35,
        "anger": 0.35,
        "hope": 0.30,
        "description": "Stealth misinformation (evades detection, moderate emotions)"
    }
]

# Truth presets
TRUTH_PRESETS = {
    "truth_factual": {
        "fear": 0.05,
        "anger": 0.00,
        "hope": 0.55,
        "description": "Factual truth with positive framing"
    },
    "truth_neutral": {
        "fear": 0.10,
        "anger": 0.00,
        "hope": 0.20,
        "description": "Neutral, low-emotion truth"
    }
}

# Combined presets dict for lookup
EMOTION_PRESETS = {
    **{preset["name"]: {k: v for k, v in preset.items() if k != "name" and k != "description"} 
       for preset in MISINFORMATION_PRESETS},
    **{name: {k: v for k, v in preset.items() if k != "description"} 
       for name, preset in TRUTH_PRESETS.items()}
}


def get_random_misinformation_preset(seed: int | None = None) -> str:
    """
    Randomly select a misinformation preset based on seed.
    
    Args:
        seed: Random seed for reproducible selection
        
    Returns:
        Preset name (e.g., "fear_panic")
    """
    import numpy as np
    rng = np.random.Generator(np.random.PCG64(seed if seed is not None else None))
    preset_idx = rng.integers(0, len(MISINFORMATION_PRESETS))
    return MISINFORMATION_PRESETS[preset_idx]["name"]


def resolve_emotion_profile(emotion_spec: Dict[str, Any] | str) -> Dict[str, float]:
    """
    Resolve emotion profile from preset name or direct values.
    
    Args:
        emotion_spec: Either a preset name (str) or dict with emotion values
        
    Returns:
        Dict with fear, anger, hope values
    """
    if isinstance(emotion_spec, str):
        # Look up preset
        if emotion_spec in EMOTION_PRESETS:
            preset = EMOTION_PRESETS[emotion_spec]
            # Extract only emotion values (exclude description if present)
            return {
                "fear": preset.get("fear", 0.0),
                "anger": preset.get("anger", 0.0),
                "hope": preset.get("hope", 0.0)
            }
        else:
            available = list(EMOTION_PRESETS.keys()) + [p["name"] for p in MISINFORMATION_PRESETS]
            raise ValueError(
                f"Unknown emotion preset: {emotion_spec}. "
                f"Available presets: {available}"
            )
    elif isinstance(emotion_spec, dict):
        # Direct values - ensure all three emotions are present
        result = {
            "fear": emotion_spec.get("fear", 0.0),
            "anger": emotion_spec.get("anger", 0.0),
            "hope": emotion_spec.get("hope", 0.0)
        }
        return result
    else:
        raise ValueError(f"Invalid emotion_spec type: {type(emotion_spec)}")


# General misinformation defaults based on research (Vosoughi et al., 2018; Roozenbeek et al., 2020)
# Vosoughi et al. (2018): False news spreads 6x faster than true news
GENERAL_MISINFORMATION_DEFAULTS = {
    "memeticity": 0.25,           # Moderately shareable (further reduced for gradual spread)
    "virality": 0.3,               # Further reduced virality (maintains ~6x ratio with truth: 0.3 / 0.05 ≈ 6x)
    "falsifiability": 0.40,        # Hard to debunk (Lewandowsky et al., 2012)
    "stealth": 0.55,               # Evades detection
    "mutation_rate": 0.06,          # Moderate mutation rate
    "violation_risk": 0.35,         # Moderate policy violations
    "persistence": 0.25,            # Beliefs fade without reinforcement
    "is_true": False
}


# Truth defaults based on research
# Vosoughi et al. (2018): True news spreads 6x slower than false news
# Ratio: 1.0 / 6.0 = 0.167 (exactly 6x difference)
TRUTH_DEFAULTS = {
    "memeticity": 0.08,            # Spreads more deliberately (further reduced for gradual spread)
    "virality": 0.05,              # Further reduced virality (maintains ~6x ratio: 0.3 / 0.05 = 6x)
    "falsifiability": 1.0,          # Fully verifiable
    "stealth": 0.0,                 # Transparent
    "mutation_rate": 0.0,           # Doesn't mutate
    "violation_risk": 0.0,          # No policy violations
    "persistence": 0.75,            # High persistence once adopted
    "is_true": True
}


class SimConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    n_agents: int = 1000
    n_steps: int = 200
    steps: int | None = None  # Alias for n_steps (for backward compatibility)
    n_claims: int = 1
    seed: int | None = None
    device: Literal["cpu", "cuda", "mps", "auto"] = "cpu"
    snapshot_interval: int = 50
    adoption_threshold: float = 0.75  # Increased from 0.7 to slow adoption and create more gradual spread
    deterministic: bool = True
    seed_fraction: float = 0.01
    use_tf32: bool = False
    
    @model_validator(mode='after')
    def resolve_steps(self) -> "SimConfig":
        """Resolve steps/n_steps compatibility."""
        if hasattr(self, 'steps') and self.steps is not None:
            self.n_steps = self.steps
        return self


class TownConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    n_neighborhoods: int = 5
    neighborhood_size_mean: float = 200.0
    neighborhood_size_std: float = 50.0
    neighborhood_specs: List[Dict[str, Any]] | None = None
    neighborhood_grid: List[int] | None = None
    household_size_mean: float = 3.0
    household_size_std: float = 1.0
    workplace_size_mean: float = 18.0
    school_size_mean: float = 22.0
    church_size_mean: float = 40.0
    church_attendance_rate: float = 0.25
    min_age: int = 0
    max_age: int = 90
    children_fraction: float = 0.22
    senior_fraction: float = 0.16
    city: str | None = None
    data_source: str | None = None
    education_levels: List[str] = Field(default_factory=lambda: ["none", "high_school", "some_college", "bachelors", "graduate"])
    occupation_types: List[str] = Field(default_factory=lambda: ["unemployed", "service", "blue_collar", "white_collar", "professional", "retired"])


class PersonalityConfig(BaseModel):
    alpha: float = 2.0
    beta: float = 2.0

class CognitiveConfig(BaseModel):
    alpha: float = 2.0
    beta: float = 2.0

class SocialConfig(BaseModel):
    alpha: float = 2.0
    beta: float = 2.0

class EmotionConfig(BaseModel):
    alpha: float = 2.0
    beta: float = 2.0

class TraitConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    skepticism_mean: float = 0.5
    skepticism_std: float = 0.15
    trust_mean: float = 0.5
    trust_std: float = 0.15
    personality: PersonalityConfig = Field(default_factory=PersonalityConfig)
    cognitive: CognitiveConfig = Field(default_factory=CognitiveConfig)
    social: SocialConfig = Field(default_factory=SocialConfig)
    emotion: EmotionConfig = Field(default_factory=EmotionConfig)


class NetworkConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    network_type: Literal["small_world", "scale_free", "random"] = "small_world"
    mean_degree: float = 8.0
    clustering: float = 0.3
    rewiring_prob: float = 0.1
    homophily_strength: float = 0.6
    geography_strength: float = 0.5
    geo_scale: float = 1.5
    intra_neighborhood_p: float = 0.05
    inter_neighborhood_p: float = 0.01
    layer_multipliers: Dict[str, float] = Field(default_factory=lambda: {
        "family": 1.6, "work": 1.1, "school": 1.0, "church": 1.2, "neighborhood": 0.8
    })


class WorldConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    media_channels: List[str] = Field(default_factory=lambda: ["mainstream"])
    moderation_strictness: float = 0.5
    algorithmic_amplification: float = 0.3
    outrage_amplification: float = 0.2
    operator_enabled: bool = False
    emotions_enabled: bool = True
    debunk_intensity: float = 0.25  # Correction intensity (Walter & Tukachinsky, 2020: 25% ± 8% effectiveness)
    feed_injection_rate: float = 0.15
    intervention_day: int | None = None
    intervention_type: str | None = None
    intervention_strength: float = 0.0
    trust_baselines: Dict[str, float] = Field(default_factory=lambda: {
        "gov": 0.55, "church": 0.45, "local_news": 0.5, 
        "national_news": 0.45, "friends": 0.6, "outgroups": 0.3
    })
    trust_variance: float = 0.12
    platform_friction: float = 0.2
    governance_response_speed: float = 0.5
    governance_transparency: float = 0.5
    media_fragmentation: float = 0.4
    reactance_enabled: bool = False
    trust_update_enabled: bool = False
    trust_erosion_rate: float = 0.02
    church_centrality: float = 0.4
    local_media_reach: float = 0.4
    national_media_reach: float = 0.35
    gov_reach: float = 0.3
    truth_campaign_intensity: float = 0.3


class BeliefUpdateConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    learning_rate: float = 0.15
    decay_rate: float = 0.008
    social_proof_weight: float = 0.22
    skepticism_dampening: float = 0.4
    mutual_exclusion_hard: bool = False
    truth_protection_threshold: float | None = None
    baseline_belief: float = 0.05
    social_proof_threshold: float = 0.6
    eta: float = 0.25
    rho: float = 0.25  # Correction effectiveness: 25% ± 8% (Walter & Tukachinsky, 2020 meta-analysis)
    alpha: float = 0.9
    beta: float = 0.6
    gamma: float = 0.4
    delta: float = 0.5
    lambda_skepticism: float = 0.7
    mu_debunk: float = 0.8  # Debunking pressure multiplier
    exposure_memory_decay: float = 0.75
    belief_decay: float = 0.02
    reactance_strength: float = 0.3


class DualProcessConfig(BaseModel):
    """Configuration for dual-process cognitive model."""
    model_config = ConfigDict(extra="allow")
    
    # System 1 parameters
    s1_emotional_weight: float = 0.4
    s1_familiarity_weight: float = 0.3
    s1_narrative_weight: float = 0.3
    s1_novelty_penalty: float = 0.2
    s1_fluency_boost: float = 0.15

    # System 2 parameters
    s2_evidence_weight: float = 0.35
    s2_source_weight: float = 0.3
    s2_consistency_weight: float = 0.25
    s2_complexity_penalty: float = 0.1

    # Integration parameters
    base_s1_tendency: float = 0.6
    cognitive_load_s1_boost: float = 0.3
    stakes_s2_boost: float = 0.25
    need_for_cognition_s2_boost: float = 0.2

    # Thresholds
    deliberation_threshold: float = 0.4
    override_threshold: float = 0.7
    conflict_detection_threshold: float = 0.3

    # Temporal dynamics
    familiarity_decay: float = 0.95
    fluency_learning_rate: float = 0.1


class SharingConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    base_share_rate: float = 0.015  # Base probability of sharing (further reduced for more gradual spread)
    belief_sensitivity: float = 2.0
    emotion_sensitivity: float = 0.5
    status_sensitivity: float = 0.5
    conformity_sensitivity: float = 0.4
    moderation_risk_sensitivity: float = 0.5


class ModerationConfig(BaseModel):
    warning_effect: float = 0.35
    downrank_effect: float = 0.4


class StrainConfig(BaseModel):
    name: str
    topic: str
    memeticity: float | None = None
    emotional_profile: Dict[str, float] | str | None = None  # Can be preset name or dict
    falsifiability: float | None = None
    stealth: float | None = None
    mutation_rate: float | None = None
    violation_risk: float | None = None
    is_true: bool = False
    virality: float | None = None
    persistence: float | None = None
    
    @model_validator(mode='before')
    @classmethod
    def resolve_defaults(cls, data: Any) -> Any:
        """Resolve emotion profile and apply defaults based on is_true."""
        if not isinstance(data, dict):
            return data
        
        # Determine is_true
        is_true = data.get("is_true", False)
        defaults = TRUTH_DEFAULTS if is_true else GENERAL_MISINFORMATION_DEFAULTS
        
        # Resolve emotion profile
        emotion_spec = data.get("emotional_profile")
        if emotion_spec is None:
            # Use default based on is_true
            if is_true:
                data["emotional_profile"] = EMOTION_PRESETS["truth_factual"].copy()
            else:
                # For misinformation, default to balanced_negative
                data["emotional_profile"] = EMOTION_PRESETS["balanced_negative"].copy()
        elif emotion_spec == "random":
            # Mark for random resolution at SimulationConfig level
            # We'll resolve this after all strains are loaded so we have access to seed
            data["_needs_random_resolution"] = True
            # Temporarily set to balanced_negative, will be replaced
            data["emotional_profile"] = EMOTION_PRESETS["balanced_negative"].copy()
        elif isinstance(emotion_spec, (str, dict)):
            data["emotional_profile"] = resolve_emotion_profile(emotion_spec)
        
        # Apply defaults for missing parameters
        if data.get("memeticity") is None:
            data["memeticity"] = defaults["memeticity"]
        if data.get("virality") is None:
            data["virality"] = defaults["virality"]
        if data.get("falsifiability") is None:
            data["falsifiability"] = defaults["falsifiability"]
        if data.get("stealth") is None:
            data["stealth"] = defaults["stealth"]
        if data.get("mutation_rate") is None:
            data["mutation_rate"] = defaults["mutation_rate"]
        if data.get("violation_risk") is None:
            data["violation_risk"] = defaults["violation_risk"]
        if data.get("persistence") is None:
            data["persistence"] = defaults["persistence"]
        
        return data


class OutputConfig(BaseModel):
    save_plots: bool = True
    save_snapshots: bool = True


class MetricsConfig(BaseModel):
    community_backend: Literal["auto", "networkx", "igraph", "none"] = "auto"
    community_max_nodes: int = 20000
    include_neighborhood_clusters: bool = True
    cluster_penetration_enabled: bool = True
    use_gpu_metrics: bool = True


class SimulationConfig(BaseModel):
    sim: SimConfig = SimConfig()
    town: TownConfig = TownConfig()
    traits: TraitConfig = TraitConfig()
    network: NetworkConfig = NetworkConfig()
    world: WorldConfig = WorldConfig()
    belief_update: BeliefUpdateConfig = BeliefUpdateConfig()
    sharing: SharingConfig = SharingConfig()
    dual_process: DualProcessConfig = DualProcessConfig()
    moderation: ModerationConfig = ModerationConfig()
    strains: List[StrainConfig] = Field(default_factory=list)
    metrics: MetricsConfig = MetricsConfig()
    output: OutputConfig = OutputConfig()
    


class ConfigError(Exception):
    pass


def deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in update.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | Path) -> SimulationConfig:
    path = Path(path)
    data = yaml.safe_load(path.read_text()) or {}
    base_path = data.get("base")
    if base_path:
        base_data = yaml.safe_load((path.parent / base_path).read_text()) or {}
        data = deep_merge(base_data, data)
        data.pop("base", None)
    try:
        config = SimulationConfig.model_validate(data)
        # Resolve random presets after validation
        seed = config.sim.seed
        for strain in config.strains:
            if (not strain.is_true and 
                hasattr(strain, '_needs_random_resolution') and 
                strain._needs_random_resolution):
                preset_name = get_random_misinformation_preset(seed)
                strain.emotional_profile = EMOTION_PRESETS[preset_name].copy()
                strain._selected_preset = preset_name
                delattr(strain, '_needs_random_resolution')
        return config
    except ValidationError as exc:
        raise ConfigError(str(exc)) from exc


def dump_config(cfg: SimulationConfig, path: str | Path) -> None:
    path = Path(path)
    path.write_text(yaml.safe_dump(cfg.model_dump(), sort_keys=False))
