# HDFC Bank data plan (2023–2026)

## Study scope

- Bank: HDFC Bank Limited
- Exchange symbol / app ticker: `HDFCBANK`
- Study dates: 2023-01-01 through 2026-11-24 (current date; extend the end date if the study is continued later)
- Benchmark: NIFTY Bank daily index close
- News language: start with English so the text matches the intended FinBERT use; preserve the original URL and publication timestamp.

## News data

**For a short pilot:** The GDELT DOC API returns article records and supports JSON or CSV output, but its searchable article window is limited to the latest three months. It cannot by itself supply a 2023–2026 history. [GDELT DOC API documentation](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/)

**For the full study period:** Check whether a university library provides a historical news archive such as Factiva, Nexis, or ProQuest, or whether Media Cloud indexes the Indian outlets and dates you need. Media Cloud date availability depends on what it has ingested, so confirm coverage for HDFC Bank before relying on it. [Media Cloud search guide](https://www.mediacloud.org/documentation/search-tool-guide)

Use search terms such as `"HDFC Bank"` and the publisher's company name/ticker when supported. Deduplicate syndicated headlines, preserve the article URL, and record the exact source/query and retrieval date. Store headlines and links rather than full article text unless the archive's license explicitly permits retaining it. Do not upload licensed material to the public app without permission.

## Price and market data

NSE's historical reports page lists security-wise price/volume archives and historical index data. NSE also has a data-for-research program for academic and non-commercial work; it asks researchers to submit its Data Seeking Request Form to `nseri@nse.co.in`. Check the current terms and whether the particular series is freely available or requires a request/fee. [NSE historical reports](https://www.nseindia.in/static/resources/historical-reports-capital-market-daily-monthly-archives), [NSE Data for Research](https://www.nse.in/static/research/initiatives-data-for-research)

The RBI Database on Indian Economy is useful for banking-sector context and banking statistics, not as a replacement for stock returns. [RBI DBIE](https://data.rbi.org.in/)

## HDFC-specific event and price adjustment

HDFC Ltd. merged into HDFC Bank effective **July 1, 2023**. Under the scheme, eligible HDFC Ltd. shareholders received 42 HDFC Bank shares for every 25 HDFC Ltd. shares. This is a major structural event in the study window. Use an appropriately adjusted price series if available, flag the merger/record-date period, and report a sensitivity analysis with and without that event window. NSE notes that displayed historical chart prices may not be adjusted for corporate actions. [HDFC Bank merger announcement](https://www.hdfc.bank.in/content/dam/hdfcbankpws/in/en/pdf/press-release/2023/q2-apr-jun/june/hdfcltdtomergeintohdfcbankeffectivejuly12023.pdf), [NSE HDFC Bank quote](https://www.nseindia.com/get-quotes/equity?symbol=HDFCBANK)

## App CSV formats

Use the headers in `data/news_template.csv` and `data/prices_template.csv`. Put `HDFCBANK` in the `ticker` column in both files. For the price file, populate `benchmark_close` with the NIFTY Bank close for the same trading date on every row. News timestamps should include the India timezone, for example `2025-01-15T11:30:00+05:30`.

The app's `close` value is used to compute close-to-close returns. If you only have unadjusted prices, record corporate actions and do not interpret the merger-period move as a normal return.
