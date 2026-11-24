# Research protocol draft

## Working title

Financial News Sentiment and Short-Term Market Reactions: Evidence from Indian Listed Banks

## Objective

Measure whether bank-specific news sentiment is associated with next-session market-adjusted returns and unusual trading volume. Treat this as an association study. The project does not claim news causes returns or that the sentiment measure can generate profitable trades.

## Questions and hypotheses

1. Is daily aggregate sentiment associated with next-trading-session abnormal returns?
2. Do days with more negative sentiment have higher-than-usual trading volume?
3. Do the associations differ between public-sector and private-sector banks?
4. Does FinBERT sentiment agree with human annotations more often than a simple lexicon baseline?

Pre-register the sample, event window, inclusion criteria, and primary outcome before examining final associations. A reasonable primary outcome is the next-session market-adjusted return; treat same-day results as secondary because daily data cannot precisely isolate the time of an intraday article.

## Sample and data dictionary

Choose a balanced set of actively traded public- and private-sector banks and a multi-year window for which news and price coverage overlap. Record ticker, bank group, source, source URL, publication time, headline, optional abstract/snippet, and collection date. Prefer links plus short permitted excerpts instead of retaining full copyrighted articles.

Market data should contain exchange trading date, ticker, adjusted close if licensed/available, volume, and a consistent benchmark close. Use RBI banking statistics for context and bank-group covariates where appropriate. Record missing-data and exclusion decisions.

## Text model evaluation

Create a stratified sample across banks, sources, and years. Two annotators independently label positive, neutral, or negative sentiment toward the bank, resolve disagreements, and report agreement. Compare the frozen FinBERT model with the lexicon baseline using a confusion matrix, macro-F1, and class-level precision/recall. Inspect errors involving negation, regulatory actions, credit quality, and neutral factual reporting. Do not fine-tune on the evaluation sample.

## Outcomes and statistical approach

- Daily sentiment: mean document polarity (positive probability minus negative probability), with article count reported.
- Abnormal return: bank close-to-close return minus benchmark return for the same session.
- Next-session abnormal return: the next available trading session after the assigned event session.
- Abnormal volume: volume divided by the trailing median volume, calculated using prior sessions only.

Start with descriptive plots and rank/Pearson correlations. For inferential analysis, use bank and date fixed effects where sample size permits, standard errors clustered by bank and date, confidence intervals, and correction for multiple comparisons across windows. Include a baseline model with lagged returns and market movement. Report effect sizes and uncertainty rather than only p-values.

## Timing, duplicates, and confounders

Convert article timestamps to India Standard Time. Assign after-close stories to the next available exchange session. Deduplicate using normalized headline, URL, and short time windows; syndicated versions should not count as independent observations. Flag earnings releases, RBI policy decisions, major macroeconomic announcements, and other bank-specific events. Run sensitivity analyses with and without these observations.

Daily close data cannot establish the exact intraday reaction to a story. News may follow price moves, multiple stories can occur on the same day, and earnings or regulatory events may drive both tone and returns. These are central interpretation limits.

## Reproducibility and publication checklist

- Keep an immutable copy of raw data in private storage with source and retrieval notes.
- Publish code, data dictionary, annotation instructions, and only data that licenses permit.
- Freeze package versions after the environment has been checked.
- State study dates, coverage gaps, model name/version, and any excluded observations.
- Include a limitations section and avoid investment recommendations.
