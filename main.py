import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정 및 타이틀
st.set_page_config(page_title="서울-양평 기온 비교 (도시 열섬현상)", layout="wide")

st.title("🏙️ 서울 vs 🌲 양평 기온 비교를 통한 도시 열섬현상 분석")
st.markdown("""
이 웹앱은 대도시인 **서울**과 교외 지역인 **양평**의 2025년 시간별 기온 데이터를 비교하여 
도시화로 인해 발생하는 **도시 열섬현상(Urban Heat Island Effect)**을 시각적으로 분석합니다.
""")

# 2. 데이터 불러오기 함수 (cp949 인코딩 및 캐싱 적용)
@st.cache_data
def load_data():
    # 파일명은 사용자 데이터에 맞춰 '서울_기온.csv', '양평_기온.csv'로 설정
    df_s = pd.read_csv("서울_기온.csv", encoding="cp949")
    df_y = pd.read_csv("양평_기온.csv", encoding="cp949")
    
    # 일시 데이터를 날짜/시간 형태로 변환
    df_s['일시'] = pd.to_datetime(df_s['일시'])
    df_y['일시'] = pd.to_datetime(df_y['일시'])
    
    return df_s, df_y

# 데이터 로드 및 전처리 프로세스
try:
    df_seoul, df_yangpyeong = load_data()
    
    # 분석에 필요한 컬럼만 합쳐서 새로운 데이터프레임 구성
    df_compare = pd.DataFrame({
        '일시': df_seoul['일시'],
        '서울': df_seoul['기온(°C)'],
        '양평': df_yangpyeong['기온(°C)']
    })
    
    # 서울과 양평의 기온차(서울 - 양평) 계산
    df_compare['기온차(서울-양평)'] = df_compare['서울'] - df_compare['양평']
    
    # 월(Month)과 시각(Hour) 정보 추출
    df_compare['월'] = df_compare['일시'].dt.month
    df_compare['시각'] = df_compare['일시'].dt.hour

    # 3. 사이드바 - 주요 요약 지표(Metric)
    st.sidebar.header("📊 2025년 기온 요약 요약")
    avg_seoul = df_compare['서울'].mean()
    avg_yang = df_compare['양평'].mean()
    avg_diff = df_compare['기온차(서울-양평)'].mean()
    
    st.sidebar.metric("서울 평균 기온", f"{avg_seoul:.2f} °C")
    st.sidebar.metric("양평 평균 기온", f"{avg_yang:.2f} °C")
    st.sidebar.metric("평균 기온차 (서울-양평)", f"{avg_diff:.2f} °C", delta=f"+{avg_diff:.2f} °C")

    # 4. ① 1년간 두 지역의 기온 변화 (선그래프)
    st.header("① 1년간 두 지역의 기온 변화")
    st.markdown("2025년 1년 동안 두 지역의 시간별 기온 추이입니다. 그래프의 마우스 휠을 통해 확대/축소가 가능합니다.")
    
    # st.line_chart는 인덱스를 X축으로 인식하므로 일시를 인덱스로 지정
    df_line = df_compare.set_index('일시')[['서울', '양평']]
    st.line_chart(df_line)

    st.markdown("---")

    # 하단 레이아웃을 2개의 컬럼으로 분할하여 배치
    col1, col2 = st.columns(2)

    with col1:
        # 5. ② 시각(0~23시)별 평균 기온차 (막대그래프)
        st.header("② 시각별 평균 기온차 (서울-양평)")
        st.markdown("하루 중 어느 시간대에 도시 열섬현상이 가장 강하게 나타나는지 분석합니다.")
        
        # 시각별로 그룹화하여 기온차의 평균 계산
        df_hour = df_compare.groupby('시각')['기온차(서울-양평)'].mean()
        st.bar_chart(df_hour)
        
        st.info("💡 **인사이트:** 도시의 아스팔트와 콘크리트 건물이 낮 동안 축적한 열을 밤에 방출하기 때문에, 대개 **늦은 밤부터 새벽 시간대**에 서울과 양평의 기온차가 더 벌어지는 것을 볼 수 있습니다.")

    with col2:
        # 6. ③ 월(1~12월)별 평균 기온차 (막대그래프)
        st.header("③ 월별 평균 기온차 (서울-양평)")
        st.markdown("계절의 변화에 따라 도시 열섬현상의 강도가 어떻게 달라지는지 분석합니다.")
        
        # 월별로 그룹화하여 기온차의 평균 계산
        df_month = df_compare.groupby('월')['기온차(서울-양평)'].mean()
        st.bar_chart(df_month)
        
        st.info("💡 **인사이트:** 바람이 약하고 맑은 날이 많아 방사 냉각이 잘 일어나는 **가을철이나 겨울철**에 교외 지역(양평)의 기온이 더 빠르게 떨어지므로 열섬현상이 뚜렷해지는 경향이 있습니다.")

    # 7. 원본 데이터 일부 보기
    st.markdown("---")
    st.header("📋 데이터 확인")
    with st.expander("비교 데이터프레임 상위 50개 행 보기"):
        st.dataframe(df_compare.head(50), use_container_width=True)

except FileNotFoundError as e:
    st.error("⚠️ 파일을 찾을 수 없습니다. '서울_기온.csv'와 '양평_기온.csv' 파일이 이 파이썬 스크립트와 **같은 폴더**에 있는지 확인해주세요.")
except Exception as e:
    st.error(f"⚠️ 에러가 발생했습니다: {e}")
