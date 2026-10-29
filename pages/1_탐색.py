import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="탐색", layout="wide")
st.title("탐색")

# TODO: 첫 화면(app.py)에서 데이터를 읽는 주소와 똑같이 맞춰 주세요.
DATA_URL = "여기에 첫 화면과 같은 주소를 넣으세요"


@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    return pd.read_csv(url, encoding="utf-8")


df = load_data(DATA_URL)

YN = {0: "없음", 1: "있음"}
STROKE_LABEL = {0: "뇌졸중 없음", 1: "뇌졸중 있음"}

# 1. 나이와 평균 혈당의 분포
st.header("1. 나이와 평균 혈당의 분포")
col1, col2 = st.columns(2)
with col1:
    fig = px.histogram(df, x="age", title="나이 분포", labels={"age": "나이", "count": "사람 수"})
    fig.update_layout(yaxis_title="사람 수")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.histogram(
        df,
        x="avg_glucose_level",
        title="평균 혈당 분포",
        labels={"avg_glucose_level": "평균 혈당"},
    )
    fig.update_layout(yaxis_title="사람 수")
    st.plotly_chart(fig, use_container_width=True)

# 2. 뇌졸중 여부에 따른 나이·평균 혈당 비교
st.header("2. 뇌졸중 여부별 나이와 평균 혈당")
df["뇌졸중 여부"] = df["stroke"].map(STROKE_LABEL)
order = {"뇌졸중 여부": ["뇌졸중 없음", "뇌졸중 있음"]}

col1, col2 = st.columns(2)
with col1:
    fig = px.box(
        df,
        x="뇌졸중 여부",
        y="age",
        title="나이",
        labels={"age": "나이"},
        category_orders=order,
    )
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.box(
        df,
        x="뇌졸중 여부",
        y="avg_glucose_level",
        title="평균 혈당",
        labels={"avg_glucose_level": "평균 혈당"},
        category_orders=order,
    )
    st.plotly_chart(fig, use_container_width=True)

mean_table = (
    df.groupby("뇌졸중 여부")[["age", "avg_glucose_level"]]
    .mean()
    .round(2)
    .rename(columns={"age": "나이 평균", "avg_glucose_level": "평균 혈당 평균"})
    .reindex(["뇌졸중 없음", "뇌졸중 있음"])
    .reset_index()
)
st.subheader("두 그룹의 평균값")
st.dataframe(mean_table, hide_index=True, use_container_width=True)

# 3. 고혈압·심장병 여부별 뇌졸중 비율
st.header("3. 고혈압·심장병 여부별 뇌졸중 비율")
col1, col2 = st.columns(2)
for col, (column, name) in zip(
    (col1, col2),
    (("hypertension", "고혈압"), ("heart_disease", "심장병")),
):
    rate = (
        df.groupby(column)["stroke"]
        .mean()
        .mul(100)
        .round(2)
        .rename("뇌졸중 비율(%)")
        .reset_index()
    )
    rate[name] = rate[column].map(YN)
    with col:
        fig = px.bar(
            rate,
            x=name,
            y="뇌졸중 비율(%)",
            text="뇌졸중 비율(%)",
            title=f"{name} 여부별 뇌졸중 비율",
            category_orders={name: ["없음", "있음"]},
        )
        fig.update_traces(texttemplate="%{text}%")
        st.plotly_chart(fig, use_container_width=True)

# 4. bmi가 비어 있는 사람들
st.header("4. 체질량지수(bmi)가 비어 있는 사람")
bmi_missing = df[df["bmi"].isna()]
bmi_table = pd.DataFrame(
    {
        "구분": ["bmi가 비어 있는 사람", "전체"],
        "사람 수": [len(bmi_missing), len(df)],
        "뇌졸중 사람 수": [int(bmi_missing["stroke"].sum()), int(df["stroke"].sum())],
        "뇌졸중 비율(%)": [
            round(bmi_missing["stroke"].mean() * 100, 2) if len(bmi_missing) else float("nan"),
            round(df["stroke"].mean() * 100, 2),
        ],
    }
)
st.dataframe(bmi_table, hide_index=True, use_container_width=True)

# 5. 흡연 상태별 사람 수
st.header("5. 흡연 상태별 사람 수")
smoking = (
    df["smoking_status"]
    .value_counts(dropna=False)
    .rename_axis("흡연 상태")
    .reset_index(name="사람 수")
)
st.dataframe(smoking, hide_index=True, use_container_width=True)
