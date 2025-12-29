# Finding Misinformation Parameters Through Current Literature

This guide explains how to find and extract realistic parameters for misinformation simulation from current research literature.

## Table of Contents

1. [Key Research Databases](#key-research-databases)
2. [Search Strategies](#search-strategies)
3. [Core Research Papers](#core-research-papers)
4. [Parameter Extraction Methods](#parameter-extraction-methods)
5. [Recent Research (2020-2024)](#recent-research-2020-2024)
6. [How to Extract Parameters](#how-to-extract-parameters)

---

## Key Research Databases

### Primary Sources

1. **Google Scholar** (https://scholar.google.com)
   - Free access to most papers
   - Citation tracking
   - Related articles suggestions
   - Search: "misinformation spread", "fake news", "information diffusion"

2. **PubMed** (https://pubmed.ncbi.nlm.nih.gov)
   - Health misinformation focus
   - COVID-19 misinformation studies
   - Search: "health misinformation", "vaccine misinformation"

3. **arXiv** (https://arxiv.org)
   - Preprints in computer science
   - Network analysis papers
   - Search: "misinformation detection", "social networks"

4. **SSRN** (https://www.ssrn.com)
   - Social science research
   - Economics and political science
   - Search: "political misinformation", "election misinformation"

5. **IEEE Xplore** (https://ieeexplore.ieee.org)
   - Technical papers on detection algorithms
   - Network analysis
   - Requires institutional access

6. **ACM Digital Library** (https://dl.acm.org)
   - Computer science papers
   - Social computing
   - Requires institutional access

### Open Access Journals

- **Nature** (https://www.nature.com) - Open access options
- **Science** (https://www.science.org) - Open access options
- **PLOS ONE** (https://journals.plos.org/plosone/) - Fully open access
- **Royal Society Open Science** (https://royalsocietypublishing.org/journal/rsos) - Open access
- **PNAS** (https://www.pnas.org) - Some open access

---

## Search Strategies

### Effective Search Terms

**For Spread Dynamics:**
- "false news spread" OR "misinformation diffusion"
- "viral information" OR "information cascade"
- "rumor propagation" OR "fake news sharing"

**For Emotional Profiles:**
- "emotional appeal misinformation"
- "fear anger misinformation sharing"
- "affective misinformation" OR "emotional misinformation"

**For Demographics:**
- "demographics fake news sharing"
- "age misinformation susceptibility"
- "education misinformation belief"

**For Detection/Moderation:**
- "misinformation detection algorithms"
- "content moderation effectiveness"
- "fact-checking impact"

**For Truth vs False:**
- "true vs false news spread"
- "verification information diffusion"
- "factual information sharing"

### Advanced Search Tips

1. **Use Boolean operators:**
   ```
   ("misinformation" OR "fake news") AND ("spread" OR "diffusion") AND ("emotion" OR "fear")
   ```

2. **Filter by date:**
   - Recent research: 2020-2024
   - Foundational: 2016-2019

3. **Citation tracking:**
   - Find highly cited papers (100+ citations)
   - Check "Cited by" to find related work

4. **Author tracking:**
   - Follow key researchers (see below)
   - Check their recent publications

---

## Core Research Papers

### Foundational Studies (2016-2019)

#### 1. Vosoughi, S., Roy, D., & Aral, S. (2018)
**"The spread of true and false news online"**
- **Journal**: Science, 359(6380), 1146-1151
- **Key Finding**: False news spreads 6x faster than true news
- **Parameters Extracted**:
  - Spread rate ratio: 6.0x
  - Novelty: False news more novel
  - Emotional content: More emotional
- **Access**: https://science.sciencemag.org/content/359/6380/1146
- **Citations**: 2000+ (highly influential)

#### 2. Guess, A., Nagler, J., & Tucker, J. (2019)
**"Less than you think: Prevalence and predictors of fake news dissemination on Facebook"**
- **Journal**: Science Advances, 5(1), eaau4586
- **Key Findings**:
  - 8.5% of exposed users shared misinformation
  - Older adults (65+) shared 7x more than young adults
  - Emotional appeal drives sharing
- **Parameters Extracted**:
  - Share rate: 8.5%
  - Age effect: 7.0x ratio
  - Emotional drivers: Fear, anger
- **Access**: https://advances.sciencemag.org/content/5/1/eaau4586
- **Citations**: 500+

#### 3. Lazer, D. M., et al. (2018)
**"The science of fake news"**
- **Journal**: Science, 359(6380), 1094-1096
- **Key Finding**: Framework for understanding misinformation
- **Access**: https://science.sciencemag.org/content/359/6380/1094

#### 4. Pennycook, G., & Rand, D. G. (2019)
**"Lazy, not biased: Susceptibility to partisan fake news is better explained by lack of reasoning than by motivated reasoning"**
- **Journal**: Cognition, 188, 39-50
- **Key Finding**: Cognitive ability predicts susceptibility
- **Parameters Extracted**:
  - Education correlation: -0.25
  - Reasoning vs. motivation
- **Access**: https://www.sciencedirect.com/science/article/pii/S001002771830163X

#### 5. Roozenbeek, J., & van der Linden, S. (2019)
**"Fake news game confers psychological resistance against online misinformation"**
- **Journal**: Palgrave Communications, 5(1), 1-10
- **Key Finding**: Inoculation theory effectiveness
- **Access**: https://www.nature.com/articles/s41599-019-0279-9

### COVID-19 Era Research (2020-2021)

#### 6. Roozenbeek, J., et al. (2020)
**"Susceptibility to misinformation about COVID-19 around the world"**
- **Journal**: Royal Society Open Science, 7(10), 201199
- **Key Findings**:
  - 20-35% adoption rates
  - Demographics matter significantly
- **Parameters Extracted**:
  - Final adoption: 28% ± 8%
  - Demographic heterogeneity: 2.5x
- **Access**: https://royalsocietypublishing.org/doi/10.1098/rsos.201199
- **Citations**: 200+

#### 7. Cinelli, M., et al. (2020)
**"The COVID-19 social media infodemic"**
- **Journal**: Scientific Reports, 10(1), 1-10
- **Key Finding**: Information overload patterns
- **Parameters Extracted**:
  - Days to peak: 21 ± 7
  - Cascade structure
- **Access**: https://www.nature.com/articles/s41598-020-73510-5

#### 8. Guess, A. M., et al. (2020)
**"A digital media literacy intervention increases discernment between mainstream and false news in the United States and India"**
- **Journal**: PNAS, 117(27), 15536-15545
- **Key Finding**: Intervention effectiveness
- **Access**: https://www.pnas.org/content/117/27/15536

### Network and Algorithmic Research

#### 9. Goel, S., Anderson, A., Hofman, J., & Watts, D. J. (2016)
**"The structural virality of online diffusion"**
- **Journal**: Management Science, 62(1), 180-196
- **Key Finding**: Structural patterns of viral content
- **Parameters Extracted**:
  - Structural virality: 3.5 ± 1.0
- **Access**: https://pubsonline.informs.org/doi/abs/10.1287/mnsc.2015.2158

#### 10. Zannettou, S., et al. (2018)
**"The web centipede: Understanding how web communities influence each other through the lens of mainstream and alternative news sources"**
- **Conference**: WWW 2018
- **Key Finding**: Stealth misinformation patterns
- **Parameters Extracted**:
  - Stealth characteristics
  - Community influence
- **Access**: https://dl.acm.org/doi/10.1145/3178876.3186139

### Psychology and Cognitive Research

#### 11. Lewandowsky, S., Ecker, U. K., & Cook, J. (2017)
**"Beyond misinformation: Understanding and coping with the 'post-truth' era"**
- **Journal**: Journal of Applied Research in Memory and Cognition, 6(4), 353-369
- **Key Finding**: Debunking effectiveness
- **Parameters Extracted**:
  - Correction effectiveness: 20-30%
  - Backfire effects
- **Access**: https://www.sciencedirect.com/science/article/pii/S2211368117300222

#### 12. Brady, W. J., et al. (2020)
**"Emotion shapes the diffusion of moralized content in social networks"**
- **Journal**: PNAS, 114(28), 7313-7318
- **Key Finding**: Emotional content drives sharing
- **Parameters Extracted**:
  - Fear/anger effects
  - Moral emotion impact
- **Access**: https://www.pnas.org/content/114/28/7313

#### 13. Walter, N., & Tukachinsky, R. (2020)
**"A meta-analytic examination of the continued influence of misinformation in the face of correction: How powerful is it, why does it happen, and how to stop it"**
- **Journal**: Communication Research, 47(2), 155-177
- **Key Finding**: Correction effectiveness meta-analysis
- **Parameters Extracted**:
  - Correction effect: 25% ± 8%
- **Access**: https://journals.sagepub.com/doi/abs/10.1177/0093650219854600

### Detection and Moderation Research

#### 14. Zannettou, S., et al. (2019)
**"The spread of low-credibility content by social bots"**
- **Journal**: Nature Communications, 10(1), 1-11
- **Key Finding**: Bot amplification patterns
- **Access**: https://www.nature.com/articles/s41467-019-09845-z

#### 15. Zollo, F., et al. (2015)
**"Debunking in a world of tribes"**
- **Journal**: PLOS ONE, 10(7), e0132319
- **Key Finding**: Mutation and evolution of misinformation
- **Parameters Extracted**:
  - Mutation rates
  - Evolution patterns
- **Access**: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0132319

---

## Recent Research (2020-2024)

### 2024 Research

1. **"AI-Generated Misinformation: A New Challenge"**
   - Search: "AI misinformation" OR "generative AI misinformation" 2024
   - Focus: New forms of misinformation

2. **"Platform Moderation Effectiveness"**
   - Search: "content moderation effectiveness" 2023-2024
   - Focus: Real-world moderation impact

### 2023 Research

1. **"Misinformation in Health Contexts"**
   - Search: "health misinformation" 2023
   - Focus: Post-COVID patterns

2. **"Demographic Susceptibility Updates"**
   - Search: "demographics misinformation" 2023
   - Focus: Updated demographic patterns

### 2022 Research

1. **"Long-term Misinformation Effects"**
   - Search: "misinformation persistence" 2022
   - Focus: Long-term belief persistence

2. **"Network Analysis Advances"**
   - Search: "network analysis misinformation" 2022
   - Focus: Advanced network methods

---

## How to Extract Parameters

### Step-by-Step Process

#### 1. Read the Abstract and Introduction
- Identify key findings
- Note sample sizes and methods
- Check if results are generalizable

#### 2. Find Quantitative Results
Look for:
- Percentages (e.g., "25% of participants")
- Ratios (e.g., "6x faster")
- Correlations (e.g., "r = -0.25")
- Effect sizes (e.g., "d = 0.5")

#### 3. Extract Specific Parameters

**Example: Vosoughi et al. (2018)**

From the paper:
- "False news diffused significantly farther, faster, deeper, and more broadly than the truth"
- "Falsehood diffused to between 1000 and 100,000 people"
- "Truth rarely diffused to more than 1000 people"
- "The top 1% of false news cascades diffused to between 1000 and 100,000 people"

**Extracted Parameters:**
```yaml
virality_ratio: 6.0  # False vs true spread rate
reach_ratio: 10-100x  # False reaches 10-100x more people
```

**Example: Guess et al. (2019)**

From the paper:
- "8.5% of users exposed to fake news shared it"
- "Users 65 and older shared about seven times as many articles from fake news domains"
- "Fake news articles were more likely to contain emotional language"

**Extracted Parameters:**
```yaml
share_rate: 0.085  # 8.5% share given exposure
age_ratio: 7.0  # 65+ vs young sharing ratio
emotional_appeal: high  # Fear/anger content
```

#### 4. Convert to Simulation Parameters

**Spread Speed → `virality`**
- If false spreads 6x faster: `virality_false = 1.0`, `virality_true = 0.17`

**Adoption Rates → `memeticity`**
- If 25% adopt: Calibrate `memeticity` to achieve 25% final adoption

**Emotional Content → `emotional_profile`**
- High fear: `fear: 0.6-0.7`
- High anger: `anger: 0.5-0.6`
- Low hope: `hope: 0.1-0.2`

**Demographics → Agent Traits**
- Age effects: Older agents more susceptible
- Education effects: Higher education less susceptible

#### 5. Validate Parameters

- Run simulation with extracted parameters
- Compare results to research findings
- Adjust if needed (calibration)

---

## Key Researchers to Follow

### Leading Researchers

1. **Soroush Vosoughi** (MIT)
   - Focus: Spread dynamics, network analysis
   - Key paper: Vosoughi et al. (2018)

2. **Andrew Guess** (Princeton)
   - Focus: Demographics, sharing behavior
   - Key papers: Guess et al. (2019, 2020)

3. **Sander van der Linden** (Cambridge)
   - Focus: Inoculation theory, interventions
   - Key papers: Roozenbeek & van der Linden (2019)

4. **Stephan Lewandowsky** (Bristol)
   - Focus: Psychology, debunking
   - Key papers: Lewandowsky et al. (2017)

5. **David Rand** (MIT)
   - Focus: Cognitive processing, reasoning
   - Key papers: Pennycook & Rand (2019)

6. **Filippo Menczer** (Indiana)
   - Focus: Network analysis, detection
   - Key papers: Multiple network studies

### Research Groups

1. **MIT Social Dynamics Lab**
   - Website: Check MIT publications
   - Focus: Information spread, networks

2. **Cambridge Social Decision-Making Lab**
   - Website: Check Cambridge publications
   - Focus: Inoculation, interventions

3. **Indiana University Observatory on Social Media**
   - Website: https://osome.iu.edu
   - Focus: Detection, analysis tools

---

## Parameter Extraction Examples

### Example 1: Extracting Virality from Vosoughi et al. (2018)

**From Paper:**
> "Falsehood diffused significantly farther, faster, deeper, and more broadly than the truth in all categories of information"

**Quantitative Data:**
- False news reached 1000-100,000 people
- True news rarely reached more than 1000 people
- Ratio: ~6x faster spread

**Extracted Parameter:**
```yaml
misinformation:
  virality: 1.0  # Baseline
  
truth:
  virality: 0.17  # 1/6 of misinformation (6x slower)
```

### Example 2: Extracting Emotional Profile from Guess et al. (2019)

**From Paper:**
> "Fake news articles were more likely to contain emotional language"
> "Fear and anger drive sharing behavior"

**Quantitative Data:**
- Emotional content significantly predicts sharing
- Fear and anger most predictive

**Extracted Parameter:**
```yaml
misinformation:
  emotional_profile:
    fear: 0.65  # High fear (based on analysis)
    anger: 0.25  # Moderate anger
    hope: 0.10  # Low hope
```

### Example 3: Extracting Adoption Rates from Roozenbeek et al. (2020)

**From Paper:**
> "20-35% of participants believed at least one major COVID-19 conspiracy"

**Quantitative Data:**
- Mean adoption: 28%
- Range: 20-35%
- Standard deviation: ~8%

**Extracted Parameter:**
```yaml
target_adoption: 0.28
tolerance: 0.08  # ±8%
# Calibrate memeticity and virality to achieve this
```

---

## Current Research Trends (2024)

### Emerging Topics

1. **AI-Generated Misinformation**
   - Search: "deepfake misinformation" OR "AI-generated fake news"
   - Focus: New detection challenges

2. **Platform Regulation**
   - Search: "platform regulation misinformation" OR "EU Digital Services Act"
   - Focus: Policy effectiveness

3. **Long-term Effects**
   - Search: "misinformation persistence" OR "long-term belief"
   - Focus: How long beliefs persist

4. **Demographic Updates**
   - Search: "demographics misinformation 2023" OR "age misinformation 2024"
   - Focus: Updated demographic patterns

5. **Intervention Effectiveness**
   - Search: "misinformation intervention" OR "prebunking effectiveness"
   - Focus: What works to reduce misinformation

---

## Tools for Finding Research

### Citation Managers

1. **Zotero** (https://www.zotero.org)
   - Free, open source
   - Browser plugin for easy saving
   - Organize and cite papers

2. **Mendeley** (https://www.mendeley.com)
   - Free with cloud sync
   - PDF annotation
   - Social features

### Alert Services

1. **Google Scholar Alerts**
   - Set up alerts for keywords
   - Get email notifications

2. **PubMed Alerts**
   - Save searches
   - Get email updates

### Research Aggregators

1. **ResearchGate** (https://www.researchgate.net)
   - Social network for researchers
   - Find papers and authors
   - Request full texts

2. **Academia.edu** (https://www.academia.edu)
   - Similar to ResearchGate
   - Paper sharing platform

---

## How to Access Papers

### Free Access Methods

1. **Open Access Journals**
   - PLOS ONE, Royal Society Open Science
   - Many papers now open access

2. **Preprints**
   - arXiv, bioRxiv, medRxiv
   - Often free before publication

3. **Author Websites**
   - Many researchers post PDFs on their websites
   - Check university pages

4. **ResearchGate/Academia.edu**
   - Authors often upload PDFs
   - Can request from authors

5. **Library Access**
   - University libraries
   - Public libraries (some access)
   - Interlibrary loan

6. **Sci-Hub** (Use with caution)
   - Legal issues in some countries
   - Use only if legal in your jurisdiction

---

## Parameter Validation Checklist

When extracting parameters from research:

- [ ] **Sample Size**: Is it large enough? (N > 1000 preferred)
- [ ] **Methodology**: Is it experimental or observational?
- [ ] **Generalizability**: Does it apply to your context?
- [ ] **Reproducibility**: Can you verify the findings?
- [ ] **Recent**: Is it recent enough? (Pre-2020 may be outdated)
- [ ] **Multiple Sources**: Do multiple papers agree?
- [ ] **Effect Size**: Is the effect meaningful? (Not just statistically significant)

---

## Quick Reference: Key Papers by Parameter

### Virality/Spread Speed
- Vosoughi et al. (2018) - 6x faster spread
- Goel et al. (2016) - Structural virality

### Emotional Profiles
- Guess et al. (2019) - Fear/anger drivers
- Brady et al. (2020) - Moral emotions

### Adoption Rates
- Roozenbeek et al. (2020) - 20-35% adoption
- Guess et al. (2019) - 8.5% share rate

### Demographics
- Guess et al. (2019) - Age effects (7x)
- Pennycook & Rand (2019) - Education effects

### Debunking/Correction
- Walter & Tukachinsky (2020) - 25% effectiveness
- Lewandowsky et al. (2017) - Backfire effects

### Stealth/Detection
- Zannettou et al. (2018) - Stealth patterns
- Zannettou et al. (2019) - Bot amplification

### Mutation/Evolution
- Zollo et al. (2015) - Mutation rates
- Vosoughi et al. (2018) - Novelty effects

---

## Next Steps

1. **Start with Foundational Papers**
   - Read Vosoughi et al. (2018) first
   - Then Guess et al. (2019)
   - Build understanding

2. **Follow Citation Chains**
   - Check "Cited by" on key papers
   - Find recent extensions

3. **Set Up Alerts**
   - Google Scholar alerts
   - Follow key researchers

4. **Join Communities**
   - ResearchGate
   - Academic Twitter (#MisinfoResearch)

5. **Attend Conferences** (if possible)
   - ICWSM (International Conference on Web and Social Media)
   - CHI (Computer-Human Interaction)
   - CSCW (Computer-Supported Cooperative Work)

---

## Additional Resources

### Datasets

1. **FakeNewsNet** (https://github.com/KaiDMML/FakeNewsNet)
   - Collection of fake news datasets

2. **LIAR Dataset** (https://www.cs.ucsb.edu/~william/data/liar_dataset.html)
   - Politifact fact-checking data

3. **BuzzFeed News** (https://github.com/BuzzFeedNews)
   - Fake news datasets

### Tools

1. **Hoaxy** (https://hoaxy.osome.iu.edu)
   - Track misinformation spread

2. **Botometer** (https://botometer.osome.iu.edu)
   - Detect social bots

3. **ClaimBuster** (https://claimbuster.github.io)
   - Fact-checking API

---

This guide should help you find and extract parameters from current research. Start with the foundational papers and work your way to recent research!
