# Agent Architecture

The Town Misinformation Contagion Simulator uses a cognitively-grounded agent-based model. Agents process information through a Dual-Process architecture and transition between states defined by the SEDPNR framework.

## 1. Dual-Process Cognition (System 1 & System 2)

Based on Kahneman's theory, agents evaluate news through two distinct channels:

- **System 1 (Fast/Intuitive)**:
  - Driven by emotional resonance, familiarity, and narrative fit.
  - Dominant when cognitive load is high or the agent is in a "fluent" state.
- **System 2 (Slow/Analytical)**:
  - Evaluates evidence quality, source credibility, and logical consistency.
  - Triggered by doubt, high stakes (identity threat), or novelty.

## 2. SEDPNR State Model

Agents transition through several states for each piece of misinformation:

- **Susceptible (S)**: Has not yet encountered the claim.
- **Exposed (E)**: Has seen the claim but not yet formed a strong belief.
- **Doubtful (D)**: Triggered when an agent detects conflict between System 1 intuition and System 2 analysis. Doubtful agents engage in more analytical thinking.
- **Infected (P/N)**: 
  - **Positively Infected (P)**: Believes and spreads the rumor in a positive tone.
  - **Negatively Infected (N)**: Rejects the rumor and may spread warnings or debunks (Negative sharing).
- **Restrained (R)**: Agents who have shared the information multiple times and hit "engagement fatigue". Restrained agents stop spreading the rumor.

## 3. Sharing Channels

Sharing is no longer a binary action. Agents can share via two distinct channels:
1. **Positive Channel**: Spreading the rumor as true.
2. **Negative Channel**: Sharing to debunk or warn others.

## 4. Cultural & Demographic Nuance

- **Identity-Protective Cognition**: Agents are more susceptible to claims that align with their cultural group.
- **Biased Media Diets**: Media consumption is biased by age (Youth: TikTok/Instagram, Seniors: TV/News) and ethnicity (Community-specific penetration, e.g., WhatsApp).
- **Age Multipliers**: Older adults (65+) share misinformation significantly more frequently (up to 7x) than younger adults.
- **Skepticism & Numeracy**: Traits that modulate the weight of System 2 thinking.

## 5. Spread Logic

- **Social Cascades**: Information spread is driven by social ties. Initially seeded agents are marked as "Exposed" to initiate the cascade.
- **Engagement Fatigue**: To prevent infinite loops, agents hit a "Restrained" state after repeated sharing, realistically modeling information saturation.
