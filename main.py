import streamlit as st
import pandas as pd

# -----------------------------------
# 기본 설정
# -----------------------------------
st.set_page_config(page_title="도시 열섬과 전력수요 분석", layout="wide")

st.title("🌆 도시 열섬현상과 전력수요 분석")
st.write("2025년 서울·양평 기온과 전력수요 데이터를 이용한 분석")

# -----------------------------------
# 데이터 불러오기
# -----------------------------------
seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
power = pd.read_csv("전력수요.csv", encoding="cp949")

# 날짜형 변환
seoul["일시"] = pd.to_datetime(seoul["일시"])
yangpyeong["일시"] = pd.to_datetime(yangpyeong["일시"])
power["일시"] = pd.to_datetime(power["일시"])

# -----------------------------------
# 탭 생성
# -----------------------------------
tab1, tab2 = st.tabs(["🌆 열섬 분석", "⚡ 전력 연결"])

# ===================================
# 탭1 : 열섬 분석
# ===================================
with tab1:

    st.header("서울과 양평의 기온 비교")

    # 필요한 열만 선택
    s = seoul[["일시", "기온(°C)"]].rename(columns={"기온(°C)": "서울"})
    y = yangpyeong[["일시", "기온(°C)"]].rename(columns={"기온(°C)": "양평"})

    # 병합
    temp = pd.merge(s, y, on="일시")

    # 기온차
    temp["기온차"] = temp["서울"] - temp["양평"]

    # 시간, 월
    temp["시간"] = temp["일시"].dt.hour
    temp["월"] = temp["일시"].dt.month

    # -------------------------
    # ① 연간 기온 변화
    # -------------------------
    st.subheader("① 2025년 기온 변화")

    line_df = temp.set_index("일시")[["서울", "양평"]]
    st.line_chart(line_df)

    # -------------------------
    # ② 시간별 평균 기온차
    # -------------------------
    st.subheader("② 시각별 평균 기온차 (서울 - 양평)")

    hour_diff = (
        temp.groupby("시간")["기온차"]
        .mean()
        .to_frame("평균 기온차")
    )

    st.bar_chart(hour_diff)

    # -------------------------
    # ③ 월별 평균 기온차
    # -------------------------
    st.subheader("③ 월별 평균 기온차 (서울 - 양평)")

    month_diff = (
        temp.groupby("월")["기온차"]
        .mean()
        .to_frame("평균 기온차")
    )

    st.bar_chart(month_diff)

# ===================================
# 탭2 : 전력 연결
# ===================================
with tab2:

    st.header("서울 기온과 전력수요의 관계")

    # 병합
    s = seoul[["일시", "기온(°C)"]]

    energy = pd.merge(s, power, on="일시")

    energy["월"] = energy["일시"].dt.month

    # -------------------------
    # ① 산점도
    # -------------------------
    st.subheader("① 기온과 전력수요의 관계")

    st.scatter_chart(
        energy,
        x="기온(°C)",
        y="전력수요(MWh)"
    )

    # -------------------------
    # ② 기온 구간별 평균 전력수요
    # -------------------------
    st.subheader("② 기온 구간별 평균 전력수요")

    bins = [-20, -10, 0, 10, 20, 30, 40]
    labels = [
        "-10℃ 이하",
        "-10~0℃",
        "0~10℃",
        "10~20℃",
        "20~30℃",
        "30℃ 이상"
    ]

    energy["기온구간"] = pd.cut(
        energy["기온(°C)"],
        bins=bins,
        labels=labels
    )

    temp_power = (
        energy.groupby("기온구간")["전력수요(MWh)"]
        .mean()
        .to_frame("평균 전력수요")
    )

    st.bar_chart(temp_power)

    # -------------------------
    # ③ 월별 평균 전력수요
    # -------------------------
    st.subheader("③ 월별 평균 전력수요")

    month_power = (
        energy.groupby("월")["전력수요(MWh)"]
        .mean()
        .to_frame("평균 전력수요")
    )

    st.bar_chart(month_power)

# -----------------------------------
# 데이터 보기
# -----------------------------------
with st.expander("데이터 미리보기"):
    st.write("서울 기온")
    st.dataframe(seoul.head())

    st.write("양평 기온")
    st.dataframe(yangpyeong.head())

    st.write("전력수요")
    st.dataframe(power.head())
