# Spread Pattern Issues Analysis

## Current Problems

### 1. Abrupt Spreading
- **Truth claims**: Reach 50% adoption in 6-8 days, 90% in 7-9 days
- **Max daily increase**: 60-88% per day (extremely unrealistic)
- **Literature expectation**: Gradual S-curve over 21 ± 7 days

### 2. Low Misinformation Retention
- **Misinformation claims**: Peak at 0.1-0.5%, then drop to 0%
- **Retention**: 0% (all misinformation beliefs zeroed)
- **Literature expectation**: 20-35% adoption with sustained belief

## Root Causes

### 1. Truth Protection Too Strong
- Once agent adopts truth (belief > 0.8), ALL misinformation beliefs permanently zeroed
- This completely suppresses misinformation spread
- Location: `sim/simulation.py` lines 309-315, `sim/disease/belief_update_torch.py` lines 70-76

### 2. Parameters Too Aggressive
- **Base share rate**: 8.5% (Guess et al., 2019) - but this is for exposure, not adoption
- **Virality**: Truth 0.167, Misinfo 1.0 - still too high
- **Memeticity**: Truth 0.25, Misinfo 0.70 - too high
- **Age multipliers**: 7x for 65+ amplifies spread dramatically
- **Adoption threshold**: 0.8 (80%) - reasonable but spread happens too fast

### 3. Network Structure
- Likely too connected (small world network)
- High clustering coefficient causes rapid cascades
- No realistic barriers to adoption

### 4. Missing Realistic Barriers
- No skepticism delays
- No trust requirements
- No gradual belief accumulation
- No social proof thresholds

## Proposed Solutions

### 1. Reduce Base Share Rate
**Current**: 8.5%  
**Proposed**: 2-3% (base probability of sharing, not adoption)

**Rationale**: 8.5% from Guess et al. (2019) is for sharing given exposure, but we need base probability before exposure effects.

### 2. Reduce Virality
**Current**: Truth 0.167, Misinfo 1.0  
**Proposed**: Truth 0.05-0.1, Misinfo 0.3-0.5

**Rationale**: Maintain 6x ratio but reduce absolute values to slow spread.

### 3. Reduce Memeticity
**Current**: Truth 0.25, Misinfo 0.70  
**Proposed**: Truth 0.1-0.15, Misinfo 0.3-0.4

**Rationale**: Lower memeticity = less shareable = slower spread.

### 4. Weaken Truth Protection
**Current**: Permanent zeroing of all misinformation beliefs  
**Proposed Options**:
- **Option A**: Only zero misinformation beliefs above threshold (e.g., > 0.5)
- **Option B**: Gradual decay instead of instant zeroing
- **Option C**: Only protect against specific misinformation claims (not all)
- **Option D**: Delay truth protection (only activate after truth belief > 0.9 for N days)

**Recommended**: Option B (gradual decay) + Option D (delayed activation)

### 5. Increase Adoption Threshold or Make Gradual
**Current**: 0.8 (80%)  
**Proposed**: 0.85-0.9 OR gradual adoption curve

**Rationale**: Higher threshold = slower adoption = more realistic spread.

### 6. Add Skepticism Barriers
**Proposed**: Agents with high skepticism require multiple exposures before adopting
- Skepticism > 0.7: Requires 3-5 exposures
- Skepticism > 0.5: Requires 2-3 exposures
- Skepticism < 0.5: Normal adoption

### 7. Reduce Age Multiplier Impact
**Current**: 7x for 65+  
**Proposed**: Cap age multiplier effect or reduce to 3-4x

**Rationale**: 7x is correct from literature, but combined with other parameters causes explosive spread.

### 8. Add Network Constraints
**Proposed**: 
- Reduce clustering coefficient
- Add homophily barriers (agents less likely to adopt from dissimilar others)
- Add trust requirements (agents need trust > threshold to adopt)

## Implementation Priority

1. **High Priority**:
   - Reduce base share rate (2-3%)
   - Reduce virality (truth 0.05-0.1, misinfo 0.3-0.5)
   - Weaken truth protection (gradual decay + delayed activation)

2. **Medium Priority**:
   - Reduce memeticity
   - Add skepticism barriers
   - Increase adoption threshold

3. **Low Priority**:
   - Adjust network structure
   - Reduce age multiplier impact
   - Add trust requirements

## Expected Outcomes

After fixes:
- **Spread pattern**: Gradual S-curve over 14-28 days
- **Peak timing**: 21 ± 7 days (matching literature)
- **Adoption rates**: 20-35% for misinformation
- **Retention**: Sustained belief levels (not zeroed)
- **Daily increase**: Max 5-15% per day (not 60-88%)

## Current Status

**Status**: Parameters have been adjusted but spread may still be faster than ideal.

**Current Parameter Values**:
- Base share rate: **0.015** (1.5%)
- Misinformation virality: **0.3**
- Truth virality: **0.05** (maintains 6x ratio)
- Misinformation memeticity: **0.25**
- Truth memeticity: **0.08**
- Adoption threshold: **0.75** (75%)
- Truth protection decay: **8% per day** (0.92 multiplier)

## Testing Instructions

### Run Test Simulation

```bash
# Run a test simulation
python3 -m sim run \
  --config configs/world_phoenix_with_misinfo.yaml \
  --out test_outputs/spread_test
```

### Analyze Spread Patterns

```bash
python3 << 'EOF'
import pandas as pd
from pathlib import Path

output_dir = Path('test_outputs/spread_test')
metrics = pd.read_csv(output_dir / 'daily_metrics.csv')

print("="*80)
print("SPREAD PATTERN ANALYSIS")
print("="*80)

for claim in sorted(metrics['claim'].unique()):
    claim_data = metrics[metrics['claim'] == claim].sort_values('day')
    adoption = claim_data['adoption_fraction'].values
    days = claim_data['day'].values
    
    print(f"\nClaim {claim}:")
    
    # Key metrics
    start_day = days[(adoption > 0.01).argmax()] if (adoption > 0.01).any() else None
    mid_day = days[(adoption > 0.5).argmax()] if (adoption > 0.5).any() else None
    high_day = days[(adoption > 0.9).argmax()] if (adoption > 0.9).any() else None
    
    if len(adoption) > 1:
        max_increase = (adoption[1:] - adoption[:-1]).max()
        max_increase_day = days[1:][(adoption[1:] - adoption[:-1]).argmax()]
    
    final = adoption[-1]
    peak = adoption.max()
    retention = final / peak if peak > 0 else 0
    
    print(f"  Days to 1%: {start_day}")
    if mid_day:
        print(f"  Days to 50%: {mid_day}")
    if high_day:
        print(f"  Days to 90%: {high_day}")
    if len(adoption) > 1:
        print(f"  Max daily increase: {max_increase:.1%} (day {max_increase_day})")
        if max_increase > 0.15:
            print(f"    ⚠ WARNING: Daily increase > 15% (too fast)")
        elif max_increase > 0.05:
            print(f"    ✓ Daily increase reasonable (5-15%)")
        else:
            print(f"    ✓ Daily increase slow (<5%)")
    
    print(f"  Peak adoption: {peak:.1%}")
    print(f"  Final adoption: {final:.1%}")
    print(f"  Retention: {retention:.1%}")
    
    # Check against literature targets
    if claim > 0:  # Misinformation claims
        if 0.20 <= final <= 0.35:
            print(f"    ✓ Adoption rate matches literature (20-35%)")
        else:
            print(f"    ⚠ Adoption rate {final:.1%} outside target range")
        
        if mid_day and 14 <= mid_day <= 28:
            print(f"    ✓ Peak timing matches literature (21 ± 7 days)")
        elif mid_day:
            print(f"    ⚠ Peak at day {mid_day} (target: 21 ± 7 days)")
EOF
```

### Validation Checklist

Run simulations with adjusted parameters and verify:
1. ✅ Spread curves are gradual S-curves (not abrupt jumps)
2. ✅ Peak timing matches 21 ± 7 days (may need longer simulations)
3. ✅ Adoption rates are 20-35% for misinformation
4. ✅ Misinformation retention > 0% (not instant zeroing)
5. ✅ Daily increases are reasonable (5-15% max, not 60-88%)

### Troubleshooting

**If spread is still too fast**:
- Reduce `base_share_rate` to 0.01 (1%)
- Reduce `virality` further (misinfo 0.2, truth 0.033)
- Increase `adoption_threshold` to 0.8 or 0.85
- Check network structure (may be too connected)

**If spread is too slow**:
- Increase `base_share_rate` to 0.02 (2%)
- Increase `virality` (misinfo 0.4, truth 0.067)
- Decrease `adoption_threshold` to 0.7

**If misinformation retention is 0%**:
- Check that truth protection decay is working (should be 8% per day)
- Verify gradual decay is implemented in both `simulation.py` and `belief_update_torch.py`
- Consider slowing decay rate to 0.95 (5% reduction per day)
