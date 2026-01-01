# Example Configurations Using Emotion Presets

This document shows examples of how to use emotion presets and general misinformation defaults.

## Basic Example: One Truth + One Misinformation

```yaml
base: world_phoenix.yaml

sim:
  n_claims: 2

strains:
  # Truth claim - minimal config, uses all defaults
  - name: "official_health_guidance"
    topic: "health_guidance"
    is_true: true
    emotional_profile: "truth_factual"  # Optional: defaults to truth_factual anyway
  
  # Misinformation - minimal config, uses all defaults
  - name: "fear_based_misinformation"
    topic: "health_scare"
    is_true: false
    emotional_profile: "fear_panic"  # Choose emotion preset
```

## Multiple Misinformation Claims with Different Emotions

```yaml
base: world_phoenix.yaml

sim:
  n_claims: 4  # 1 truth + 3 misinformation

strains:
  - name: "official_truth"
    topic: "health"
    is_true: true
    emotional_profile: "truth_factual"
  
  # Panic-inducing misinformation
  - name: "health_panic"
    topic: "health_scare"
    emotional_profile: "fear_panic"
  
  # Outrage-inducing misinformation
  - name: "conspiracy_theory"
    topic: "conspiracy"
    emotional_profile: "anger_outrage"
  
  # Stealth misinformation
  - name: "stealth_misinformation"
    topic: "general"
    emotional_profile: "stealth_moderate"
```

## Overriding Defaults

You can still override individual parameters:

```yaml
strains:
  - name: "high_virality_misinformation"
    topic: "viral"
    is_true: false
    emotional_profile: "balanced_negative"
    virality: 1.5  # Override default (1.0) - make it more viral
    memeticity: 0.80  # Override default (0.70) - make it more shareable
```

## Custom Emotion Values

You can still use custom emotion values instead of presets:

```yaml
strains:
  - name: "custom_misinformation"
    topic: "custom"
    is_true: false
    emotional_profile: {fear: 0.6, anger: 0.3, hope: 0.1}  # Custom values
    # Other parameters still use GENERAL_MISINFORMATION_DEFAULTS
```

## Minimal Config (Maximum Defaults)

The most minimal config possible:

```yaml
strains:
  - name: "truth"
    topic: "general"
    is_true: true
    # Uses truth_factual preset + all truth defaults
  
  - name: "misinformation"
    topic: "general"
    is_true: false
    # Uses balanced_negative preset + all general misinformation defaults
```

## Available Emotion Presets

See `EMOTION_PRESETS.md` for full list:

**Misinformation:**
- `fear_panic` - Panic-inducing (health scares)
- `anger_outrage` - Outrage-inducing (conspiracies)
- `balanced_negative` - Typical misinformation (default)
- `health_scare` - Health-focused fear
- `conspiracy` - Conspiracy theories
- `stealth_moderate` - Stealth misinformation

**Truth:**
- `truth_factual` - Factual with positive framing (default for truth)
- `truth_neutral` - Neutral, low-emotion truth

## General Misinformation Defaults

When `is_true: false`, these are automatically applied:

- `memeticity`: 0.70 (highly shareable)
- `virality`: 1.0 (baseline, 6x truth)
- `falsifiability`: 0.40 (hard to debunk)
- `stealth`: 0.55 (evades detection)
- `mutation_rate`: 0.06 (moderate mutation)
- `violation_risk`: 0.35 (moderate policy violations)
- `persistence`: 0.25 (beliefs fade without reinforcement)

## Truth Defaults

When `is_true: true`, these are automatically applied:

- `memeticity`: 0.25 (spreads deliberately)
- `virality`: 0.17 (6x slower than misinformation)
- `falsifiability`: 1.0 (fully verifiable)
- `stealth`: 0.0 (transparent)
- `mutation_rate`: 0.0 (doesn't mutate)
- `violation_risk`: 0.0 (no violations)
- `persistence`: 0.75 (high persistence)
