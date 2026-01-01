# Documentation Index

This document provides an index to all documentation files organized by category.

## Documentation Structure

All documentation is organized in the `docs/` folder:

```
docs/
├── getting-started/    # Installation, quick start, examples
├── parameters/         # Parameter tuning, adjustments, configuration
├── features/           # Agent architecture, presets, implementations
├── research/           # Literature alignment, bibliography, methods
├── development/        # Architecture, contributing, git setup
└── reference/          # This index and quick reference
```

## Getting Started

**Location**: `docs/getting-started/`

1. **[README.md](getting-started/README.md)** - Complete project documentation, installation, quick start
2. **[EXAMPLE_CONFIGS.md](getting-started/EXAMPLE_CONFIGS.md)** - Example configuration files and usage

**Use these when**: You're new to the project, installing, or running your first simulation.

## Parameters

**Location**: `docs/parameters/`

1. **[PARAMETER_ADJUSTMENTS.md](parameters/PARAMETER_ADJUSTMENTS.md)** - **START HERE** - Current parameter values, what changed, and why
2. **[PARAMETER_TUNING_GUIDE.md](parameters/PARAMETER_TUNING_GUIDE.md)** - Step-by-step guide for adjusting parameters
3. **[PARAMETER_DETERMINATION.md](parameters/PARAMETER_DETERMINATION.md)** - How parameters were determined
4. **[PARAMETER_EXTRACTION_WORKSHOP.md](parameters/PARAMETER_EXTRACTION_WORKSHOP.md)** - Parameter extraction methodology

**Use these when**: You need to understand or adjust simulation parameters.

### Parameter Reference
- **Base share rate**: 0.015 (1.5%) - `sim/config.py:321`
- **Misinformation virality**: 0.3 - `sim/config.py:150`
- **Truth virality**: 0.05 - `sim/config.py:165` (maintains 6x ratio)
- **Misinformation memeticity**: 0.25 - `sim/config.py:149`
- **Truth memeticity**: 0.08 - `sim/config.py:164`
- **Adoption threshold**: 0.75 (75%) - `sim/config.py:184`
- **Truth protection decay**: 0.92 (8%/day) - `sim/simulation.py:316`

## Features

**Location**: `docs/features/`

1. **[AGENTS.md](features/AGENTS.md)** - Agent architecture and cognitive models
2. **[CULTURAL_IDENTITY_IMPLEMENTATION.md](features/CULTURAL_IDENTITY_IMPLEMENTATION.md)** - Cultural identity system
3. **[EMOTION_PRESETS.md](features/EMOTION_PRESETS.md)** - Emotion system and presets
4. **[MISINFORMATION_PRESETS.md](features/MISINFORMATION_PRESETS.md)** - Misinformation strain presets
5. **[PRESET_SYSTEM_SUMMARY.md](features/PRESET_SYSTEM_SUMMARY.md)** - Preset system overview
6. **[NEIGHBORHOOD_DIFFERENTIATION_FIX.md](features/NEIGHBORHOOD_DIFFERENTIATION_FIX.md)** - Neighborhood differentiation implementation

**Use these when**: You need to understand specific features or systems.

## Research

**Location**: `docs/research/`

1. **[LITERATURE_ALIGNMENT_UPDATES.md](research/LITERATURE_ALIGNMENT_UPDATES.md)** - Literature-based parameter updates and citations
2. **[RESEARCH_GUIDE.md](research/RESEARCH_GUIDE.md)** - Research methodology and validation
3. **[RESEARCH_BIBLIOGRAPHY.md](research/RESEARCH_BIBLIOGRAPHY.md)** - Complete bibliography
4. **[METHODS.md](research/METHODS.md)** - Formal methods with equations
5. **[SPREAD_PATTERN_ISSUES.md](research/SPREAD_PATTERN_ISSUES.md)** - **USE THIS** - Common spread pattern problems and solutions

**Use these when**: You need to understand research foundations, literature alignment, or troubleshoot spread patterns.

## Development

**Location**: `docs/development/`

1. **[ARCHITECTURE.md](development/ARCHITECTURE.md)** - System architecture and module structure
2. **[CONTRIBUTING.md](development/CONTRIBUTING.md)** - Contribution guidelines
3. **[ENHANCEMENT_PLAN.md](development/ENHANCEMENT_PLAN.md)** - Future enhancements and roadmap
4. **[GIT_SETUP.md](development/GIT_SETUP.md)** - Git setup instructions
5. **[PUSH_INSTRUCTIONS.md](development/PUSH_INSTRUCTIONS.md)** - How to push changes

**Use these when**: You're contributing code or understanding the architecture.

## Common Tasks

### I want to...
- **Run a simulation**: See [Getting Started README](getting-started/README.md) "Quick Start" section
- **Adjust parameters**: See [Parameter Tuning Guide](parameters/PARAMETER_TUNING_GUIDE.md)
- **Understand current parameters**: See [Parameter Adjustments](parameters/PARAMETER_ADJUSTMENTS.md)
- **Fix spread pattern issues**: See [Spread Pattern Issues](research/SPREAD_PATTERN_ISSUES.md)
- **Understand literature alignment**: See [Literature Alignment Updates](research/LITERATURE_ALIGNMENT_UPDATES.md)
- **Analyze results**: See `test_outputs/README.md`
- **Add new features**: See [Contributing](development/CONTRIBUTING.md) and [Architecture](development/ARCHITECTURE.md)

## Key Files by Topic

### Parameter Values
- `sim/config.py` - All default parameter values
- [Parameter Adjustments](parameters/PARAMETER_ADJUSTMENTS.md) - Current values and changes
- [Parameter Tuning Guide](parameters/PARAMETER_TUNING_GUIDE.md) - How to adjust

### Spread Patterns
- [Spread Pattern Issues](research/SPREAD_PATTERN_ISSUES.md) - Problems and solutions
- [Parameter Adjustments](parameters/PARAMETER_ADJUSTMENTS.md) - What was changed and why
- `sim/simulation.py` - Main simulation loop
- `sim/disease/sharing.py` - Sharing probability calculation

### Truth Protection
- `sim/simulation.py` lines 299-316 - Truth protection implementation
- `sim/disease/belief_update_torch.py` lines 70-74 - Belief update truth protection
- [Parameter Adjustments](parameters/PARAMETER_ADJUSTMENTS.md) - Decay rate explanation

### Literature Alignment
- [Literature Alignment Updates](research/LITERATURE_ALIGNMENT_UPDATES.md) - All literature-based updates
- [Research Bibliography](research/RESEARCH_BIBLIOGRAPHY.md) - Complete citations
- [Parameter Adjustments](parameters/PARAMETER_ADJUSTMENTS.md) - Current parameter values

## Quick Reference Commands

```bash
# Run simulation
python3 -m sim run --config configs/world_baseline.yaml --out test_outputs/my_run

# Run all world configs
python3 run_all_world_simulations.py

# Analyze spread patterns
python3 << 'EOF'
import pandas as pd
metrics = pd.read_csv('test_outputs/my_run/daily_metrics.csv')
# ... analysis code ...
EOF
```

## Documentation Updates

**Last Updated**: January 2025

**Recent Changes**:
- Documentation organized into folders by content
- Parameter values updated for realistic spread patterns
- Truth protection changed to gradual decay
- Base share rate reduced to 1.5%
- Virality and memeticity reduced
- Adoption threshold increased to 75%

**See**: [Parameter Adjustments](parameters/PARAMETER_ADJUSTMENTS.md) for full details
