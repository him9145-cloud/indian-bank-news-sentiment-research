"""Interactive exploration of Indian bank news sentiment and market reactions."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from analysis import analyze


st.set_page_config(page_title="Banking News Sentiment Research", page_icon="🏦", layout="wide")
st.title("Banking News Sentiment & Market Reactions")
st.caption("Research dashboard for Indian listed banks · Descriptive analysis, not investment advice")
st.info("The bundled example files contain fabricated demo data. Upload real, properly licensed research data before drawing conclusions.")

left, right = st.columns(2)
with left:
    news_file = st.file_uploader("News CSV", type="csv", key="news")
with right:
    price_file = st.file_uploader("Daily prices CSV", type="csv", key="prices")

with st.expander("Expected columns and timestamp rules"):
    st.markdown("""
    **News:** `published_at`, `ticker`, `headline`; optional `text`, `source`, `url`.

    **Prices:** `date`, `ticker`, `close`; optional `volume`, `benchmark_close`.

    Use a timezone in publication timestamps when possible. Naive timestamps are read as IST. Stories after 15:30 IST are matched to the next trading session present in the price file. `benchmark_close` should represent the same benchmark for every bank on a given date.
    """)

model = st.radio("Sentiment method", ["FinBERT", "Lexicon baseline"], horizontal=True,
                help="FinBERT downloads its pretrained weights the first time it runs. The lexicon is a simple comparison baseline.")

if news_file and price_file:
    try:
        news = pd.read_csv(news_file)
        prices = pd.read_csv(price_file)
        with st.spinner("Scoring text and aligning news with trading sessions…"):
            detail, summary = analyze(news, prices, model=model)
    except Exception as exc:
        st.error(f"Could not analyze these files: {exc}")
        st.stop()
else:
    data_dir = Path(__file__).parent / "data"
    news = pd.read_csv(data_dir / "sample_news.csv")
    prices = pd.read_csv(data_dir / "sample_prices.csv")
    if st.button("Load bundled fabricated demo"):
        st.session_state["use_demo"] = True
    if not st.session_state.get("use_demo"):
        st.caption("Upload both CSV files to analyze your data. Select the demo button to explore the dashboard with fabricated examples.")
        st.stop()
    try:
        detail, summary = analyze(news, prices, model=model)
    except Exception as exc:
        st.error(f"Could not analyze demo data: {exc}")
        st.stop()

if summary.empty:
    st.warning("No records could be matched to available trading dates. Check tickers, dates, and sample overlap.")
    st.stop()

detail = detail.dropna(subset=["event_date"])
tickers = sorted(detail["ticker"].dropna().unique())
selected = st.multiselect("Banks", tickers, default=tickers)
detail = detail[detail.ticker.isin(selected)]
summary = summary[summary.ticker.isin(selected)]

metric1, metric2, metric3 = st.columns(3)
metric1.metric("Articles aligned", f"{len(detail):,}")
metric2.metric("Banks covered", f"{detail.ticker.nunique():,}")
metric3.metric("Mean sentiment", f"{detail.sentiment_score.mean():+.3f}" if len(detail) else "—")

if not detail.empty:
    c1, c2 = st.columns(2)
    with c1:
        sentiment_plot = px.scatter(summary, x="event_date", y="mean_sentiment", color="ticker", size="article_count",
                                    hover_data=["article_count", "positive_share"], title="Daily news sentiment by bank")
        sentiment_plot.add_hline(y=0, line_dash="dot", line_color="gray")
        st.plotly_chart(sentiment_plot, use_container_width=True)
    with c2:
        returns_plot = px.scatter(summary, x="mean_sentiment", y="next_abnormal_return", color="ticker", size="article_count",
                                  hover_data=["event_date", "article_count"], title="Sentiment vs next-session market-adjusted return")
        st.plotly_chart(returns_plot, use_container_width=True)

    if "relative_volume" in detail:
        st.subheader("News-day trading activity")
        st.plotly_chart(px.scatter(detail, x="sentiment_score", y="relative_volume", color="ticker", hover_data=["event_date", "headline"],
                                   title="News sentiment vs relative trading volume"), use_container_width=True)

    st.subheader("Bank-day observations")
    st.dataframe(summary.sort_values("event_date", ascending=False), use_container_width=True, hide_index=True)
    st.subheader("Scored news records")
    visible = [c for c in ["published_at", "event_date", "ticker", "sentiment", "sentiment_score", "headline", "source", "url", "abnormal_return", "next_abnormal_return"] if c in detail]
    st.dataframe(detail[visible].sort_values("published_at", ascending=False), use_container_width=True, hide_index=True)
    st.download_button("Download joined analysis CSV", detail.to_csv(index=False).encode("utf-8"), "bank_news_analysis.csv", "text/csv")

st.caption("Associations are exploratory. These charts do not establish causality or guarantee predictive performance. Evaluate model errors and uncertainty before interpreting findings.")
