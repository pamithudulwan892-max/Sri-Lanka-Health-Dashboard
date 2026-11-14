import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sri Lanka Health Dashboard", page_icon="🇱🇰", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv("sri_lanka_health_clean.csv")


df = load_data()

# ---------- Header ----------
st.title("🇱🇰 How Sri Lanka's Health Changed Over 50 Years")
st.write(
    "Sri Lanka sharply reduced child deaths, but lifestyle diseases like obesity, "
    "high blood pressure and diabetes kept rising. Explore the data below."
)
st.caption("Source: World Health Organization – Global Health Observatory")

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
theme = st.sidebar.selectbox("Theme", sorted(df["theme"].unique()))
indicators = sorted(df.loc[df["theme"] == theme, "indicator"].unique())
indicator = st.sidebar.selectbox("Indicator", indicators)

data = df[df["indicator"] == indicator]
sex_options = sorted(data["sex"].unique())
sexes = st.sidebar.multiselect("Sex", sex_options, default=sex_options)

y_min, y_max = int(data["year"].min()), int(data["year"].max())
years = st.sidebar.slider("Years", y_min, y_max, (y_min, y_max))

data = data[data["sex"].isin(sexes) & data["year"].between(*years)]

if data.empty:
    st.warning("No data for these filters. Try selecting at least one sex.")
    st.stop()

# ---------- Key numbers ----------
main = data[data["sex"] == "Both sexes"] if "Both sexes" in sexes else data[data["sex"] == sexes[0]]
first, last = main.iloc[0], main.iloc[-1]
change = (last["value"] - first["value"]) / first["value"] * 100 if first["value"] else 0

c1, c2, c3 = st.columns(3)
c1.metric(f"Value in {int(first['year'])}", f"{first['value']:.1f}")
c2.metric(f"Value in {int(last['year'])}", f"{last['value']:.1f}")
c3.metric("Change", f"{change:+.0f}%")

# ---------- Trend chart ----------
fig = px.line(
    data, x="year", y="value", color="sex", markers=False,
    title=indicator, labels={"year": "Year", "value": indicator, "sex": "Sex"},
)
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, width="stretch")

# ---------- Story section ----------
st.divider()
st.subheader("The big picture: the 'double burden' of disease")
both = df[df["sex"] == "Both sexes"]
left, right = st.columns(2)

child = both[both["indicator"].isin([
    "Under-5 mortality (per 1,000 births)", "Infant mortality (per 1,000 births)"])]
left.plotly_chart(
    px.line(child, x="year", y="value", color="indicator",
            title="Child deaths fell sharply",
            labels={"year": "Year", "value": "Per 1,000 births", "indicator": ""})
    .update_layout(legend=dict(orientation="h", y=-0.25)),
    width="stretch",
)

lifestyle = both[both["theme"] == "Lifestyle diseases"]
right.plotly_chart(
    px.line(lifestyle, x="year", y="value", color="indicator",
            title="Lifestyle diseases kept rising",
            labels={"year": "Year", "value": "% of adults", "indicator": ""})
    .update_layout(legend=dict(orientation="h", y=-0.25)),
    width="stretch",
)

# ---------- Data table ----------
with st.expander("See the data"):
    st.dataframe(data, width="stretch", hide_index=True)
    st.download_button("Download as CSV", data.to_csv(index=False), "sri_lanka_health_filtered.csv")

st.caption("Note: most WHO data ends in 2016–2019, so recent events like COVID-19 and the 2022 crisis are not included.")
