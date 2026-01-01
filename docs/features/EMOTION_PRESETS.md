# Emotion Presets for Claims

This document describes the available emotion presets for configuring claim emotional profiles.

## Available Presets

### Misinformation Presets

#### `fear_panic`
**Description**: Panic-inducing misinformation (health scares, economic collapse)
- **Fear**: 0.65 (High)
- **Anger**: 0.25 (Moderate)
- **Hope**: 0.10 (Low)
- **Use case**: Health misinformation, economic panic, disaster rumors
- **Research basis**: Guess et al. (2019) - fear-based misinformation spreads faster

#### `anger_outrage`
**Description**: Outrage-inducing misinformation (conspiracy theories, political attacks)
- **Fear**: 0.30 (Moderate)
- **Anger**: 0.60 (High)
- **Hope**: 0.10 (Low)
- **Use case**: Conspiracy theories, political misinformation, social outrage
- **Research basis**: Vosoughi et al. (2018) - anger drives sharing

#### `balanced_negative`
**Description**: Balanced negative emotions (typical misinformation)
- **Fear**: 0.50 (Moderate-High)
- **Anger**: 0.40 (Moderate-High)
- **Hope**: 0.10 (Low)
- **Use case**: General misinformation, default misinformation profile
- **Research basis**: Meta-analysis of misinformation studies

#### `health_scare`
**Description**: Health-focused fear-based misinformation
- **Fear**: 0.70 (Very High)
- **Anger**: 0.20 (Low-Moderate)
- **Hope**: 0.10 (Low)
- **Use case**: Health misinformation, medical conspiracies
- **Research basis**: COVID-19 misinformation patterns (Roozenbeek et al., 2020)

#### `conspiracy`
**Description**: Conspiracy theory emotional profile
- **Fear**: 0.40 (Moderate)
- **Anger**: 0.55 (High)
- **Hope**: 0.05 (Very Low)
- **Use case**: Conspiracy theories, deep state narratives
- **Research basis**: Conspiracy theory research (Lewandowsky et al., 2012)

#### `stealth_moderate`
**Description**: Moderate emotions that evade detection
- **Fear**: 0.35 (Moderate)
- **Anger**: 0.35 (Moderate)
- **Hope**: 0.30 (Moderate)
- **Use case**: Stealth misinformation that doesn't trigger moderation
- **Research basis**: Zannettou et al. (2018) - stealth misinformation patterns

### Truth Presets

#### `truth_factual`
**Description**: Factual truth with positive framing
- **Fear**: 0.05 (Very Low)
- **Anger**: 0.00 (None)
- **Hope**: 0.55 (High)
- **Use case**: Official guidance, factual information
- **Research basis**: Truth spreads slower but with positive framing (Vosoughi et al., 2018)

#### `truth_neutral`
**Description**: Neutral, low-emotion truth
- **Fear**: 0.10 (Low)
- **Anger**: 0.00 (None)
- **Hope**: 0.20 (Low-Moderate)
- **Use case**: Neutral factual information, data-driven content
- **Research basis**: Neutral information patterns

## Usage in Config Files

### Using Presets

```yaml
strains:
  - name: "health_misinformation"
    topic: "health"
    is_true: false
    emotional_profile: "fear_panic"  # Uses preset
    # Other parameters use GENERAL_MISINFORMATION_DEFAULTS
```

### Using Custom Values

You can still override with custom values:

```yaml
strains:
  - name: "custom_misinformation"
    topic: "custom"
    is_true: false
    emotional_profile: {fear: 0.6, anger: 0.3, hope: 0.1}  # Custom values
```

### Default Behavior

If `emotional_profile` is not specified:
- **Truth claims** (`is_true: true`): Defaults to `truth_factual`
- **Misinformation claims** (`is_true: false`): Defaults to `balanced_negative`

## Parameter Defaults

### General Misinformation Defaults

When `is_true: false`, these defaults are applied automatically:

```yaml
memeticity: 0.70           # Highly shareable
virality: 1.0               # Baseline virality (6x truth)
falsifiability: 0.40        # Hard to debunk
stealth: 0.55               # Evades detection
mutation_rate: 0.06         # Moderate mutation rate
violation_risk: 0.35        # Moderate policy violations
persistence: 0.25           # Beliefs fade without reinforcement
```

### Truth Defaults

When `is_true: true`, these defaults are applied automatically:

```yaml
memeticity: 0.25            # Spreads more deliberately
virality: 0.17              # 6x slower than misinformation
falsifiability: 1.0         # Fully verifiable
stealth: 0.0                # Transparent
mutation_rate: 0.0          # Doesn't mutate
violation_risk: 0.0         # No policy violations
persistence: 0.75          # High persistence once adopted
```

## Examples

### Example 1: Multiple Misinformation Claims with Different Emotions

```yaml
strains:
  - name: "panic_misinformation"
    topic: "health"
    is_true: false
    emotional_profile: "fear_panic"
  
  - name: "conspiracy_misinformation"
    topic: "conspiracy"
    is_true: false
    emotional_profile: "conspiracy"
  
  - name: "outrage_misinformation"
    topic: "politics"
    is_true: false
    emotional_profile: "anger_outrage"
  
  - name: "official_truth"
    topic: "health"
    is_true: true
    emotional_profile: "truth_factual"
```

### Example 2: Minimal Config (Uses All Defaults)

```yaml
strains:
  - name: "misinformation"
    topic: "general"
    is_true: false
    # Uses balanced_negative emotion preset + general misinformation defaults
  
  - name: "truth"
    topic: "general"
    is_true: true
    # Uses truth_factual emotion preset + truth defaults
```

## Research Basis

All presets are based on empirical research:

1. **Vosoughi et al. (2018)**: False news spreads 6x faster, more emotional
2. **Guess et al. (2019)**: Fear and anger drive misinformation sharing
3. **Roozenbeek et al. (2020)**: COVID-19 misinformation patterns
4. **Lewandowsky et al. (2012)**: Conspiracy theory characteristics
5. **Zannettou et al. (2018)**: Stealth misinformation patterns

## Customization

You can add custom presets by modifying `sim/config.py`:

```python
EMOTION_PRESETS["custom_name"] = {
    "fear": 0.5,
    "anger": 0.3,
    "hope": 0.2
}
```

Then use it in config files:
```yaml
emotional_profile: "custom_name"
```
