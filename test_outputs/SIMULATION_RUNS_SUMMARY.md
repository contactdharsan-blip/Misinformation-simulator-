# Simulation Runs Summary

This document provides an overview of all simulation runs in the test_outputs directory, updated with literature-aligned parameters.

## Total Runs: 25 simulation runs

## Run Categories

### 1. Literature-Aligned Runs
**Location**: `literature_aligned_runs/`

Simulations specifically run to validate literature alignment:

- **baseline_literature_aligned** - Baseline with literature-aligned parameters
- **phoenix_literature_aligned** - Phoenix with truth + 3 misinformation claims

**Key Features**:
- Age-based sharing (65+ share 7x more)
- Education-belief correlation (-0.25)
- Correction effectiveness (25%)
- Base share rate (8.5%)
- Spread ratio (6x false vs true)

### 2. World Simulations Batch
**Location**: `world_simulations_YYYYMMDD_HHMMSS/`

Batch runs of all world configurations (12 simulations):

- `world_baseline/` - Baseline configuration
- `world_high_trust_gov/` - High government trust
- `world_low_trust_gov/` - Low government trust  
- `world_strong_moderation/` - Strong moderation
- `world_collapsed_local_media/` - Collapsed local media
- `world_high_religion_hub/` - High religion hub
- `world_outrage_algorithm/` - Outrage algorithm
- `world_phoenix/` - Phoenix metro area
- `world_phoenix_multi_misinformation/` - Multiple misinformation claims
- `world_phoenix_truth_random/` - Truth + random misinformation
- `phoenix_test/` - Phoenix test config
- `phoenix_with_misinfo/` - Phoenix with misinformation

### 3. Phoenix Test Runs
**Location**: Root of `test_outputs/`

Individual Phoenix test runs:

- `phoenix_neighborhood_test/` - Comprehensive neighborhood differentiation test
- `phoenix_large_10k_per_neighborhood/` - Large-scale (60k agents, 10k per neighborhood)
- `phoenix_with_misinfo/` - Phoenix with truth + 3 misinformation
- `phoenix_run/` - Initial Phoenix run
- `phoenix_test/` - Phoenix test configuration
- `phoenix_misinfo/` - Phoenix with misinformation only
- `phoenix_detailed/` - Detailed run with frequent snapshots

### 4. Other Runs
- `baseline/` - Baseline simulation
- `collapsed_local_media/` - Collapsed media scenario
- `high_religion_hub/` - High religion scenario
- `high_trust_gov/` - High trust scenario

## Literature Alignment Status

### Parameters Aligned ✓
- ✅ Age-based sharing: 65+ share 7x more (Guess et al., 2019)
- ✅ Education-belief correlation: -0.25 (Pennycook & Rand, 2021)
- ✅ Correction effectiveness: 25% (Walter & Tukachinsky, 2020)
- ✅ Base share rate: 8.5% (Guess et al., 2019)
- ✅ Spread ratio: 6x false vs true (Vosoughi et al., 2018)

### Results Analysis

**Truth Claims**:
- Reach 100% adoption quickly (days 8-11)
- Truth protection mechanism working as expected
- Suppresses misinformation effectively

**Misinformation Claims**:
- Initial spread observed
- Suppressed by truth protection by day 25-50
- Peak timing varies (days 0-6 observed)
- Final adoption: 0% (due to truth protection)

**Note**: With truth protection enabled, misinformation is intentionally suppressed. To observe misinformation spread patterns matching literature (20-35% adoption, peak at 21±7 days), run simulations:
1. Without truth claims, OR
2. With truth protection disabled/delayed, OR
3. With lower truth virality to allow misinformation to spread first

## Running New Simulations

### Run all world configs:
```bash
python3 run_all_world_simulations.py
```

### Run literature-aligned tests:
```bash
python3 update_test_outputs.py
```

### Run specific config:
```bash
python3 -m sim run --config configs/world_baseline.yaml --out test_outputs/my_run
```

## File Structure

Each simulation run contains:
- `daily_metrics.csv` - Time-series data
- `belief_snapshots.parquet` - Belief states (if enabled)
- `summary.json` - Summary statistics
- `config_resolved.yaml` - Final configuration
- `plots/` - Visualization plots
- `run_metadata.json` - Metadata
- `strain_info.json` - Strain information

## Notes

- All simulations use literature-aligned parameters
- Truth protection is enabled in most configs (suppresses misinformation)
- Age-based sharing effects are active
- Education effects are active
- Correction effectiveness is set to 25%
