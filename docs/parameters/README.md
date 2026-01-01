# Parameters Documentation

This folder contains all documentation related to simulation parameters, tuning, and configuration.

## Files

- **[PARAMETER_ADJUSTMENTS.md](PARAMETER_ADJUSTMENTS.md)** - **START HERE** - Current parameter values, recent changes, and rationale
- **[PARAMETER_TUNING_GUIDE.md](PARAMETER_TUNING_GUIDE.md)** - Step-by-step guide for adjusting parameters to achieve desired results
- **[PARAMETER_DETERMINATION.md](PARAMETER_DETERMINATION.md)** - How parameters were originally determined
- **[PARAMETER_EXTRACTION_WORKSHOP.md](PARAMETER_EXTRACTION_WORKSHOP.md)** - Parameter extraction methodology and workshop notes

## Quick Reference

### Current Parameter Values
- Base share rate: **0.015** (1.5%) - `sim/config.py:321`
- Misinformation virality: **0.3** - `sim/config.py:150`
- Truth virality: **0.05** - `sim/config.py:165` (maintains 6x ratio)
- Misinformation memeticity: **0.25** - `sim/config.py:149`
- Truth memeticity: **0.08** - `sim/config.py:164`
- Adoption threshold: **0.75** (75%) - `sim/config.py:184`
- Truth protection decay: **0.92** (8%/day) - `sim/simulation.py:316`

## Common Tasks

- **Understanding current parameters**: See [PARAMETER_ADJUSTMENTS.md](PARAMETER_ADJUSTMENTS.md)
- **Adjusting parameters**: See [PARAMETER_TUNING_GUIDE.md](PARAMETER_TUNING_GUIDE.md)
- **Troubleshooting spread patterns**: See [../research/SPREAD_PATTERN_ISSUES.md](../research/SPREAD_PATTERN_ISSUES.md)
