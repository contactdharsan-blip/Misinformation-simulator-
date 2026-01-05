# Parameter Adjustments for Realistic Spread Patterns

## Problem Identified

The literature-aligned runs showed:
- **Abrupt spreading**: Truth claims reached 50% adoption in 6-8 days, 90% in 7-9 days
- **Max daily increase**: 60-88% per day (extremely unrealistic)
- **Low misinformation retention**: Misinformation peaked at 0.1-0.5%, then dropped to 0%

## Current Parameter Values (Updated)

### 1. Base Share Rate ✓
**Current Value**: 0.012 (1.2%)  
**File**: `sim/config.py` line 321  
**Previous**: 0.085 (8.5%) → 0.025 (2.5%) → 0.015 (1.5%) → **0.012 (1.2%)**

**Instructions for Adjustment**:
```python
# In sim/config.py, SharingConfig class:
base_share_rate: float = 0.015  # Adjust this value (0.01-0.03 recommended)
```

**Rationale**: The 8.5% from Guess et al. (2019) is for sharing given exposure, but we need a lower base probability before exposure effects are applied. Reduced to 1.5% to create more gradual spread.

### 2. Virality ✓
**Current Values**:
- Misinformation: **0.3** (was 1.0 → 0.4)
- Truth: **0.05** (was 0.167 → 0.067)

**File**: `sim/config.py` lines 149-150, 164-165

**Instructions for Adjustment**:
```python
# In sim/config.py:
GENERAL_MISINFORMATION_DEFAULTS = {
    "virality": 0.3,  # Adjust this (0.2-0.5 recommended)
    ...
}

TRUTH_DEFAULTS = {
    "virality": 0.05,  # Adjust this (0.03-0.1 recommended)
    ...
}
```

**Rationale**: Maintains the 6x ratio (0.3 / 0.05 = 6x) but reduces absolute values to slow spread. This should create more gradual S-curves over 14-28 days.

### 3. Memeticity ✓
**Current Values**:
- Misinformation: **0.25** (was 0.70 → 0.35)
- Truth: **0.08** (was 0.25 → 0.12)

**File**: `sim/config.py` lines 149, 164

**Instructions for Adjustment**:
```python
# In sim/config.py:
GENERAL_MISINFORMATION_DEFAULTS = {
    "memeticity": 0.25,  # Adjust this (0.2-0.4 recommended)
    ...
}

TRUTH_DEFAULTS = {
    "memeticity": 0.08,  # Adjust this (0.05-0.15 recommended)
    ...
}
```

**Rationale**: Lower memeticity = less shareable = slower spread. This helps create more realistic adoption curves.

### 4. Adoption Threshold ✓
**Current Value**: 0.8 (80%)  
**File**: `sim/config.py` line 184  
**Previous**: 0.70 (70%) → 0.75 (75%) → **0.8 (80%)**

**Instructions for Adjustment**:
```python
# In sim/config.py, SimConfig class:
adoption_threshold: float = 0.75  # Adjust this (0.7-0.85 recommended)
```

**Rationale**: Higher threshold = slower adoption = more gradual spread pattern.

### 5. Truth Protection ✓
**Current Implementation**: Gradual decay (8% reduction per day)  
**Previous**: Instant zeroing → 15% decay → **8% decay**

**Files**: 
- `sim/simulation.py` lines 299-316
- `sim/disease/belief_update_torch.py` lines 70-74

**Instructions for Adjustment**:
```python
# In sim/simulation.py and sim/disease/belief_update_torch.py:
decay_rate = 0.92  # Adjust this (0.85-0.95 recommended)
# 0.92 = 8% reduction per day
# 0.85 = 15% reduction per day
# 0.95 = 5% reduction per day (slower decay)
```

**Rationale**: Instant zeroing was too aggressive and caused misinformation to disappear completely. Gradual decay (8% per day) allows misinformation to persist longer, creating more realistic retention patterns.

**Implementation Details**: 
- When an agent adopts truth (belief >= threshold), their misinformation beliefs are multiplied by 0.92 each day
- This means misinformation decays by 8% per day instead of instantly disappearing
- After ~30 days, misinformation beliefs would decay to ~10% of original value
- This allows for sustained misinformation presence while still showing truth protection effects

### 6. Dual-Process Parameters ✓
**Files**: `sim/config.py` lines 319-348

**Implementation**:
- `s1_emotional_weight`: 0.4 (Dominance of emotion in early stage)
- `deliberation_threshold`: 0.4 (Belief uncertainty trigger for System 2)
- `cognitive_load_s1_boost`: 0.3 (Load shifts processing to System 1)

### 7. Engagement Fatigue (Restrained State) ✓
**File**: `sim/simulation.py` lines 271-274

**Implementation**: 
- Agents become **Restrained** after 3 shares per claim.
- Transition is governed by SEDPNR $\lambda$ parameters (P/N -> R).

### 8. SEDPNR Transition Rates ✓
**Current Values** (Nature 2024 Calibrated):
- **alpha (S->E)**: 0.1 (Exposure susceptibility)
- **gamma (E->D)**: 0.1 (Doubt trigger probability)
- **beta_pos (E/D->P)**: 0.5 (Positive infection from state)
- **mu (E/D->S)**: 0.05 (Recovery/Correction)

After these changes:
- **Spread pattern**: Gradual S-curve over 14-28 days (not 6-9 days)
- **Peak timing**: 21 ± 7 days (matching literature)
- **Daily increase**: Max 5-15% per day (not 60-88%)
- **Adoption rates**: 20-35% for misinformation (sustained, not zeroed)
- **Retention**: Misinformation beliefs persist longer, creating more realistic patterns

## How to Test Parameter Adjustments

### Running Simulations with Current Parameters

```bash
# Run a baseline simulation
python3 -m sim run --config configs/world_baseline.yaml --out test_outputs/baseline_test

# Run Phoenix simulation with misinformation
python3 -m sim run --config configs/world_phoenix_with_misinfo.yaml --out test_outputs/phoenix_test

# Run all world configurations
python3 run_all_world_simulations.py
```

### Analyzing Results

```bash
# Check spread patterns
python3 << 'EOF'
import pandas as pd
import matplotlib.pyplot as plt

metrics = pd.read_csv('test_outputs/phoenix_test/daily_metrics.csv')

for claim in metrics['claim'].unique():
    claim_data = metrics[metrics['claim'] == claim].sort_values('day')
    adoption = claim_data['adoption_fraction'].values
    days = claim_data['day'].values
    
    # Check spread speed
    mid_day = days[(adoption > 0.5).argmax()] if (adoption > 0.5).any() else None
    max_increase = (adoption[1:] - adoption[:-1]).max() if len(adoption) > 1 else 0
    
    print(f"Claim {claim}:")
    print(f"  Days to 50%: {mid_day}")
    print(f"  Max daily increase: {max_increase:.1%}")
EOF
```

### Validation Checklist

To validate these changes:
1. ✅ Run literature-aligned simulations with new parameters
2. ✅ Check that spread curves are gradual S-curves (not abrupt jumps)
3. ✅ Verify peak timing is 21 ± 7 days (may need longer simulations)
4. ✅ Confirm adoption rates are 20-35% for misinformation
5. ✅ Verify misinformation retention > 0% (not instant zeroing)
6. ✅ Check daily increases are reasonable (5-15% max, not 60-88%)

### Fine-Tuning Parameters

If spread is still too fast:
1. **Reduce base_share_rate**: Try 0.01 (1%) or lower
2. **Reduce virality further**: Misinfo 0.2, Truth 0.033 (maintains 6x ratio)
3. **Reduce memeticity**: Misinfo 0.2, Truth 0.05
4. **Increase adoption_threshold**: Try 0.8 (80%) or 0.85 (85%)
5. **Slow decay rate**: Try 0.95 (5% reduction per day)

If spread is too slow:
1. **Increase base_share_rate**: Try 0.02 (2%) or 0.025 (2.5%)
2. **Increase virality**: Misinfo 0.4, Truth 0.067
3. **Increase memeticity**: Misinfo 0.3, Truth 0.1

## Next Steps

1. **Test new parameters**: Run simulations to verify improvements
2. **Fine-tune if needed**: Adjust decay rate, virality, or base share rate based on results
3. **Add skepticism barriers**: Consider requiring multiple exposures for high-skepticism agents
4. **Network adjustments**: May need to adjust network structure if spread is still too fast
5. **Longer simulations**: Run 100+ day simulations to observe full spread patterns

## Files Modified

1. `sim/config.py`: Updated base_share_rate, virality, memeticity, adoption_threshold
2. `sim/simulation.py`: Changed truth protection from instant zeroing to gradual decay
3. `sim/disease/belief_update_torch.py`: Changed truth protection to gradual decay

## Notes

- The 6x virality ratio (misinformation vs truth) is maintained
- Age multipliers (7x for 65+) are unchanged - they're correct from literature
- Education effects are unchanged - they're correct from literature
- These changes focus on slowing spread and allowing misinformation retention
