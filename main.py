import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(page_title="서울-양평 기온 및 전력수요 분석", layout="wide")

st.title("🏙️ 서울·양평 기온 분석 및 전력수요 연결 대시보드")
st.markdown("""
이 대시보드는 대도시(서울)와 교외 지역(양평)의 기온 데이터를 비교하여 **도시 열섬현상**을 분석하고, 
나아가 **서울의 기온 변화가 전력수요에 미치는 영향**을 통합적으로 살펴봅니다.
""")

# 2. 데이터 로드 및 결측치/형식 안전 전처리 함수
@st.cache_data
def load_and_process_data():
    # 파일 읽기 (cp949 반영)
    df_s = pd.read_csv("서울_기온.csv", encoding="cp949")
    df_y = pd.read_csv("양평_기온.csv", encoding="cp949")
    df_p = pd.read_csv("전력수요.csv", encoding="cp949")
    
    # [안전 장치 1] 양끝 공백이 있을 경우를 대비해 컬럼명 및 문자열 공백 제거
    df_s.columns = df_s.columns.str.strip()
    df_y.columns = df_y.columns.str.strip()
    df_p.columns = df_p.columns.str.strip()
    
    df_s['일시'] = df_s['일시'].astype(str).str.strip()
    df_y['일시'] = df_y['일시'].astype(str).str.strip()
    df_p['일시'] = df_p['일시'].astype(str).str.strip()
    
    # [안전 장치 2] 일시 컬럼을 동일한 datetime64 형태로 변환
    df_s['일시'] = pd.to_datetime(df_s['일시'], errors='coerce')
    df_y['일시'] = pd.to_datetime(df_y['일시'], errors='coerce')
    df_p['일시'] = pd.to_datetime(df_p['일시'], errors='coerce')
    
    # 변환 실패(NaT) 데이터 제거
    df_s = df_s.dropna(subset=['일시'])
    df_y = df_y.dropna(subset=['일시'])
    df_p = df_p.dropna(subset=['일시'])
    
    # 3) [탭 1용 데이터 병합] 서울 기온과 양평 기온 inner join
    df_temp = pd.merge(df_s[['일시', '기온(°C)']], df_y[['일시', '기온(°C)']], on='일시', suffixes=('_서울', '_양평'))
    df_temp['기온차(서울-양평)'] = df_temp['기온(°C)_서울'] - df_temp['기온(°C)_양평']
    df_temp['월'] = df_temp['일시'].dt.month
    df_temp['시각'] = df_temp['일시'].dt.hour
    
    # 4) [탭 2용 데이터 병합] 서울 기온과 전력수요 inner join
    df_power = pd.merge(df_s[['일시', '기온(°C)']], df_p[['일시', '전력수요(MWh)']], on='일시')
    df_power['월'] = df_power['일시'].dt.month
    
    # 기온 구간 자동 연산을 위한 5도 단위 버림 연산
    df_power['기온구간'] = (df_power['기온(°C)'] // 5) * 5
    
    return df_temp, df_power

# 앱 구동 및 에러 트래킹 구조화
try:
    df_temp, df_power = load_and_process_data()
    
    # 데이터가 비어있는지 검증
    if df_temp.empty or df_power.empty:
        st.error("⚠️ 데이터 병합 결과가 비어있습니다. 세 파일의 '일시' 데이터 형식이 서로 일치하는지 확인해 주세요.")
    else:
        # 3. 탭 구성
        tab1, tab2 = st.tabs(["🔥 탭 1: 열섬 현상 분석", "⚡ 탭 2: 기온과 전력수요 연결"])
        
        # ==========================================
        # [탭 1: 열섬 분석]
        # ==========================================
        with tab1:
            st.header("🏙️ 서울 - 양평 도시 열섬 분석")
            
            # ① 1년간 두 지역 기온 변화 (선그래프)
            st.subheader("① 1년간 두 지역 기온 변화")
            df_line = df_temp.set_index('일시')[['기온(°C)_서울', '기온(°C)_양평']]
            df_line.columns = ['서울 기온', '양평 기온']
            st.line_chart(df_line)
            
            col1, col2 = st.columns(2)
            with col1:
                # ② 시각(0~23시)별 평균 기온차
                st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
                df_hour_diff = df_temp.groupby('시각')['기온차(서울-양평)'].mean()
                st.bar_chart(df_hour_diff)
                
            with col2:
                # ③ 월(1~12월)별 평균 기온차
                st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
                df_month_diff = df_temp.groupby('월')['기온차(서울-양평)'].mean()
                st.bar_chart(df_month_diff)

        # ==========================================
        # [탭 2: 전력 연결]
        # ==========================================
        with tab2:
            st.header("⚡ 기온 변화와 전력수요 데이터 연결")
            
            # ① 기온(가로)과 전력수요(세로)의 산점도
            st.subheader("① 기온과 전력수요 산점도")
            # 데이터 개수가 너무 많아 느려질 수 있으므로 기온과 전력수요 컬럼만 명확히 지정해 매핑
            df_scatter = df_power[['기온(°C)', '전력수요(MWh)']]
            st.scatter_chart(data=df_scatter, x='기온(°C)', y='전력수요(MWh)')
            
            col3, col4 = st.columns(2)
            with col3:
                # ② 기온 구간별 평균 전력수요 (안전한 인덱스 구조 적용)
                st.subheader("② 기온 구간별 평균 전력수요")
                df_range_demand = df_power.groupby('기온구간')['전력수요(MWh)'].mean()
                # 차트 가독성을 위해 정렬 후 출력
                st.bar_chart(df_range_demand)
                
            with col4:
                # ③ 월(1~12월)별 평균 전력수요
                st.subheader("③ 월별 평균 전력수요")
                df_month_power = df_power.groupby('월')['전력수요(MWh)'].mean()
                st.bar_chart(df_month_power)

except FileNotFoundError as e:
    st.error("⚠️ [파일을 찾을 수 없음] '서울_기온.csv', '양평_기온.csv', '전력수요.csv' 파일이 코드 파일(app.py)과 **같은 폴더** 안에 있는지 확인해 주세요.")
except KeyError as e:
    st.error(f"⚠️ [컬럼 이름 매칭 실패] 파일 내에 필요한 열 이름이 올바른지 확인해 주세요. 누락된 키: {e}")
except Exception as e:
    # Streamlit 화면에 상세 오류 코드(Traceback)를 출력하여 디버깅을 원활하게 유도
    st.error("⚠️ 예상치 못한 내부 에러가 발생했습니다.")
    st.exception(e)
