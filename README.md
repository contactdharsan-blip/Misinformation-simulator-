# Town Misinformation Contagion Simulator

A cognitively-grounded agent-based model for studying how misinformation spreads through social networks. The simulator builds synthetic towns with realistic social structures, implements psychological theories of belief formation, and enables testing of intervention strategies.

## Features

### Cognitive Architecture
- **Dual-Process Theory** (Kahneman, 2011): System 1 (fast/intuitive) and System 2 (slow/analytical) processing
- **Motivated Reasoning**: Identity-protective cognition with confirmation bias and psychological reactance
- **Attention Economics**: Bounded rationality with finite cognitive resources
- **Source Memory**: Credibility tracking and sleeper effects

### Social Network Modeling
- **Multi-layer Networks**: Family, workplace, school, church, and neighborhood ties
- **Homophily**: Belief-similarity-based connection patterns
- **Dynamic Evolution**: Networks rewire based on belief divergence
- **Echo Chamber Emergence**: Filter bubbles form as emergent property

### Misinformation Dynamics
- **Continuous Belief States**: Beliefs range from 0.0 to 1.0 per claim
- **Cascade Tracking**: Full genealogy of information spread
- **Structural Virality**: Distinguishes viral from broadcast patterns
- **R-effective Computation**: True epidemiological reproduction numbers

### Intervention Testing
- **Content Moderation**: Configurable removal/suppression effects
- **Prebunking/Inoculation**: Pre-exposure resistance building
- **Narrative Competition**: Competing claims and counter-messaging

### Technical Features
- **GPU Acceleration**: PyTorch-based vectorized computations (CUDA optional)
- **Deterministic Execution**: Full reproducibility with seed control
- **Comprehensive Metrics**: Adoption, polarization, entropy, cascade analysis
- **Interactive Dashboard**: Streamlit-based visualization

## Installation

### Using uv (Recommended)
```bash
cd town_misinfo_sim
uv venv
source .venv/bin/activate
uv pip install -e .
```

### Using pip
```bash
cd town_misinfo_sim
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Optional Dependencies
```bash
# For advanced community detection
pip install python-igraph

# For development
pip install -e ".[dev]"
```

## Quick Start

### Run a Baseline Simulation
```bash
python -m sim run \
  --config configs/world_baseline.yaml \
  --seed 42 \
  --steps 30 \
  --n 1000 \
  --out runs/baseline/
```

### Run an Alternate World
```bash
python -m sim run \
  --config configs/world_strong_moderation.yaml \
  --seed 42 \
  --steps 30 \
  --n 1000 \
  --out runs/moderation/
```

### Run a Parameter Sweep
```bash
python -m sim sweep \
  --configs configs/world_*.yaml \
  --seeds 1 2 3 4 5 \
  --out runs/sweep/
```

### Aggregate Results
```bash
python -m sim aggregate --runs runs/sweep/* --out runs/sweep/
```

### Launch Dashboard
```bash
python -m sim dashboard --run runs/baseline/
```

### Benchmark Performance
```bash
python -m sim bench \
  --config configs/world_baseline.yaml \
  --n 10000 \
  --steps 200 \
  --device cuda \
  --repeat 3 \
  --out runs/bench/
```

## World Configurations

Pre-configured scenarios in `configs/`:

| Configuration | Description |
|---------------|-------------|
| `world_baseline.yaml` | Standard balanced parameters |
| `world_high_trust_gov.yaml` | High institutional trust scenario |
| `world_low_trust_gov.yaml` | Low institutional trust scenario |
| `world_strong_moderation.yaml` | Aggressive content moderation |
| `world_collapsed_local_media.yaml` | Local media ecosystem collapse |
| `world_high_religion_hub.yaml` | High religious institution centrality |
| `world_outrage_algorithm.yaml` | Algorithmic amplification of outrage |

## Configuration Structure

```yaml
sim:
  steps: 30              # Simulation duration (days)
  n_agents: 1000         # Population size
  device: cuda           # cuda, mps, or cpu
  seed: 42               # Random seed

town:
  # Demographics and institution parameters

network:
  # Homophily and geography controls per layer

world:
  # Trust baselines, media reach, moderation

belief_update:
  # Coefficients for belief dynamics

sharing:
  # Share probability parameters

strains:
  # Synthetic claims with emotional profiles

metrics:
  # Community detection and metric settings
```

## Strain Properties

Each misinformation claim (strain) in the simulation is defined by a set of properties that control how it spreads, persists, and interacts with the population. Understanding these properties is crucial for configuring realistic misinformation scenarios.

### Core Properties

#### `name` (string)
- **Description**: Unique identifier for the strain
- **Example**: `"health_rumor"`, `"economic_panic"`
- **Usage**: Used for tracking and reporting in outputs

#### `topic` (string)
- **Description**: Categorical classification of the claim's subject matter
- **Valid values**: `health_rumor`, `economic_panic`, `moral_spiral`, `tech_conspiracy`, `outsider_threat`, `health_guidance`, `moral_spiritual`
- **Effect**: 
  - Claims with `moral` or `spiritual` topics receive +35% boost in church media exposure
  - Used for topic-based filtering and analysis
- **Example**: `topic: "health_rumor"`

#### `memeticity` (float, 0.0-1.0)
- **Description**: Base "stickiness" or inherent appeal of the claim
- **Range**: Typically 0.3-0.8
- **Effect**: Multiplies institutional exposure (media, social feeds, church)
  - Formula: `exposure = memeticity * (base_media + church_media + feed_boost)`
- **Higher values**: Claim spreads more easily through media channels
- **Lower values**: Claim requires more social proof to spread
- **Example**: `memeticity: 0.65` (highly contagious)

#### `emotional_profile` (dict)
- **Description**: Emotional resonance of the claim across three dimensions
- **Components**:
  - `fear` (0.0-1.0): How much the claim triggers fear/anxiety
  - `anger` (0.0-1.0): How much the claim triggers anger/outrage
  - `hope` (0.0-1.0): How much the claim offers hope/solutions
- **Effect**: 
  - Influences sharing probability through emotion matching with agent emotional states
  - High `anger` values amplify social media feed exposure via outrage amplification
  - Formula: `emotion_score = fear*weights[0] + anger*weights[1] + hope*weights[2]`
- **Example**: `emotional_profile: {fear: 0.5, anger: 0.3, hope: 0.2}`

### Verifiability Properties

#### `falsifiability` (float, 0.0-1.0)
- **Description**: How easily the claim can be fact-checked or debunked
- **Range**: Typically 0.4-1.0
- **Effect**: 
  - Higher values = easier to debunk = stronger debunking pressure
  - Used in debunk formula: `debunk = debunk_intensity * falsifiability * (1 - stealth)`
  - Truth claims typically have `falsifiability: 1.0` (fully verifiable)
- **Higher values**: Claim is more vulnerable to fact-checking
- **Lower values**: Claim is harder to disprove (e.g., vague conspiracy theories)
- **Example**: `falsifiability: 0.6` (moderately debunkable)

#### `stealth` (float, 0.0-1.0)
- **Description**: How well the claim evades detection and moderation
- **Range**: Typically 0.0-0.6
- **Effect**: 
  - Reduces debunking effectiveness: `debunk ∝ (1 - stealth)`
  - Reduces moderation penalties: `moderation_risk = violation_risk * (1 - stealth)`
  - Higher stealth = claim flies under the radar
- **Higher values**: Claim is harder to detect and moderate
- **Lower values**: Claim is more visible to fact-checkers and moderators
- **Example**: `stealth: 0.45` (moderately stealthy)

### Spread Dynamics

#### `virality` (float, default: 1.0)
- **Description**: Multiplicative factor for sharing probability
- **Range**: Typically 0.5-1.5
- **Effect**: Directly multiplies share probabilities
  - Formula: `final_share_prob = base_share_prob * virality`
- **Higher values**: Claim spreads faster through social networks
- **Lower values**: Claim spreads slower (useful for truth claims that spread more deliberately)
- **Example**: `virality: 1.2` (20% more likely to be shared)

#### `mutation_rate` (float, 0.0-1.0)
- **Description**: Probability per day that the claim mutates into a variant
- **Range**: Typically 0.0-0.08
- **Effect**: 
  - Each day, with probability `mutation_rate`, creates a mutated variant
  - Mutations slightly alter `stealth` (+/-0.05) and `falsifiability` (-0.03)
  - Mutated strains have `_m` suffix appended to name
- **Higher values**: Claim evolves rapidly, creating variants
- **Lower values**: Claim remains stable
- **Example**: `mutation_rate: 0.08` (8% chance per day of mutation)
- **Note**: Mutations create new strain objects with modified properties, but due to the fixed-size belief tensor, mutated strains share the same claim index as their parent. The mutation affects exposure and sharing calculations but mutations are not tracked as separate claims in metrics. This reflects real-world behavior where variants of misinformation compete for the same "belief slot" in agents' minds.

### Persistence Properties

#### `persistence` (float, 0.0-1.0, default: 0.0)
- **Description**: Resistance to belief decay over time
- **Range**: Typically 0.0-0.6
- **Effect**: 
  - Reduces belief decay rate: `decay = base_decay * (1 - persistence)`
  - `persistence: 0.5` means decay is halved
  - `persistence: 1.0` means no decay (beliefs persist indefinitely)
- **Higher values**: Beliefs in this claim fade more slowly
- **Lower values**: Beliefs decay at normal rate
- **Example**: `persistence: 0.4` (beliefs decay 40% slower)

### Risk Properties

#### `violation_risk` (float, 0.0-1.0)
- **Description**: Likelihood the claim violates platform policies
- **Range**: Typically 0.0-0.5
- **Effect**: 
  - Increases moderation penalties: `penalty = violation_risk * moderation_strictness`
  - Combined with stealth: `effective_risk = violation_risk * (1 - stealth)`
- **Higher values**: Claim is more likely to be flagged by moderators
- **Lower values**: Claim is less likely to trigger moderation
- **Example**: `violation_risk: 0.35` (moderate policy violation risk)

### Truth Properties

#### `is_true` (boolean, default: false)
- **Description**: Whether the claim is factual/truthful
- **Effect**: 
  - Truth claims receive positive exposure boost from institutional campaigns
  - Truth claims do not receive debunking pressure (they ARE the truth)
  - Agents with high belief in truth claims (≥`truth_protection_threshold`) are protected from conversion to misinformation
  - Truth claims can reduce belief in misinformation through truth signal amplification
- **Example**: `is_true: true`

### Example Strain Configuration

```yaml
strains:
  - name: "health_rumor"
    topic: "health_rumor"
    memeticity: 0.65          # Highly contagious
    emotional_profile: 
      fear: 0.6               # High fear appeal
      anger: 0.2
      hope: 0.2
    falsifiability: 0.7       # Can be debunked
    stealth: 0.4              # Somewhat evades detection
    mutation_rate: 0.05       # 5% daily mutation chance
    violation_risk: 0.3       # Moderate policy risk
    virality: 1.2             # 20% more shareable
    persistence: 0.3          # Beliefs decay 30% slower
    is_true: false            # Misinformation
```

### Property Interactions

- **Debunking**: `debunk_effectiveness ∝ falsifiability * (1 - stealth)`
- **Moderation**: `moderation_penalty ∝ violation_risk * (1 - stealth) * moderation_strictness`
- **Exposure**: `institutional_exposure = memeticity * (media_channels + social_feeds)`
- **Sharing**: `share_probability = base_prob * virality * (1 - moderation_penalty)`
- **Belief Decay**: `decay_rate = base_decay * (1 - persistence)`

### Design Guidelines

- **High-spread misinformation**: High `memeticity` (0.65-0.75), high `virality` (1.0-1.2), moderate `stealth` (0.5-0.6)
- **Stealth misinformation**: High `stealth` (0.5-0.6), low `falsifiability` (0.3-0.4), moderate `violation_risk` (0.3-0.4)
- **Viral misinformation**: High `virality` (1.0-1.2), high `anger` emotion (0.4-0.6), high `memeticity` (0.7-0.8)
- **Truth claims**: `is_true: true`, `falsifiability: 1.0`, `stealth: 0.0`, lower `virality` (0.15-0.2), higher `persistence` (0.7-0.8)

### Realistic Parameter Ranges (Based on Research)

Based on empirical studies (Vosoughi et al., 2018; Roozenbeek et al., 2020; Guess et al., 2019):

**Misinformation:**
- `memeticity`: 0.65-0.75 (highly shareable)
- `virality`: 1.0-1.2 (spreads 6x faster than truth)
- `emotional_profile`: High fear (0.5-0.7), moderate-high anger (0.4-0.6), low hope (0.1-0.2)
- `falsifiability`: 0.3-0.5 (harder to debunk)
- `stealth`: 0.5-0.6 (evades detection)
- `mutation_rate`: 0.05-0.08 (rapid evolution)
- `persistence`: 0.2-0.3 (beliefs fade without reinforcement)

**Truth:**
- `memeticity`: 0.2-0.3 (spreads more deliberately)
- `virality`: 0.15-0.2 (6x slower than misinformation)
- `emotional_profile`: Low fear (0.0-0.1), no anger (0.0), moderate hope (0.5-0.6)
- `falsifiability`: 1.0 (fully verifiable)
- `stealth`: 0.0 (transparent)
- `mutation_rate`: 0.0 (doesn't mutate)
- `persistence`: 0.7-0.8 (high persistence once adopted)

## Output Files

Each simulation run produces:

| File | Description |
|------|-------------|
| `daily_metrics.csv` | Daily adoption, belief, polarization metrics |
| `summary.json` | Peak statistics and intervention effects |
| `cascade_stats.json` | Information cascade analysis |
| `config_resolved.yaml` | Final resolved configuration |
| `run_metadata.json` | Versions, device, seed, git commit |
| `snapshots.parquet` | Belief state snapshots at intervals |

## Project Structure

```
town_misinfo_sim/
├── configs/                 # World configuration files
├── docs/                    # Additional documentation
│   └── METHODS.md          # Formal methods with equations
├── sim/                     # Main source code
│   ├── calibration/        # ABC calibration framework
│   ├── cascades/           # Cascade tracking and analysis
│   ├── cognition/          # Cognitive architecture modules
│   ├── dashboard/          # Streamlit visualization
│   ├── disease/            # Belief update and exposure
│   ├── dynamics/           # Network evolution
│   ├── io/                 # Input/output utilities
│   ├── metrics/            # Metric computation
│   ├── narratives/         # Competing narratives
│   ├── town/               # Town and network generation
│   └── world/              # World effects (moderation, media)
├── scripts/                 # Validation and analysis scripts
├── tests/                   # Unit tests
├── ARCHITECTURE.md         # Module structure documentation
├── BREAKTHROUGH_INNOVATIONS.md  # Technical innovations
└── pyproject.toml          # Project configuration
```

## Validation Results

The model has been validated with 1,200+ simulations:

| Metric | Value | Target |
|--------|-------|--------|
| Mean adoption (50 seeds) | 26.5% ± 3.0% | 20-40% |
| Seeds in target range | 98% | >90% |
| Strong moderation effect | -57% | Significant |
| Prebunking effect (30%) | -68% | Significant |

See `validation_results/NATURE_SUMMARY.md` for comprehensive validation.

## Quality Checks

```bash
# Run tests
python -m pytest

# Lint code
ruff check sim tests

# Type checking
mypy sim
```

## Performance Notes

- Belief updates run on GPU when available (`--device cuda`)
- For large simulations, keep `n_claims` small
- Disable cluster penetration for faster sweeps:
  ```yaml
  metrics:
    cluster_penetration_enabled: false
  ```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Base learning rate | 0.15 | Controls adoption speed |
| Social proof weight | 0.22 | Influence of peer beliefs |
| Skepticism dampening | 0.40 | Individual resistance |
| Decay rate | 0.008 | Belief fade over time |
| Adoption threshold | 0.70 | Belief level for "adoption" |

## Theoretical Foundations

The model integrates established theories:

- **Dual-Process Theory** (Kahneman, 2011)
- **Motivated Reasoning** (Kunda, 1990)
- **Inoculation Theory** (McGuire, 1961; van der Linden, 2017)
- **Social Proof** (Cialdini, 1984)
- **Attention Economics** (Simon, 1971)
- **Structural Virality** (Goel et al., 2016)

## Safety and Ethics

This simulator is designed for **research and defensive scenario analysis**. It does not include a misinformation optimizer. An optional research-only operator stub exists but is disabled by default.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use this simulator in your research, please cite:

```bibtex
@software{misinfo_sim,
  author = {Thiru, Mukund},
  title = {Town Misinformation Contagion Simulator},
  url = {https://github.com/contactmukundthiru-cyber/Misinformation-Agent-Simulation},
  year = {2024}
}
```

## References

1. Kahneman, D. (2011). *Thinking, fast and slow*. Farrar, Straus and Giroux.
2. Kunda, Z. (1990). The case for motivated reasoning. *Psychological Bulletin*.
3. van der Linden, S. (2017). Inoculating against misinformation. *Science*.
4. Vosoughi, S., Roy, D., & Aral, S. (2018). The spread of true and false news online. *Science*.
5. Goel, S., et al. (2016). The structural virality of online diffusion. *Management Science*.
# Misinformation-simulator-
# Misinformation-simulator-
# Misinformation-simulator-
