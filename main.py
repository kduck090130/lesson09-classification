import json
from pathlib import Path

import pandas as pd
import streamlit as st

APP_TITLE = "뇌졸중 예측 실습실"
APP_ICON = "🧠"
DATA_URL = (
    "https://raw.githubusercontent.com/kduck090130/data/refs/heads/main/stroke.csv"
)
RECORD_DIR = Path(__file__).parent / "내_기록"
RECORD_FILE = RECORD_DIR / "기록.json"

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")


# ---------------------------------------------------------------- 저장/불러오기
def load_record() -> dict:
    """내_기록 폴더의 json 파일을 읽어 온다. 없거나 깨져 있으면 빈 기록을 돌려준다."""
    empty = {"우리말_뜻": {}, "출처": ""}
    if not RECORD_FILE.exists():
        return empty
    try:
        with open(RECORD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return empty
    meanings = data.get("우리말_뜻", {})
    source = data.get("출처", "")
    return {
        "우리말_뜻": meanings if isinstance(meanings, dict) else {},
        "출처": source if isinstance(source, str) else "",
    }


def save_record(record: dict) -> None:
    RECORD_DIR.mkdir(parents=True, exist_ok=True)
    with open(RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- 데이터
@st.cache_data(show_spinner="데이터를 불러오는 중입니다...")
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_URL, encoding="utf-8")


def describe_values(series: pd.Series) -> str:
    """열의 값이 어떤 종류인지 짧게 설명한다."""
    values = series.dropna()
    if values.empty:
        return "값 없음"
    unique = sorted(values.unique(), key=lambda v: str(v))
    if pd.api.types.is_numeric_dtype(values):
        if len(unique) <= 2:
            return "숫자 " + ", ".join(f"{v:g}" for v in unique) + f" ({len(unique)}가지)"
        return f"숫자 ({values.min():g} ~ {values.max():g})"
    return f"글자 {len(unique)}가지: " + ", ".join(str(v) for v in unique)


def big_card(label: str, value: str) -> str:
    return f"""
    <div style="border:1px solid rgba(128,128,128,0.35); border-radius:12px;
                padding:20px 12px; text-align:center;">
        <div style="font-size:0.95rem; opacity:0.75;">{label}</div>
        <div style="font-size:2.6rem; font-weight:700; line-height:1.3;">{value}</div>
    </div>
    """


# ---------------------------------------------------------------- 화면
st.title(f"{APP_ICON} {APP_TITLE}")
st.caption("뇌졸중 데이터가 어떤 데이터인지 먼저 살펴봅니다.")

try:
    df = load_data()
except Exception as e:  # 네트워크 오류 등
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()

record = load_record()

# 1) 큰 숫자 카드 네 개
total = len(df)
n_cols = df.shape[1]
n_stroke = int((df["stroke"] == 1).sum())
ratio = n_stroke / total * 100 if total else 0

c1, c2, c3, c4 = st.columns(4)
c1.markdown(big_card("전체 사람 수", f"{total:,}명"), unsafe_allow_html=True)
c2.markdown(big_card("열 개수", f"{n_cols}개"), unsafe_allow_html=True)
c3.markdown(big_card("stroke가 1인 사람 수", f"{n_stroke:,}명"), unsafe_allow_html=True)
c4.markdown(big_card("stroke가 1인 비율", f"{ratio:.1f}%"), unsafe_allow_html=True)

# 2) 열 설명 표 (우리말 뜻만 직접 입력)
st.subheader("열 설명 표")
st.caption("‘우리말 뜻’ 칸을 눌러 교재를 보고 직접 적은 뒤, 아래 [뜻 저장하기]를 눌러 주세요.")

info = pd.DataFrame(
    {
        "열 이름": df.columns,
        "우리말 뜻": [record["우리말_뜻"].get(c, "") for c in df.columns],
        "값의 종류": [describe_values(df[c]) for c in df.columns],
        "빈 값 개수": [int(df[c].isna().sum()) for c in df.columns],
    }
)

with st.form("meaning_form"):
    edited = st.data_editor(
        info,
        hide_index=True,
        use_container_width=True,
        disabled=["열 이름", "값의 종류", "빈 값 개수"],
        column_config={
            "우리말 뜻": st.column_config.TextColumn(
                "우리말 뜻", help="교재를 보고 직접 적어 보세요."
            ),
        },
    )
    saved_meaning = st.form_submit_button("뜻 저장하기")

if saved_meaning:
    record["우리말_뜻"] = {
        row["열 이름"]: ("" if pd.isna(row["우리말 뜻"]) else str(row["우리말 뜻"]))
        for _, row in edited.iterrows()
    }
    save_record(record)
    st.success("우리말 뜻을 저장했습니다. 새로고침해도 그대로 남아 있어요.")

# 3) 데이터 처음 다섯 줄
st.subheader("데이터 처음 다섯 줄")
st.dataframe(df.head(5), use_container_width=True, hide_index=True)

# 4) 데이터 출처
st.subheader("데이터 출처")
with st.form("source_form"):
    source_text = st.text_area(
        "교재에 나온 출처를 적어 주세요.",
        value=record["출처"],
        height=140,
    )
    saved_source = st.form_submit_button("출처 저장하기")

if saved_source:
    record["출처"] = source_text
    save_record(record)
    st.success("출처를 저장했습니다. 새로고침해도 그대로 남아 있어요.")
