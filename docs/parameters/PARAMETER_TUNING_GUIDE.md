# Parameter Tuning Guide

This guide provides instructions for adjusting simulation parameters to achieve desired spread patterns.

## Quick Reference: Current Parameter Values

| Parameter | Value | Location | Range |
|-----------|-------|----------|-------|
| Base share rate | 0.015 (1.5%) | `sim/config.py:321` | 0.01-0.03 |
| Misinformation virality | 0.3 | `sim/config.py:150` | 0.2-0.5 |
| Truth virality | 0.05 | `sim/config.py:165` | 0.03-0.1 |
| Misinformation memeticity | 0.25 | `sim/config.py:149` | 0.2-0.4 |
| Truth memeticity | 0.08 | `sim/config.py:164` | 0.05-0.15 |
| Adoption threshold | 0.75 (75%) | `sim/config.py:184` | 0.7-0.85 |
| Truth protection decay | 0.92 (8%/day) | `sim/simulation.py:316` | 0.85-0.95 |

## Common Adjustments

### If Spread is Too Fast

**Symptoms**: 
- Adoption reaches 50% in <10 days
- Max daily increase >15%
- Abrupt S-curves instead of gradual

**Solutions**:
1. **Reduce base share rate**: Change `base_share_rate` from 0.015 to 0.01 (1%)
2. **Reduce virality**: 
   - Misinformation: 0.3 → 0.2
   - Truth: 0.05 → 0.033 (maintains 6x ratio)
3. **Reduce memeticity**:
   - Misinformation: 0.25 → 0.2
   - Truth: 0.08 → 0.05
4. **Increase adoption threshold**: Change from 0.75 to 0.8 or 0.85

**Example**:
```python
# In sim/config.py
base_share_rate: float = 0.01  # Reduced from 0.015

GENERAL_MISINFORMATION_DEFAULTS = {
    "virality": 0.2,  # Reduced from 0.3
    "memeticity": 0.2,  # Reduced from 0.25
}

TRUTH_DEFAULTS = {
    "virality": 0.033,  # Reduced from 0.05 (maintains 6x ratio)
    "memeticity": 0.05,  # Reduced from 0.08
}

adoption_threshold: float = 0.8  # Increased from 0.75
```

### If Spread is Too Slow

**Symptoms**:
- Adoption reaches 50% in >30 days
- Max daily increase <3%
- Very flat curves

**Solutions**:
1. **Increase base share rate**: Change from 0.015 to 0.02 (2%) or 0.025 (2.5%)
2. **Increase virality**:
   - Misinformation: 0.3 → 0.4
   - Truth: 0.05 → 0.067 (maintains 6x ratio)
3. **Increase memeticity**:
   - Misinformation: 0.25 → 0.3
   - Truth: 0.08 → 0.1
4. **Decrease adoption threshold**: Change from 0.75 to 0.7

**Example**:
```python
# In sim/config.py
base_share_rate: float = 0.025  # Increased from 0.015

GENERAL_MISINFORMATION_DEFAULTS = {
    "virality": 0.4,  # Increased from 0.3
    "memeticity": 0.3,  # Increased from 0.25
}

TRUTH_DEFAULTS = {
    "virality": 0.067,  # Increased from 0.05 (maintains 6x ratio)
    "memeticity": 0.1,  # Increased from 0.08
}

adoption_threshold: float = 0.7  # Decreased from 0.75
```

### If Misinformation Retention is Too Low

**Symptoms**:
- Misinformation beliefs drop to 0% quickly
- No sustained misinformation presence

**Solutions**:
1. **Slow truth protection decay**: Change `decay_rate` from 0.92 to 0.95 (5% reduction per day)
2. **Reduce truth virality**: Make truth spread slower so misinformation has time to establish
3. **Delay truth introduction**: Start truth claims later in simulation

**Example**:
```python
# In sim/simulation.py and sim/disease/belief_update_torch.py
decay_rate = 0.95  # Changed from 0.92 (slower decay = 5% reduction per day)
```

### If Peak Timing Doesn't Match Literature (21 ± 7 days)

**Symptoms**:
- Peak occurs before day 14 or after day 28
- Doesn't match Cinelli et al. (2020) findings

**Solutions**:
1. **Adjust base share rate**: Lower = later peak, Higher = earlier peak
2. **Adjust virality**: Lower = later peak, Higher = earlier peak
3. **Run longer simulations**: Ensure simulation runs at least 50-100 days to observe full pattern
4. **Check network structure**: May need to adjust clustering or connectivity

## Testing Your Changes

### 1. Run Simulation
```bash
python3 -m sim run --config configs/world_baseline.yaml --out test_outputs/tuning_test
```

### 2. Analyze Results
```bash
python3 << 'EOF'
import pandas as pd
from pathlib import Path

metrics = pd.read_csv('test_outputs/tuning_test/daily_metrics.csv')

for claim in sorted(metrics['claim'].unique()):
    claim_data = metrics[metrics['claim'] == claim].sort_values('day')
    adoption = claim_data['adoption_fraction'].values
    days = claim_data['day'].values
    
    # Key metrics
    start_day = days[(adoption > 0.01).argmax()] if (adoption > 0.01).any() else None
    mid_day = days[(adoption > 0.5).argmax()] if (adoption > 0.5).any() else None
    max_increase = (adoption[1:] - adoption[:-1]).max() if len(adoption) > 1 else 0
    
    print(f"\nClaim {claim}:")
    print(f"  Days to 1%: {start_day}")
    print(f"  Days to 50%: {mid_day}")
    print(f"  Max daily increase: {max_increase:.1%}")
    
    # Check against targets
    if mid_day:
        if 14 <= mid_day <= 28:
            print(f"  ✓ Peak timing matches literature (21 ± 7 days)")
        else:
            print(f"  ⚠ Peak timing outside target range (target: 21 ± 7 days)")
    
    if max_increase > 0.15:
        print(f"  ⚠ Daily increase too fast (>15%)")
    elif max_increase > 0.05:
        print(f"  ✓ Daily increase reasonable (5-15%)")
EOF
```

### 3. Iterate

Based on results:
- If too fast → reduce parameters
- If too slow → increase parameters
- If timing wrong → adjust base share rate or virality
- If retention low → slow decay rate

## Parameter Relationships

### Maintaining 6x Virality Ratio

The literature (Vosoughi et al., 2018) shows misinformation spreads 6x faster than truth. Always maintain this ratio:

```python
# If misinformation virality = 0.3
# Then truth virality = 0.3 / 6 = 0.05

# If misinformation virality = 0.2
# Then truth virality = 0.2 / 6 = 0.033

# If misinformation virality = 0.4
# Then truth virality = 0.4 / 6 = 0.067
```

### Parameter Impact Hierarchy

1. **Base share rate**: Largest impact on spread speed
2. **Virality**: Direct multiplier effect
3. **Memeticity**: Affects exposure through media channels
4. **Adoption threshold**: Affects when agents "adopt" claims
5. **Decay rate**: Affects misinformation retention

## Best Practices

1. **Make small changes**: Adjust parameters by 10-20% at a time
2. **Test incrementally**: Test each change before making another
3. **Run multiple seeds**: Use different seeds to check robustness
4. **Check multiple metrics**: Don't just look at adoption, check belief levels, retention, etc.
5. **Document changes**: Note what you changed and why
6. **Compare to literature**: Verify results match expected ranges from research

## References

- **Vosoughi et al. (2018)**: 6x spread ratio (misinformation vs truth)
- **Cinelli et al. (2020)**: Peak timing 21 ± 7 days
- **Roozenbeek et al. (2020)**: Adoption rates 20-35%
- **Guess et al. (2019)**: Age effects (65+ share 7x more)

See `LITERATURE_ALIGNMENT_UPDATES.md` for full details.
