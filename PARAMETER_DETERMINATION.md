# How Parameters Are Determined for Misinformation and Truth Claims

This document explains the different methods used to determine realistic parameters for misinformation and truth claims in the simulation.

## Overview

There are **three main approaches** to parameter determination:

1. **Empirical Calibration** (Automated) - Uses ABC (Approximate Bayesian Computation) to match real-world data
2. **Literature-Based Defaults** (Manual) - Set parameters based on research findings
3. **Manual Configuration** (Custom) - Set parameters directly in YAML config files

---

## 1. Empirical Calibration (Automated)

The simulation includes an **ABC (Approximate Bayesian Computation) calibration framework** that automatically finds parameters matching real-world data.

### How It Works

1. **Define Empirical Targets** (`sim/calibration/empirical_targets.py`):
   - Target statistics from research (e.g., "25% adoption rate")
   - Tolerance ranges (e.g., ±10%)
   - Sources cited (e.g., Vosoughi et al., 2018)

2. **Define Parameter Priors** (`sim/calibration/priors.py`):
   - Reasonable ranges for each parameter
   - Based on theory and prior studies
   - Example: `memeticity` uniform(0.3, 0.8)

3. **Run ABC Calibration**:
   ```python
   from sim.calibration.abc import ABCCalibrator
   
   calibrator = ABCCalibrator(
       empirical_targets=GENERAL_MISINFORMATION_TARGETS,
       priors=define_parameter_priors()
   )
   
   # Find parameters that match empirical targets
   calibrated_params = calibrator.calibrate(n_samples=1000)
   ```

### Empirical Targets Used

Based on research literature:

**COVID-19 Misinformation:**
- Final adoption: 28% ± 8% (Roozenbeek et al., 2020)
- Days to peak: 21 ± 7 days (Cinelli et al., 2020)
- Spread rate ratio (false vs true): 6.0x (Vosoughi et al., 2018)

**General Misinformation:**
- Final adoption: 25% ± 10%
- Adopter mean belief: 0.75 ± 0.08
- Structural virality: 3.5 ± 1.0 (Goel et al., 2016)

**Election Misinformation:**
- Exposure fraction: 25% ± 5% (Guess et al., 2018)
- Share given exposure: 8.5% ± 2% (Guess et al., 2019)
- Age sharing ratio: 7.0x (65+ vs young)

---

## 2. Literature-Based Defaults (Manual)

Parameters can be set based on research findings without running calibration.

### Key Research Sources

#### Vosoughi et al. (2018) - "The spread of true and false news online"
**Finding**: False news spreads **6x faster** than true news

**Implications for Parameters:**
- **Truth `virality`**: 0.17 (baseline)
- **Misinformation `virality`**: 1.0 (6x truth)
- **Truth `memeticity`**: 0.25 (lower shareability)
- **Misinformation `memeticity`**: 0.72 (highly shareable)

#### Roozenbeek et al. (2020) - COVID-19 misinformation
**Finding**: 20-35% of population adopted at least one major COVID conspiracy

**Implications:**
- Target adoption rates: 20-35%
- Calibrate `virality`, `memeticity`, `emotional_profile` to achieve this

#### Guess et al. (2019) - Demographics of misinformation sharing
**Finding**: 
- Older adults (65+) share 7x more than young adults
- Higher emotional appeal drives sharing

**Implications:**
- **Misinformation `emotional_profile`**: High fear (0.5-0.7), moderate anger (0.4-0.6)
- **Truth `emotional_profile`**: Low fear (0.0-0.1), moderate hope (0.5-0.6)

#### Lewandowsky et al. (2012) - Debunking misinformation
**Finding**: Vague claims are harder to debunk

**Implications:**
- **Misinformation `falsifiability`**: 0.3-0.5 (low = hard to debunk)
- **Truth `falsifiability`**: 1.0 (fully verifiable)

#### Zannettou et al. (2018) - Stealth misinformation
**Finding**: Some misinformation evades detection

**Implications:**
- **Misinformation `stealth`**: 0.5-0.6 (evades moderation)
- **Truth `stealth`**: 0.0 (transparent)

### Recommended Parameter Ranges

Based on the research above:

#### Misinformation Claims

```yaml
memeticity: 0.65-0.75          # Highly shareable (Vosoughi et al.)
virality: 1.0-1.2               # Spreads 6x faster than truth
emotional_profile:
  fear: 0.5-0.7                 # High fear (Guess et al.)
  anger: 0.4-0.6                # Moderate-high anger
  hope: 0.1-0.2                 # Low hope
falsifiability: 0.3-0.5        # Hard to debunk (Lewandowsky et al.)
stealth: 0.5-0.6                # Evades detection (Zannettou et al.)
mutation_rate: 0.05-0.08        # Rapid evolution (Zollo et al.)
persistence: 0.2-0.3            # Beliefs fade without reinforcement
violation_risk: 0.3-0.4         # Moderate policy violations
```

#### Truth Claims

```yaml
memeticity: 0.2-0.3             # Spreads more deliberately
virality: 0.15-0.2               # 6x slower than misinformation
emotional_profile:
  fear: 0.0-0.1                  # Low fear (factual)
  anger: 0.0                      # No anger
  hope: 0.5-0.6                  # Moderate hope
falsifiability: 1.0              # Fully verifiable
stealth: 0.0                     # Transparent
mutation_rate: 0.0                # Doesn't mutate
persistence: 0.7-0.8             # High persistence once adopted
violation_risk: 0.0              # No policy violations
is_true: true
```

---

## 3. Manual Configuration (Custom)

You can set parameters directly in YAML config files.

### Example: Your Current Config

From `configs/world_phoenix_truth_random.yaml`:

```yaml
strains:
  # Truth claim
  - name: "official_health_guidance"
    memeticity: 0.35              # Manually set
    virality: 0.6                  # Manually set
    emotional_profile: 
      fear: 0.1
      anger: 0.0
      hope: 0.2
    falsifiability: 1.0           # Truth is verifiable
    stealth: 0.0                   # No stealth
    is_true: true
  
  # Misinformation claim
  - name: "random_misinformation"
    memeticity: 0.66              # Manually set
    virality: 1.17                # Manually set
    emotional_profile: 
      fear: 0.23
      anger: 0.33
      hope: 0.30
    falsifiability: 0.41          # Harder to debunk
    stealth: 0.38                 # Some stealth
    is_true: false
```

### How to Choose Manual Values

1. **Start with literature-based defaults** (see section 2)
2. **Run test simulations** and observe outcomes
3. **Adjust parameters** to match desired behavior:
   - Want faster spread? Increase `virality` or `memeticity`
   - Want harder to debunk? Decrease `falsifiability`, increase `stealth`
   - Want more persistent beliefs? Increase `persistence`
4. **Compare to empirical targets** (see `sim/calibration/empirical_targets.py`)

---

## Parameter Relationships

Understanding how parameters interact helps determine realistic combinations:

### Spread Speed
- **Primary**: `virality` (direct multiplier)
- **Secondary**: `memeticity` (affects exposure)
- **Emotional**: High `fear`/`anger` increases sharing

### Debunking Resistance
- **Primary**: Low `falsifiability` (hard to fact-check)
- **Secondary**: High `stealth` (evades detection)
- **Combined**: `debunk_effectiveness ∝ falsifiability × (1 - stealth)`

### Belief Persistence
- **Primary**: `persistence` (reduces decay)
- **Secondary**: High `emotional_profile` (emotional attachment)
- **Effect**: `decay_rate = base_decay × (1 - persistence)`

### Moderation Resistance
- **Primary**: High `stealth` (evades detection)
- **Secondary**: Low `violation_risk` (subtle claims)
- **Combined**: `moderation_penalty ∝ violation_risk × (1 - stealth)`

---

## Validation Checklist

When setting parameters manually, check:

- [ ] **Adoption rate**: Does final adoption match research (20-35% for misinformation)?
- [ ] **Spread speed**: Does misinformation spread ~6x faster than truth?
- [ ] **Demographics**: Do older adults adopt more (if modeling age effects)?
- [ ] **Polarization**: Does polarization increase over time?
- [ ] **Cascade structure**: Are most cascades small with few viral ones?

Run validation:
```bash
python scripts/run_validation.py --config your_config.yaml
```

---

## Using the Calibration Framework

To automatically find parameters matching empirical targets:

```python
from sim.calibration.abc import ABCCalibrator
from sim.calibration.empirical_targets import GENERAL_MISINFORMATION_TARGETS
from sim.calibration.priors import define_parameter_priors

# Initialize calibrator
calibrator = ABCCalibrator(
    empirical_targets=GENERAL_MISINFORMATION_TARGETS,
    priors=define_parameter_priors(),
    tolerance=0.1  # Acceptable deviation from targets
)

# Run calibration
calibrated_params = calibrator.calibrate(
    n_samples=1000,      # Number of simulations
    n_accepted=50        # Keep top 50 matches
)

# Use calibrated parameters
print(calibrated_params)
```

---

## Summary

| Method | Use Case | Effort | Accuracy |
|--------|----------|--------|----------|
| **Empirical Calibration** | Research, publication | High | Highest |
| **Literature-Based** | Quick setup, exploration | Low | High |
| **Manual Configuration** | Custom scenarios, testing | Medium | Variable |

**Recommendation**: 
- Start with **literature-based defaults** for quick exploration
- Use **empirical calibration** for research/publication
- Use **manual configuration** for specific scenarios or when you know what you want

---

## References

1. Vosoughi, S., Roy, D., & Aral, S. (2018). The spread of true and false news online. *Science*.
2. Roozenbeek, J., et al. (2020). Susceptibility to misinformation about COVID-19. *Royal Society Open Science*.
3. Guess, A., et al. (2019). Less than you think: Prevalence and predictors of fake news dissemination on Facebook. *Science Advances*.
4. Lewandowsky, S., et al. (2012). Misinformation and its correction. *Psychological Science*.
5. Zannettou, S., et al. (2018). The web centipede: Understanding how web communities influence each other. *WWW*.
6. Goel, S., et al. (2016). The structural virality of online diffusion. *Management Science*.
