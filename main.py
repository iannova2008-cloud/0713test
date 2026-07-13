import streamlit as st
import pandas as pd

st.set_page_config(page_title="도시 열섬현상 분석", layout="wide")

st.title("🌆 서울과 양평의 기온 비교를 통한 도시 열섬현상 분석")

# -----------------------------
# 데이터 불러오기
# -----------------------------
seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")

# 날짜 형식 변환
seoul["일시"] = pd.to_datetime(seoul["일시"])
yangpyeong["일시"] = pd.to_datetime(yangpyeong["일시"])

# 필요한 열만 사용
seoul = seoul[["일시", "기온(°C)"]].rename(columns={"기온(°C)": "서울"})
yangpyeong = yangpyeong[["일시", "기온(°C)"]].rename(columns={"기온(°C)": "양평"})

# 데이터 병합
df = pd.merge(seoul, yangpyeong, on="일시")

# 기온차 계산
df["기온차"] = df["서울"] - df["양평"]

# 시간, 월 정보 추출
df["시간"] = df["일시"].dt.hour
df["월"] = df["일시"].dt.month

# -----------------------------
# 기본 통계
# -----------------------------
st.header("📊 기본 정보")

col1, col2, col3 = st.columns(3)

col1.metric("평균 서울 기온", f"{df['서울'].mean():.2f} ℃")
col2.metric("평균 양평 기온", f"{df['양평'].mean():.2f} ℃")
col3.metric("평균 기온차", f"{df['기온차'].mean():.2f} ℃")

# -----------------------------
# ① 연간 기온 변화
# -----------------------------
st.header("① 2025년 서울과 양평의 기온 변화")

line_df = df.set_index("일시")[["서울", "양평"]]
st.line_chart(line_df)

# -----------------------------
# ② 시간별 평균 기온차
# -----------------------------
st.header("② 시각(0~23시)별 평균 기온차 (서울 - 양평)")

hour_diff = (
    df.groupby("시간")["기온차"]
    .mean()
    .to_frame(name="평균 기온차")
)

st.bar_chart(hour_diff)

# -----------------------------
# ③ 월별 평균 기온차
# -----------------------------
st.header("③ 월(1~12월)별 평균 기온차 (서울 - 양평)")

month_diff = (
    df.groupby("월")["기온차"]
    .mean()
    .to_frame(name="평균 기온차")
)

st.bar_chart(month_diff)

# -----------------------------
# 데이터 보기
# -----------------------------
with st.expander("데이터 확인"):
    st.dataframe(df)
