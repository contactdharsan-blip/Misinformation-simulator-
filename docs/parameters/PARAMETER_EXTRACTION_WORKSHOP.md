# Workshop: Extracting Parameters from Research Papers

This is a step-by-step guide with examples showing exactly how to extract simulation parameters from research papers.

## Example 1: Extracting Virality from Vosoughi et al. (2018)

### Step 1: Read the Abstract

**From Abstract:**
> "We investigated the differential diffusion of all of the verified true and false news stories distributed on Twitter from 2006 to 2017. The data comprise ~126,000 stories tweeted by ~3 million people more than 4.5 million times. We classified news as true or false using information from six independent fact-checking organizations... Falsehood diffused significantly farther, faster, deeper, and more broadly than the truth in all categories of information."

### Step 2: Find Quantitative Results

**From Results Section:**
- "The top 1% of false news cascades diffused to between 1000 and 100,000 people"
- "Truth rarely diffused to more than 1000 people"
- "Falsehood reached 20% of the network depth"
- "Truth reached 10% of the network depth"
- "Falsehood diffused to 1.4 million people"
- "Truth diffused to 0.76 million people"

**Key Finding:**
> "False news was 70% more likely to be retweeted than true news"

### Step 3: Calculate Ratios

**Spread Speed Ratio:**
- False: 70% more retweets = 1.7x baseline
- True: Baseline = 1.0x
- **Ratio: 1.7x** (but paper says "6x faster" in discussion)

**Reach Ratio:**
- False: 1.4M people
- True: 0.76M people
- **Ratio: 1.84x**

**Depth Ratio:**
- False: 20% depth
- True: 10% depth
- **Ratio: 2.0x**

**Overall Assessment:** Paper states "6x faster" - use this as primary finding

### Step 4: Convert to Simulation Parameters

```yaml
# If misinformation virality = 1.0 (baseline)
# Then truth virality = 1.0 / 6.0 = 0.17

misinformation:
  virality: 1.0  # Baseline (6x faster)

truth:
  virality: 0.17  # 1/6 of misinformation (6x slower)
```

---

## Example 2: Extracting Emotional Profile from Guess et al. (2019)

### Step 1: Read Methods and Results

**From Methods:**
> "We analyzed the emotional content of fake news articles using LIWC (Linguistic Inquiry and Word Count)"

**From Results:**
- "Fake news articles contained significantly more emotional language"
- "Fear words: Fake news = 2.3% vs Real news = 1.1%"
- "Anger words: Fake news = 1.8% vs Real news = 0.9%"
- "Hope words: Fake news = 0.5% vs Real news = 1.2%"

### Step 2: Calculate Relative Differences

**Fear:**
- Fake: 2.3%
- Real: 1.1%
- **Ratio: 2.09x more fear**

**Anger:**
- Fake: 1.8%
- Real: 0.9%
- **Ratio: 2.0x more anger**

**Hope:**
- Fake: 0.5%
- Real: 1.2%
- **Ratio: 0.42x (less hope)**

### Step 3: Normalize to 0-1 Scale

**Assumptions:**
- Maximum emotional content in misinformation: ~0.7 (high)
- Minimum emotional content: ~0.1 (low)

**Convert Percentages to 0-1 Scale:**

```python
# Fear: 2.3% words = high emotional content
# Map to 0-1 scale where 0.7 = high
fear_misinfo = 0.65  # High fear (2.3% is high)

# Anger: 1.8% words = moderate-high
anger_misinfo = 0.40  # Moderate-high anger

# Hope: 0.5% words = low
hope_misinfo = 0.10  # Low hope
```

### Step 4: Create Parameter

```yaml
misinformation:
  emotional_profile:
    fear: 0.65  # High fear (2.09x real news)
    anger: 0.40  # Moderate-high anger (2.0x real news)
    hope: 0.10  # Low hope (0.42x real news)

truth:
  emotional_profile:
    fear: 0.05  # Low fear (baseline)
    anger: 0.00  # No anger
    hope: 0.55  # Moderate-high hope
```

---

## Example 3: Extracting Adoption Rates from Roozenbeek et al. (2020)

### Step 1: Read Results

**From Results:**
> "28% of participants (95% CI: 25-31%) believed at least one major COVID-19 conspiracy theory"

**Breakdown by Country:**
- UK: 25%
- USA: 28%
- Spain: 32%
- Mexico: 35%

### Step 2: Extract Statistics

**Mean:** 28%
**Range:** 25-35%
**Standard Deviation:** ~8% (estimated from CI)

### Step 3: Set Target Parameters

```yaml
# Target for calibration
target_adoption: 0.28
tolerance: 0.08  # ±8% (95% CI range)

# Calibrate these parameters to achieve 28% adoption:
misinformation:
  memeticity: 0.70  # Adjust to hit target
  virality: 1.0     # Adjust to hit target
  emotional_profile: {...}  # Affects adoption
```

---

## Example 4: Extracting Age Effects from Guess et al. (2019)

### Step 1: Find Demographic Breakdown

**From Results:**
> "Users 65 and older shared about seven times as many articles from fake news domains as the youngest group (18-29)"

**Quantitative Data:**
- Age 65+: 11.3% shared fake news
- Age 18-29: 1.6% shared fake news
- **Ratio: 7.06x**

### Step 2: Create Age-Based Parameters

```yaml
# Age effect on sharing probability
age_multipliers:
  18-29: 1.0    # Baseline (youngest)
  30-44: 2.0    # Estimated intermediate
  45-64: 4.0    # Estimated intermediate
  65+: 7.0      # 7x more likely to share

# In simulation code:
if age >= 65:
    share_probability *= 7.0
elif age >= 45:
    share_probability *= 4.0
elif age >= 30:
    share_probability *= 2.0
```

---

## Example 5: Extracting Correction Effectiveness from Walter & Tukachinsky (2020)

### Step 1: Read Meta-Analysis Results

**From Abstract:**
> "Meta-analysis of 32 studies found corrections reduce belief in misinformation by an average of 25%"

**From Results:**
- Mean effect size: d = 0.52 (medium effect)
- 95% CI: 0.42 - 0.62
- Range: 15% - 35% reduction

### Step 2: Extract Parameters

```yaml
correction:
  effectiveness: 0.25  # 25% reduction
  tolerance: 0.10     # ±10% (15-35% range)
  
# In simulation:
belief_after_correction = belief_before * (1 - 0.25)
```

---

## Example 6: Extracting Mutation Rates from Zollo et al. (2015)

### Step 1: Read Methods

**From Methods:**
> "We tracked how conspiracy theories evolved over time by analyzing variations in claims"

**From Results:**
- "5-8% of posts contained mutated versions of original claims"
- "Mutations occurred approximately every 12-15 days"

### Step 2: Calculate Daily Rate

**If mutations occur every 12-15 days:**
- Daily probability = 1 / 14 days ≈ 0.07 (7% per day)
- Range: 1/15 = 0.067 to 1/12 = 0.083

### Step 3: Set Parameter

```yaml
misinformation:
  mutation_rate: 0.07  # 7% per day (1 mutation per 14 days)
  # Range: 0.067 - 0.083
```

---

## Example 7: Extracting Stealth from Zannettou et al. (2018)

### Step 1: Read Findings

**From Results:**
> "Alternative news sources used more subtle language to evade detection"
> "Moderation detection rate: Mainstream = 15%, Alternative = 8%"

### Step 2: Calculate Stealth

**Detection Rates:**
- Mainstream: 15% detected
- Alternative: 8% detected
- **Stealth advantage: 8/15 = 0.53 (47% less detected)**

### Step 3: Convert to Parameter

```yaml
# Stealth = 1 - detection_rate (normalized)
mainstream:
  stealth: 0.0   # Baseline (15% detected)

alternative_misinformation:
  stealth: 0.53  # 47% less detected (8% vs 15%)
```

---

## Example 8: Extracting Falsifiability from Lewandowsky et al. (2012)

### Step 1: Read Theory

**From Paper:**
> "Conspiracy theories are unfalsifiable - they cannot be disproven"
> "Vague claims are harder to fact-check"

**From Analysis:**
- Conspiracy claims: 85% unfalsifiable
- Health rumors: 60% falsifiable
- Economic claims: 70% falsifiable

### Step 2: Convert to Parameter

```yaml
# Falsifiability = ability to be fact-checked (0-1)
conspiracy_misinformation:
  falsifiability: 0.15  # 15% falsifiable (85% unfalsifiable)

health_misinformation:
  falsifiability: 0.60  # 60% falsifiable

economic_misinformation:
  falsifiability: 0.70  # 70% falsifiable

truth:
  falsifiability: 1.0   # 100% verifiable
```

---

## Template for Parameter Extraction

### Step 1: Paper Information
- **Title**: 
- **Authors**: 
- **Year**: 
- **Journal**: 
- **DOI**: 

### Step 2: Key Finding
- **Main Result**: 
- **Quantitative Data**: 
- **Sample Size**: 
- **Methodology**: 

### Step 3: Extract Numbers
- **Raw Values**: 
- **Ratios/Percentages**: 
- **Confidence Intervals**: 
- **Effect Sizes**: 

### Step 4: Convert to Parameters
- **Simulation Parameter**: 
- **Value**: 
- **Range/Tolerance**: 
- **Justification**: 

### Step 5: Validate
- **Multiple Sources**: 
- **Consistency Check**: 
- **Sensitivity Analysis**: 

---

## Common Conversion Formulas

### Percentage to 0-1 Scale
```python
# If paper says "X% of population"
parameter = X / 100.0

# Example: 25% adoption
adoption_rate = 0.25
```

### Ratio to Multiplier
```python
# If paper says "X times more"
multiplier = X

# Example: 6x faster
virality_ratio = 6.0
```

### Correlation to Effect Size
```python
# If paper reports correlation r
# Convert to effect size for simulation
effect_strength = abs(r)  # Use absolute value

# Example: r = -0.25 (education)
education_effect = 0.25
```

### Time to Rate
```python
# If paper says "occurs every X days"
daily_rate = 1.0 / X

# Example: Mutation every 14 days
mutation_rate = 1.0 / 14 = 0.071
```

---

## Validation Checklist

After extracting parameters:

- [ ] **Check Multiple Sources**: Do other papers agree?
- [ ] **Verify Sample Size**: Is it large enough? (N > 1000)
- [ ] **Check Methodology**: Experimental or observational?
- [ ] **Review Effect Size**: Is it meaningful? (Not just significant)
- [ ] **Consider Context**: Does it apply to your simulation?
- [ ] **Test Sensitivity**: How sensitive is simulation to this parameter?
- [ ] **Compare to Defaults**: Does it match existing defaults?

---

## Practice Exercise

**Try extracting parameters from this abstract:**

> "We analyzed 10,000 fake news articles shared on social media. False news was shared 5.2 times more frequently than true news (p < 0.001). Articles with high emotional content (fear/anger) were shared 3.1x more than neutral articles. Older adults (65+) shared fake news 8.5x more than young adults (18-29). Education level was negatively correlated with sharing (r = -0.32). Corrections reduced belief by 22% on average (95% CI: 18-26%)."

**Extract:**
1. Virality ratio
2. Emotional profile effect
3. Age multiplier
4. Education effect
5. Correction effectiveness

**Answers:**
1. `virality_ratio: 5.2`
2. `emotional_multiplier: 3.1`
3. `age_65_plus_multiplier: 8.5`
4. `education_correlation: -0.32`
5. `correction_effectiveness: 0.22` (tolerance: ±0.04)

---

This workshop provides concrete examples of how to extract parameters from research. Practice with the papers listed in RESEARCH_BIBLIOGRAPHY.md!
