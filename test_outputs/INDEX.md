# Test Outputs Index

Quick reference for all test runs in this directory.

## Phoenix Simulations

| Run Name | Description | Agents | Claims | Key Files |
|----------|-------------|--------|--------|-----------|
| **phoenix_neighborhood_test** | Comprehensive neighborhood differentiation test | 5,000 | 4 | `neighborhood_differentiation_report.txt`, `neighborhood_analysis.json`, `EXECUTIVE_SUMMARY.md` |
| **phoenix_large_10k_per_neighborhood** | Large-scale simulation (10k per neighborhood) | 60,000 | 4 | `daily_metrics.csv`, `belief_snapshots.parquet` |
| **phoenix_with_misinfo** | Phoenix with truth + 3 misinformation claims | 5,000 | 4 | `daily_metrics.csv`, `summary.json` |
| **phoenix_run** | Initial Phoenix simulation | 5,000 | 1 | `daily_metrics.csv` |
| **phoenix_test** | Phoenix test configuration | 5,000 | 1 | `daily_metrics.csv` |
| **phoenix_misinfo** | Phoenix with misinformation only | 5,000 | 1 | `daily_metrics.csv` |
| **phoenix_detailed** | Detailed run with frequent snapshots | 5,000 | 4 | `daily_metrics.csv` |

## Quick Access

### Most Important Runs

1. **phoenix_neighborhood_test/** - Full analysis with neighborhood differentiation validation
2. **phoenix_large_10k_per_neighborhood/** - Large-scale validation (60k agents)

### Analysis Files

- `phoenix_neighborhood_test/neighborhood_differentiation_report.txt` - Comprehensive report
- `phoenix_neighborhood_test/neighborhood_analysis.json` - Structured data
- `phoenix_neighborhood_test/EXECUTIVE_SUMMARY.md` - Quick summary

### Common Files in Each Run

- `daily_metrics.csv` - Time-series metrics for all claims
- `summary.json` - Summary statistics
- `config_resolved.yaml` - Final configuration used
- `plots/` - Visualization plots
- `belief_snapshots.parquet` - Belief states (if enabled)

## Running Tests

```bash
# Run neighborhood differentiation test
python3 test_neighborhood_differentiation.py

# Results saved to: test_outputs/phoenix_neighborhood_test/
```

## Notes

- All runs use Phoenix metro area configuration with 6 neighborhoods
- Truth protection mechanism is enabled in most runs
- Neighborhood differentiation fix is validated in `phoenix_neighborhood_test`
