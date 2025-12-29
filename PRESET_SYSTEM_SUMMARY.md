# Emotion Preset System Summary

## Overview

The simulation now uses **5 literature-based misinformation presets** that can be randomly selected based on seed, ensuring all misinformation claims use consistent general defaults while varying only in emotional profile.

## Key Features

### 1. 5 Core Misinformation Presets

All based on empirical research:

1. **`fear_panic`** - Vosoughi et al. (2018), Guess et al. (2019)
   - Fear: 0.65, Anger: 0.25, Hope: 0.10
   - Panic-inducing misinformation (health scares, economic collapse)

2. **`anger_outrage`** - Vosoughi et al. (2018)
   - Fear: 0.30, Anger: 0.60, Hope: 0.10
   - Outrage-inducing misinformation (conspiracy theories, political attacks)

3. **`balanced_negative`** - Meta-analysis
   - Fear: 0.50, Anger: 0.40, Hope: 0.10
   - Typical misinformation profile (default)

4. **`conspiracy`** - Lewandowsky et al. (2012)
   - Fear: 0.40, Anger: 0.55, Hope: 0.05
   - Conspiracy theory profile (deep state narratives)

5. **`stealth_moderate`** - Zannettou et al. (2018)
   - Fear: 0.35, Anger: 0.35, Hope: 0.30
   - Stealth misinformation (evades detection)

### 2. Random Selection Based on Seed

When `emotional_profile: "random"` is specified:

```yaml
strains:
  - name: "misinformation"
    topic: "general"
    is_true: false
    emotional_profile: "random"  # Randomly selects from 5 presets
```

- Uses `sim.seed` for reproducible selection
- Same seed = same preset
- Different seeds explore different misinformation types

### 3. General Misinformation Defaults

All misinformation claims (`is_true: false`) automatically use:

```yaml
memeticity: 0.70           # Highly shareable
virality: 1.0               # Baseline (6x truth)
falsifiability: 0.40        # Hard to debunk
stealth: 0.55               # Evades detection
mutation_rate: 0.06         # Moderate mutation
violation_risk: 0.35        # Moderate policy violations
persistence: 0.25           # Beliefs fade without reinforcement
```

Only the emotion profile differs between presets.

## Usage Examples

### Example 1: Random Selection

```yaml
sim:
  seed: 42  # Determines which preset is selected

strains:
  - name: "misinformation"
    topic: "general"
    is_true: false
    emotional_profile: "random"  # Selects preset based on seed=42
```

### Example 2: Specific Preset

```yaml
strains:
  - name: "panic_misinformation"
    topic: "health"
    is_true: false
    emotional_profile: "fear_panic"  # Explicitly choose fear_panic
```

### Example 3: Multiple Misinformation Claims

```yaml
strains:
  - name: "misinformation_1"
    topic: "health"
    is_true: false
    emotional_profile: "random"  # Random preset based on seed
  
  - name: "misinformation_2"
    topic: "politics"
    is_true: false
    emotional_profile: "random"  # Different random preset (uses seed + claim index)
```

## Implementation Details

### Code Location

- **Presets defined**: `sim/config.py` → `MISINFORMATION_PRESETS`
- **Random selection**: `sim/config.py` → `get_random_misinformation_preset(seed)`
- **Config loading**: `sim/config.py` → `load_config()` resolves "random" presets

### How Random Selection Works

```python
def get_random_misinformation_preset(seed: int | None = None) -> str:
    """Randomly select a misinformation preset based on seed."""
    import numpy as np
    rng = np.random.Generator(np.random.PCG64(seed if seed is not None else None))
    preset_idx = rng.integers(0, len(MISINFORMATION_PRESETS))
    return MISINFORMATION_PRESETS[preset_idx]["name"]
```

- Uses NumPy's PCG64 generator for reproducibility
- Returns preset name (e.g., "fear_panic")
- Same seed always selects same preset

## Benefits

1. **Consistency**: All misinformation uses same parameter defaults
2. **Variety**: Random selection explores different misinformation types
3. **Reproducibility**: Seed-based selection ensures reproducibility
4. **Literature-Based**: All presets grounded in empirical research
5. **Simplicity**: Minimal config needed - just specify `emotional_profile: "random"`

## Updated Config File

Your `configs/world_phoenix_truth_random.yaml` now uses:

```yaml
strains:
  - name: "official_health_guidance"
    topic: "health_guidance"
    is_true: true
    emotional_profile: "truth_factual"
  
  - name: "misinformation"
    topic: "general"
    is_true: false
    emotional_profile: "random"  # Randomly selects from 5 presets based on seed
```

## Documentation

- **`MISINFORMATION_PRESETS.md`** - Detailed description of all 5 presets with research citations
- **`EMOTION_PRESETS.md`** - Original documentation (now includes random selection)
- **`EXAMPLE_CONFIGS.md`** - Usage examples

## Testing

To test random selection:

```python
from sim.config import get_random_misinformation_preset

# Same seed = same preset
preset1 = get_random_misinformation_preset(seed=42)
preset2 = get_random_misinformation_preset(seed=42)
assert preset1 == preset2  # True

# Different seeds = potentially different presets
preset3 = get_random_misinformation_preset(seed=100)
# May or may not equal preset1
```
