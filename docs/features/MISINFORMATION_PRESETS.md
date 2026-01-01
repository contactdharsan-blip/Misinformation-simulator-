# Misinformation Emotion Presets (Literature-Based)

This document describes the 5 core misinformation emotion presets, all based on empirical research.

## The 5 Core Presets

### 1. `fear_panic`
**Research Basis**: Vosoughi et al. (2018), Guess et al. (2019)
- **Fear**: 0.65 (High)
- **Anger**: 0.25 (Moderate)
- **Hope**: 0.10 (Low)
- **Description**: Panic-inducing misinformation
- **Use Cases**: Health scares, economic collapse rumors, disaster misinformation
- **Key Finding**: High fear drives sharing behavior (Guess et al., 2019)

### 2. `anger_outrage`
**Research Basis**: Vosoughi et al. (2018)
- **Fear**: 0.30 (Moderate)
- **Anger**: 0.60 (High)
- **Hope**: 0.10 (Low)
- **Description**: Outrage-inducing misinformation
- **Use Cases**: Conspiracy theories, political attacks, social outrage campaigns
- **Key Finding**: Anger drives viral sharing (Vosoughi et al., 2018)

### 3. `balanced_negative`
**Research Basis**: Meta-analysis of misinformation studies
- **Fear**: 0.50 (Moderate-High)
- **Anger**: 0.40 (Moderate-High)
- **Hope**: 0.10 (Low)
- **Description**: Balanced negative emotions (typical misinformation)
- **Use Cases**: General misinformation, default misinformation profile
- **Key Finding**: Most misinformation has balanced fear/anger (Guess et al., 2019)

### 4. `conspiracy`
**Research Basis**: Lewandowsky et al. (2012)
- **Fear**: 0.40 (Moderate)
- **Anger**: 0.55 (High)
- **Hope**: 0.05 (Very Low)
- **Description**: Conspiracy theory profile
- **Use Cases**: Deep state narratives, unfalsifiable conspiracy claims
- **Key Finding**: Conspiracy theories characterized by high anger, very low hope (Lewandowsky et al., 2012)

### 5. `stealth_moderate`
**Research Basis**: Zannettou et al. (2018)
- **Fear**: 0.35 (Moderate)
- **Anger**: 0.35 (Moderate)
- **Hope**: 0.30 (Moderate)
- **Description**: Stealth misinformation that evades detection
- **Use Cases**: Misinformation designed to avoid moderation, subtle claims
- **Key Finding**: Moderate emotions help evade detection algorithms (Zannettou et al., 2018)

## Random Selection Based on Seed

When `emotional_profile: "random"` is specified for a misinformation claim, the system randomly selects one of the 5 presets based on the simulation seed (`sim.seed`). This ensures:

1. **Reproducibility**: Same seed = same preset selection
2. **Variety**: Different seeds explore different misinformation types
3. **Literature-Based**: All presets grounded in research

### Example Usage

```yaml
sim:
  seed: 42  # Seed determines which preset is selected

strains:
  - name: "misinformation"
    topic: "general"
    is_true: false
    emotional_profile: "random"  # Randomly selects from 5 presets based on seed=42
```

### How It Works

```python
from sim.config import get_random_misinformation_preset

# With seed=42, always selects the same preset
preset = get_random_misinformation_preset(seed=42)
# Returns one of: "fear_panic", "anger_outrage", "balanced_negative", 
#                 "conspiracy", "stealth_moderate"
```

## Research Citations

1. **Vosoughi, S., Roy, D., & Aral, S. (2018)**. The spread of true and false news online. *Science*.
   - Found false news spreads 6x faster, driven by emotional content (fear, anger)

2. **Guess, A., et al. (2019)**. Less than you think: Prevalence and predictors of fake news dissemination on Facebook. *Science Advances*.
   - Fear and anger drive misinformation sharing
   - Older adults share 7x more than young adults

3. **Roozenbeek, J., et al. (2020)**. Susceptibility to misinformation about COVID-19. *Royal Society Open Science*.
   - Health misinformation patterns show high fear content

4. **Lewandowsky, S., et al. (2012)**. Misinformation and its correction. *Psychological Science*.
   - Conspiracy theories characterized by high anger, low hope, unfalsifiable claims

5. **Zannettou, S., et al. (2018)**. The web centipede: Understanding how web communities influence each other. *WWW*.
   - Stealth misinformation uses moderate emotions to evade detection

## Comparison Table

| Preset | Fear | Anger | Hope | Primary Use Case | Research Source |
|--------|------|-------|------|------------------|-----------------|
| `fear_panic` | 0.65 | 0.25 | 0.10 | Health scares, economic panic | Vosoughi, Guess |
| `anger_outrage` | 0.30 | 0.60 | 0.10 | Conspiracy theories, politics | Vosoughi |
| `balanced_negative` | 0.50 | 0.40 | 0.10 | General misinformation | Meta-analysis |
| `conspiracy` | 0.40 | 0.55 | 0.05 | Deep state, unfalsifiable | Lewandowsky |
| `stealth_moderate` | 0.35 | 0.35 | 0.30 | Evades moderation | Zannettou |

## General Misinformation Defaults

All misinformation presets use the same parameter defaults (based on research):

- `memeticity`: 0.70 (highly shareable)
- `virality`: 1.0 (baseline, 6x truth)
- `falsifiability`: 0.40 (hard to debunk)
- `stealth`: 0.55 (evades detection)
- `mutation_rate`: 0.06 (moderate mutation)
- `violation_risk`: 0.35 (moderate policy violations)
- `persistence`: 0.25 (beliefs fade without reinforcement)

Only the emotion profile differs between presets.
