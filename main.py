import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="서울-양평 열섬현상 분석", layout="wide")

st.title("🏙️ 서울 vs 🌲 양평 기온 비교를 통한 도시 열섬현상 분석")
st.markdown("""
본 웹앱은 동일한 위도 선상에 위치하지만 도시화 정도가 다른 **서울(대도시)**과 **양평(교외 지역)**의 
2025년 기온 데이터를 비교하여 **도시 열섬현상(Urban Heat Island Effect)**을 시각적으로 확인합니다.
""")

# 1. 데이터 불러오기 (cp949 인코딩 반영)
@st.cache_data
def load_data():
    df_s = pd.read_csv("서울_기온.csv", encoding="cp949")
    df_y = pd.read_csv("양평_기온.csv", encoding="cp949")
    
    # 일시 컬럼을 datetime 형식으로 변환하여 분석에 활용
    df_s['일시'] = pd.to_datetime(df_s['일시'])
    df_y['일시'] = pd.to_datetime(df_y['일시'])
    
    return df_s, df_y

try:
    df_seoul, df_yangpyeong = load_data()
    
    # 데이터 병합 및 전처리
    df_compare = pd.DataFrame({
        '일시': df_seoul['일시'],
        '서울': df_seoul['기온(°C)'],
        '양평': df_yangpyeong['기온(°C)']
    })
    df_compare['기온차(서울-양평)'] = df_compare['서울'] - df_compare['양평']
    df_compare['월'] = df_compare['일시'].dt.month
    df_compare['시각'] = df_compare['일시'].dt.hour

    # 사이드바 요약 정보
    st.sidebar.header("📊 2025년 평균 기온 요약")
    st.sidebar.metric("서울 평균 기온", f"{df_compare['서울'].mean():.2f} °C")
    st.sidebar.metric("양평 평균 기온", f"{df_compare['양평'].mean():.2f} °C")
    st.sidebar.metric("평균 기온차 (서울-양평)", f"{df_compare['기온차(서울-양평)'].mean():.2f} °C", delta_color="inverse")

    # ---- ① 1년간 두 지역의 기온 변화 (선그래프) ----
    st.header("① 1년간 두 지역의 기온 변화")
    st.markdown("2025년 1년 동안의 서울과 양평의 전체 기온 추이입니다. (스크롤/확대 가능)")
    
    # 시각화를 위한 데이터 재구조화 (Streamlit 내장 line_chart용)
    df_line = df_compare.set_index('일시')[['서울', '양평']]
    st.line_chart(df_line)

    # 하단 2분할 레이아웃
    col1, col2 = st.columns(2)

    with col1:
        # ---- ② 시각(0~23시)별 평균 기온차 (막대그래프) ----
        st.header("② 시각별 평균 기온차 (서울 - 양평)")
        st.markdown("하루 중 어느 시간대에 열섬현상이 더 뚜렷하게 나타나는지 확인합니다.")
        
        df_hour = df_compare.groupby('시각')['기온차(서울-양평)'].mean().reset_index()
        df_hour = df_hour.set_index('시각')
        st.bar_chart(df_hour)
        st.caption("💡 대도시인 서울은 콘크리트와 아스팔트가 밤낮으로 열을 저장하고 배출하므로, 주로 **야간과 새벽 시간대**에 기온차가 커지는 경향을 보입니다.")

    with col2:
        # ---- ③ 월(1~12월)별 평균 기온차 (막대그래프) ----
        st.header("③ 월별 평균 기온차 (서울 - 양평)")
        st.markdown("계절에 따라 도시 열섬현상의 강도가 어떻게 달라지는지 확인합니다.")
        
        df_month = df_compare.groupby('월')['기온차(서울-양평)'].mean().reset_index()
        df_month = df_month.set_index('월')
        st.bar_chart(df_month)
        st.caption("💡 대체로 맑고 바람이 약한 **가을/겨울철**이나 **환절기**에 도시와 교외 간의 방사 냉각 차이로 인해 열섬현상이 더 강하게 나타날 수 있습니다.")

    # 데이터 샘플 보여주기
    st.header("📋 데이터 샘플 확인")
    st.dataframe(df_compare.head(100), use_container_width=True)

except FileNotFoundError as e:
    st.error(f"데이터 파일을 찾을 수 없습니다. '서울_기온.csv'와 '양평_기온.csv' 파일이 앱과 동일한 폴더에 있는지 확인해주세요. 상세 에러: {e}")
