# Town Misinformation Contagion Simulator

A cognitively-grounded agent-based model for studying how misinformation spreads through social networks.

## Quick Start

```bash
# Install dependencies
pip install -e .

# Run a simulation
python3 -m sim run --config configs/world_baseline.yaml --out test_outputs/baseline
```

## Documentation

All documentation is organized in the `docs/` folder:

- **[Getting Started](docs/getting-started/)** - Installation, quick start, examples
- **[Parameters](docs/parameters/)** - Parameter tuning, adjustments, configuration
- **[Features](docs/features/)** - Agent architecture, presets, implementations
- **[Research](docs/research/)** - Literature alignment, bibliography, methods
- **[Development](docs/development/)** - Architecture, contributing, git setup
- **[Reference](docs/reference/)** - Documentation index, quick reference

## Key Documentation Files

- **[README (Full)](docs/getting-started/README.md)** - Complete project documentation
- **[Parameter Tuning Guide](docs/parameters/PARAMETER_TUNING_GUIDE.md)** - How to adjust parameters
- **[Documentation Index](docs/reference/DOCUMENTATION_INDEX.md)** - Complete documentation index

## Current Parameter Values

- **Base share rate**: 0.012 (1.2%)
- **Misinformation virality**: 0.3
- **Truth virality**: 0.05 (maintains 6x ratio)
- **Adoption threshold**: 0.8 (80%)
- **Truth protection decay**: 0.92 (8% per day)
- **State Model**: SEDPNR (Nature 2024 calibrated)
- **Cognition**: Dual-Process (System 1/2) with identity threat detection
- **Demographics**: Biased media diets by age/ethnicity
- **Restrained Threshold**: 3 shares (Engagement fatigue)

## License

MIT License - see [LICENSE](LICENSE) for details.
