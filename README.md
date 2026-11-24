# Banking News Sentiment and Market Reactions

**Live dashboard:** https://indian-bank-news-sentiment-research-endumrcwk96ujqm55mgu4b.streamlit.app/

Research project studying whether financial news sentiment is associated with short-term returns and unusual trading activity for Indian listed banks. This is an academic research tool, not investment advice or a trading signal.

## Research question

Does the sentiment of bank-specific financial news relate to same-day or next-trading-day market-adjusted returns and trading volume?

## Current scope

- Upload news as CSV with `published_at`, `ticker`, `headline` (optional `text`), `source`, and `url` columns.
- Upload daily prices as CSV with `date`, `ticker`, `close`, and optional `volume` columns. An optional `benchmark_close` column provides benchmark returns.
- Score text with ProsusAI/FinBERT when installed and selected; otherwise use a transparent lexicon baseline.
- Aggregate sentiment and compare it with same-day and next-day returns, relative to the uploaded benchmark when available.
- Inspect the records behind aggregate scores and export the joined analysis.

All example data in `data/sample_*.csv` is fabricated and exists only to demonstrate the interface. Do not treat it as evidence.

## Run locally

```bash
cd banking_sentiment_research
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

FinBERT downloads model weights on first use and needs a working network connection. The lexicon baseline runs without model downloads and is included for comparison, not as a validated finance model.

## Input schema

News timestamps should include a timezone where possible (for example `2025-01-15T11:30:00+05:30`). Naive timestamps are assumed to be India Standard Time. Headlines published after the 15:30 IST market close are assigned to the next trading day. Weekends and exchange holidays are rolled forward to the next date present in the price file.

Price dates should use the exchange trading date. If only `close` is supplied, simple close-to-close returns are used. Add a benchmark close series repeated for each ticker/date to estimate market-adjusted returns. The dashboard shows associations and descriptive event comparisons; it does not establish causality.

## Research plan

1. Define the sample of banks, study window, source inclusion rules, and duplicate handling before collecting data.
2. Preserve publication timestamps, article URLs, and source identifiers. Check data licensing before redistribution.
3. Manually annotate a stratified sample of headlines and report FinBERT's precision, recall, and confusion matrix against those labels.
4. Compare sentiment with same-day and next-day market-adjusted returns and abnormal volume; report sample sizes and uncertainty intervals.
5. Run robustness checks by bank type, source, event window, and removal of duplicate/syndicated articles.
6. Discuss confounders and limits. Avoid causal and predictive claims unless supported by a suitable out-of-sample design.

## Publish

This folder is prepared for Streamlit Community Cloud. Publish the folder as a GitHub repository, then create a Streamlit app pointing to `app.py` with the root directory set to `banking_sentiment_research`. For a clean public project, use a separate repository instead of the existing personal-finance repository. Add a data license/attribution note for any real dataset and never publish licensed article text without permission.

## Data starting points

- RBI Database on Indian Economy: https://data.rbi.org.in/
- NSE historical market reports: https://www.nseindia.in/static/resources/historical-reports-capital-market-daily-monthly-archives
- NSE data-sharing policy for research: https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Data%20list%20under%20NSE%20Data%20Sharing%20Policy%20for%20Research%20and%20Analysis_20250728.pdf
- Financial PhraseBank benchmark: https://huggingface.co/datasets/lmassaron/FinancialPhraseBank

Review the relevant source terms and dataset license before collecting, storing, or republishing data.
