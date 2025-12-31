# Neighborhood Differentiation Fix

## Problem Identified

Despite having different demographic parameters (education, income, ethnicity) across neighborhoods, adoption rates were very similar because:

1. **Traits were generated globally** - All agents received traits (skepticism, conformity, numeracy, etc.) from the same distribution, regardless of neighborhood demographics
2. **Trust was generated globally** - All agents received trust values (trust_gov, trust_church, trust_media, etc.) from the same baseline with only random jitter
3. **Neighborhood demographics were ignored** - Even though neighborhood specs included `college_educated` rates and `median_income`, these were not used to differentiate agent traits or trust

## Root Cause

In `sim/town/generator.py`:
- Line 197: `traits = generate_traits(...)` - Generated globally for all agents
- Line 198: `trust = generate_trust(...)` - Generated globally for all agents

These functions did not accept neighborhood-specific parameters, so neighborhoods with:
- High education (0.72 college_educated) vs Low education (0.18 college_educated)
- High income ($105k median) vs Low income ($38k median)

...had identical trait and trust distributions, leading to similar adoption rates.

## Solution Implemented

### 1. Made `generate_traits()` neighborhood-aware

**Location**: `sim/town/demographics.py`

**Changes**:
- Added parameters: `neighborhood_ids`, `neighborhood_education`, `neighborhood_income`
- **Education effects**:
  - Higher education → Higher skepticism (+0.15 effect)
  - Higher education → Higher numeracy (+0.2 effect)
  - Higher education → Lower conspiratorial tendency (-0.15 effect)
- **Income effects**:
  - Higher income → Lower conformity (-0.2 effect, more independent thinking)

### 2. Made `generate_trust()` neighborhood-aware

**Location**: `sim/town/demographics.py`

**Changes**:
- Added parameters: `neighborhood_ids`, `neighborhood_income`, `neighborhood_education`
- **Income effects**:
  - Higher income → Higher trust in government (+0.125 max effect)
  - Higher income → Higher trust in media (+0.1 max effect)
- **Education effects**:
  - Higher education → Higher trust in media (+0.1 effect)
  - Higher education → Lower trust in church (-0.15 effect)

### 3. Updated `generate_town()` to extract and pass neighborhood parameters

**Location**: `sim/town/generator.py`

**Changes**:
- Extracts `college_educated` and `median_income` from neighborhood specs
- Passes these parameters to `generate_traits()` and `generate_trust()`

## Expected Impact

Neighborhoods should now show differentiated adoption rates:

1. **High-education neighborhoods** (e.g., Paradise Valley, North Scottsdale):
   - Higher skepticism → Lower misinformation adoption
   - Higher numeracy → Better critical thinking
   - Higher trust in media → More exposure to debunking

2. **Low-education neighborhoods** (e.g., Maryvale, South Mountain):
   - Lower skepticism → Higher misinformation adoption
   - Lower numeracy → Less critical evaluation
   - Lower trust in media → Less exposure to corrections

3. **High-income neighborhoods**:
   - Higher trust in institutions → More exposure to official information
   - Lower conformity → More independent evaluation

4. **Low-income neighborhoods**:
   - Lower trust in institutions → Less exposure to corrections
   - Higher conformity → More susceptible to social influence

## Testing Recommendations

1. Run simulations with Phoenix config (`world_phoenix.yaml`)
2. Compare adoption rates across neighborhoods:
   - Paradise Valley (high edu/income) vs Maryvale (low edu/income)
   - North Scottsdale (high edu/income) vs South Mountain (low edu/income)
3. Verify that adoption rates now differ meaningfully (e.g., 10-30% difference)
4. Check that cultural matching still works (strains targeting specific groups)

## Notes

- Effects are moderate (±0.1 to ±0.2) to avoid extreme differences
- Base distributions still apply (neighborhood effects are adjustments)
- Random jitter still applies on top of neighborhood effects
- If neighborhood specs are not provided, behavior is unchanged (backward compatible)
