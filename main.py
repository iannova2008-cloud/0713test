<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>열섬현상과 전력수요의 관계 분석</title>
    <!-- Chart.js 및 PapaParse, 추세선 플러그인 CDN 로드 -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-trendline"></script>
    <style>
        :root {
            --primary-blue: #2b6cb0;
            --secondary-orange: #dd6b20;
            --bg-gray: #f7fafc;
            --card-bg: #ffffff;
            --text-dark: #2d3748;
            --text-muted: #718096;
            --accent-green: #319795;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
        }

        body {
            background-color: var(--bg-gray);
            color: var(--text-dark);
            line-height: 1.6;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* 헤더 디자인 */
        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 40px 20px;
            background: linear-gradient(135deg, var(--primary-blue), #4299e1);
            color: white;
            border-radius: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }

        header h1 {
            font-size: 2.2rem;
            margin-bottom: 10px;
            font-weight: 700;
        }

        header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        /* 카드 공통 디자인 */
        .card {
            background-color: var(--card-bg);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
            border: 1px solid #e2e8f0;
            transition: transform 0.2s;
        }

        .card h2 {
            font-size: 1.4rem;
            color: var(--primary-blue);
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 2px solid #edf2f7;
            padding-bottom: 8px;
        }

        /* 에러 및 로딩 메시지 창 */
        #status-message {
            display: block;
        }

        .alert-box {
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 500;
        }
        .alert-error {
            background-color: #fff5f5;
            color: #c53030;
            border: 1px solid #fed7d7;
        }
        .alert-info {
            background-color: #ebf8ff;
            color: #2b6cb0;
            border: 1px solid #bee3f8;
        }

        /* 필터 컨트롤 영역 */
        .filter-group {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 15px;
            padding: 15px;
            background-color: #f7fafc;
            border-radius: 8px;
        }

        .filter-item {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .filter-item label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
        }

        .filter-item select, .filter-item input {
            padding: 8px 12px;
            border: 1px solid #cbd5e0;
            border-radius: 6px;
            background-color: white;
            font-size: 0.95rem;
            color: var(--text-dark);
            outline: none;
        }

        .filter-item select:focus {
            border-color: var(--primary-blue);
        }

        /* Grid 배치 (반응형 2단 분할) */
        .grid-2 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
        }

        /* 그래프 콘테이너 고정 크기 제어 */
        .chart-container {
            position: relative;
            width: 100%;
            height: 400px;
            margin-top: 15px;
        }

        /* 상관관계 지표 대시보드 */
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .stat-box {
            background-color: #f7fafc;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #e2e8f0;
        }

        .stat-box .value {
            font-size: 1.8rem;
            font-weight: 700;
            margin-top: 5px;
        }
        .r-color { color: var(--secondary-orange); }
        .interpret-color { color: var(--accent-green); }

        blockquote {
            border-left: 4px solid #cbd5e0;
            padding-left: 15px;
            color: var(--text-muted);
            font-style: italic;
            margin-top: 15px;
            font-size: 0.9rem;
        }

        /* 결과 요약 리스트 스타일 */
        .result-list {
            padding-left: 20px;
        }
        .result-list li {
            margin-bottom: 10px;
        }

        /* 반응형 미디어 쿼리 모바일 타겟 */
        @media (max-width: 768px) {
            body { padding: 10px; }
            header h1 { font-size: 1.6rem; }
            header p { font-size: 1rem; }
            .grid-2 { grid-template-columns: 1fr; }
            .chart-container { height: 300px; }
        }
    </style>
</head>
<body>

<div class="container">
    <!-- 1. 제목과 탐구 질문 -->
    <header>
        <h1>🏙️ 열섬현상과 전력수요의 관계</h1>
        <p><strong>탐구 질문:</strong> 열섬 강도가 커질수록 전력수요도 증가할까?</p>
    </header>

    <!-- 데이터 불러오기 상태 안내 메시지 창 -->
    <div id="status-message">
        <div class="alert-box alert-info" id="status-text">데이터 파일을 불러오는 중입니다... 잠시만 기다려주세요.</div>
    </div>

    <!-- 2. 데이터 확인 및 필터 조건 -->
    <div class="card">
        <h2>📊 데이터 정보 및 동적 분석 필터</h2>
        <p>본 시스템은 <strong>2025년 1년 동안의 시간별 데이터(8,760행)</strong>를 연계하여 실시간 분석을 수행합니다.</p>
        <p style="font-size: 0.9rem; color: var(--text-muted); margin-top: 5px;">
            • 도심 데이터: 서울_기온.csv (변수: 일시, 기온(°C)) <br>
            • 교외 데이터: 양평_기온.csv (변수: 일시, 기온(°C)) <br>
            • 전력 데이터: 전력수요.csv (변수: 일시, 전력수요(MWh))
        </p>
        
        <div class="filter-group">
            <div class="filter-item">
                <label for="month-filter">월 선택 (시각화 대상)</label>
                <select id="month-filter" onchange="updateCharts()">
                    <option value="all">1년 전체 데이터</option>
                    <option value="1">1월 (겨울)</option>
                    <option value="2">2월</option>
                    <option value="3">3월</option>
                    <option value="4">4월</option>
                    <option value="5">5월</option>
                    <option value="6">6월 (여름)</option>
                    <option value="7">7월 (여름)</option>
                    <option value="8">8월 (여름)</option>
                    <option value="9">9월</option>
                    <option value="10">10월</option>
                    <option value="11">11월</option>
                    <option value="12">12월 (겨울)</option>
                </select>
            </div>
            <div class="filter-item" style="justify-content: flex-end;">
                <span style="font-size: 0.85rem; color: var(--text-muted); padding-bottom: 5px;" id="row-count-display">선택된 데이터: 0건</span>
            </div>
        </div>
    </div>

    <!-- 3 & 4 기온 및 전력수요 트렌드 (Grid 구조) -->
    <div class="grid-2">
        <!-- 3. 열섬현상 분석 -->
        <div class="card">
            <h2>🔥 열섬현상 분석 (기온 추이)</h2>
            <p>‘열섬 강도 = 도심 기온(서울) - 교외 기온(양평)’ 수식으로 실시간 연산된 기온의 변화 패턴입니다.</p>
            <div class="chart-container">
                <canvas id="tempChart"></canvas>
            </div>
        </div>

        <!-- 4. 전력수요 분석 -->
        <div class="card">
            <h2>⚡ 전력수요 변화 분석</h2>
            <p>선택된 분석 기간 내의 시간 흐름에 따른 전력수요 변화 그래프입니다. 기온 변동폭과 비교해 보세요.</p>
            <div class="chart-container">
                <canvas id="powerChart"></canvas>
            </div>
        </div>
    </div>

    <!-- 5. 상관관계 분석 -->
    <div class="card">
        <h2>📈 열섬 강도와 전력수요의 상관관계 분석</h2>
        <p style="margin-bottom: 15px;">연산된 열섬 강도($X$)와 전력수요($Y$)의 일대일 매핑 산점도 및 선형 추세선입니다.</p>
        
        <div class="stat-grid">
            <div class="stat-box">
                <div class="label">피어슨 상관계수 ($r$)</div>
                <div class="value r-color" id="r-value">0.00</div>
            </div>
            <div class="stat-box">
                <div class="label">상관성 자동 해석 결과</div>
                <div class="value interpret-color" id="r-interpretation">계산 중</div>
            </div>
        </div>

        <div class="chart-container" style="height: 450px;">
            <canvas id="scatterChart"></canvas>
        </div>
        
        <blockquote>
            ⚠️ <strong>통계학적 주의 안내:</strong> 두 변수 사이의 상관관계가 존재한다고 해서 반드시 한 변수가 다른 변수를 직접적으로 일으키는 '인과관계'를 의미하는 것은 아닙니다. 제3의 변수(예: 계절 변화, 절대 기온, 산업 활동량 등)가 공통적인 영향을 주고 있을 가능성을 유의해야 합니다.
        </blockquote>
    </div>

    <!-- 6. 탐구 결과 요약 -->
    <div class="card">
        <h2>📝 데이터 탐구 결과 요약</h2>
        <ul class="result-list">
            <li><strong>지리적 기온 격차:</strong> 2025년 기온 관측 자료 분석 결과 대도시 중심인 서울의 기온이 녹지가 풍부한 교외 지역인 양평에 비해 전반적으로 높게 나타나 열섬현상이 실제 존재함을 알 수 있습니다.</li>
            <li><strong>열섬과 에너지 수요의 유동성:</strong> 필터를 이용해 '여름철(6,7,8월)' 또는 특정 월을 선택하여 분석할 때와 '1년 전체'를 볼 때 상관계수 및 추세선의 형태가 다르게 나타납니다.</li>
            <li><strong>해석 유의사항:</strong> 단순 열섬 강도(두 지역의 차이)만으로는 전체 전력수요의 변동을 완전히 설명하기 어렵습니다. 이는 전력 소비가 '기온의 상대적 격차' 보다는 '당일의 절대적인 폭염 또는 한파 지수'에 더욱 민감하게 반응하기 때문으로 판단됩니다.</li>
        </ul>
    </div>
</div>

<script>
    // 글로벌 데이터 저장소
    let globalData = [];
    
    // 차트 객체 포인터들
    let tempChartObj = null;
    let powerChartObj = null;
    let scatterChartObj = null;

    // 페이지 로드 시 파일 비동기 수집 순차 처리
    window.addEventListener('DOMContentLoaded', () => {
        loadAllDataFiles();
    });

    async function loadAllDataFiles() {
        try {
            // 3개의 인코딩 지정 파일을 fetch API로 병합 로드
            const resSeoul = await fetch('서울_기온.csv');
            const resYang = await fetch('양평_기온.csv');
            const resPower = await fetch('전력수요.csv');

            if (!resSeoul.ok || !resYang.ok || !resPower.ok) {
                throw new Error("파일 로드 실패");
            }

            // 프론트엔드 한글 깨짐 방지를 위해 ArrayBuffer -> TextDecoder 처리(cp949)
            const bufSeoul = await resSeoul.arrayBuffer();
            const bufYang = await resYang.arrayBuffer();
            const bufPower = await resPower.arrayBuffer();

            const decoder = new TextDecoder('cp949');
            const textSeoul = decoder.decode(bufSeoul);
            const textYang = decoder.decode(bufYang);
            const textPower = decoder.decode(bufPower);

            // PapaParse를 통한 CSV 파싱 연동
            const csvSeoul = Papa.parse(textSeoul.trim(), { header: true, skipEmptyLines: true }).data;
            const csvYang = Papa.parse(textYang.trim(), { header: true, skipEmptyLines: true }).data;
            const csvPower = Papa.parse(textPower.trim(), { header: true, skipEmptyLines: true }).data;

            // 데이터 구조 동기화 매핑 통합 데이터셋 빌드
            // '일시' 컬럼을 기준으로 완전 매핑 매칭
            const powerMap = {};
            csvPower.forEach(item => {
                if(item['일시']) powerMap[item['일시'].trim()] = parseFloat(item['전력수요(MWh)']);
            });

            const yangMap = {};
            csvYang.forEach(item => {
                if(item['일시']) yangMap[item['일시'].trim()] = parseFloat(item['기온(°C)']);
            });

            // 최종 완전 결합 어레이 생성
            globalData = [];
            csvSeoul.forEach(item => {
                const key = item['일시'] ? item['일시'].trim() : null;
                if (key && yangMap[key] !== undefined && powerMap[key] !== undefined) {
                    const seoulTemp = parseFloat(item['기온(°C)']);
                    const yangTemp = yangMap[key];
                    const uhiStrength = seoulTemp - yangTemp; // 열섬강도 수식 정의
                    
                    // 날짜 추출 파싱
                    const dt = new Date(key.replace(/-/g, '/')); // 크로스브라우징 안정화 포맷팅
                    const month = dt.getMonth() + 1;
                    const hour = dt.getHours();

                    globalData.push({
                        datetimeStr: key,
                        month: month,
                        hour: hour,
                        seoulTemp: seoulTemp,
                        yangTemp: yangTemp,
                        uhi: uhiStrength,
                        power: powerMap[key]
                    });
                }
            });

            if(globalData.length === 0) {
                showError("데이터 매핑 실패", "세 파일의 '일시' 데이터 포맷 구조가 정확하게 일치하지 않거나 공백 상태입니다. 파일 내용을 점검해 주세요.");
                return;
            }

            // 로딩 안내창 숨김 처리 및 초기 차트 실행
            document.getElementById('status-message').style.display = 'none';
            updateCharts();

        } catch (error) {
            console.error(error);
            showError("CSV 데이터 로드 에러 안내", 
                "로컬 환경 또는 GitHub Pages 가동 중 데이터 파일을 찾을 수 없거나 불러오지 못했습니다.<br><br>" +
                "<strong>💡 문제 원인 및 해결 방법 안내:</strong><br>" +
                "1. <strong>동일 폴더 배치 확인:</strong> 'index.html'이 위치한 동일한 디렉토리에 '서울_기온.csv', '양평_기온.csv', '전력수요.csv' 파일이 정확한 대소문자 이름으로 존재하는지 확인하세요.<br>" +
                "2. <strong>웹 서버 구동 환경 확인:</strong> 브라우저 보안 정책(CORS)으로 인해 웹 페이지 파일 더블클릭 실행 시 로컬 파일 직접 접근이 차단됩니다. VS Code의 Live Server 플러그인을 사용하여 구동하거나, GitHub 리포지토리에 푸시 후 <strong>GitHub Pages 서비스</strong> 환경에서 실행하셔야 데이터가 정상 구동됩니다.");
        }
    }

    function showError(title, message) {
        const msgContainer = document.getElementById('status-text');
        msgContainer.className = "alert-box alert-error";
        msgContainer.innerHTML = `<strong>❌ ${title}</strong><br><p style='margin-top:5px; font-size:0.95rem; font-weight:normal;'>${message}</p>`;
    }

    // 통계 연산용 피어슨 상관계수 r 계산기 구동 함수
    function calculatePearsonCorrelation(xArr, yArr) {
        const n = xArr.length;
        if (n === 0) return 0;
        const sumX = xArr.reduce((a, b) => a + b, 0);
        const sumY = yArr.reduce((a, b) => a + b, 0);
        const sumXY = xArr.reduce((sum, x, i) => sum + (x * yArr[i]), 0);
        const sumX2 = xArr.reduce((sum, x) => sum + (x * x), 0);
        const sumY2 = yArr.reduce((sum, y) => sum + (y * y), 0);

        const num = (n * sumXY) - (sumX * sumY);
        const den = Math.sqrt(((n * sumX2) - (sumX * sumX)) * ((n * sumY2) - (sumY * sumY)));
        if (den === 0) return 0;
        return num / den;
    }

    // 계수 부호 및 세기에 따른 해석 엔진 자동 바인딩
    function interpretCorrelation(r) {
        const absR = Math.abs(r);
        let direction = r > 0 ? "양의 상관관계" : "음의 상관관계";
        
        if (absR < 0.1) {
            return "상관관계가 매우 약함 (두 변수 간 경향성 없음)";
        } else if (absR < 0.3) {
            return `약한 ${direction} (미미한 경향성 관측)`;
        } else if (absR < 0.6) {
            return `뚜렷한 ${direction} (중간 수준의 관련성)`;
        } else {
            return `강한 ${direction} (밀접한 선형적 비례성 관계)`;
        }
    }

    // 필터 값 변경에 의거한 차트 데이터 전면 갱신 및 드로잉 엔진
    function updateCharts() {
        const selectedMonth = document.getElementById('month-filter').value;
        
        // 데이터 필터링 수행
        const filtered = globalData.filter(d => {
            if (selectedMonth === 'all') return true;
            return d.month === parseInt(selectedMonth);
        });

        // 카운터 갱신 표시
        document.getElementById('row-count-display').innerText = `선택된 데이터 수: ${filtered.length.toLocaleString()} 건`;

        // 시각화용 데이터 배열 가공 추출
        const labelsStr = filtered.map(d => d.datetimeStr);
        const seoulTemps = filtered.map(d => d.seoulTemp);
        const yangTemps = filtered.map(d => d.yangTemp);
        const uhis = filtered.map(d => d.uhi);
        const powers = filtered.map(d => d.power);

        // 상관관계 계수 도출 및 뷰어 갱신
        const rValue = calculatePearsonCorrelation(uhis, powers);
        document.getElementById('r-value').innerText = rValue.toFixed(4);
        document.getElementById('r-interpretation').innerText = interpretCorrelation(rValue);

        // --- ① 열섬 현상 기온 차트 객체 빌드 ---
        if (tempChartObj) tempChartObj.destroy();
        const ctxTemp = document.getElementById('tempChart').getContext('2d');
        tempChartObj = new Chart(ctxTemp, {
            type: 'line',
            data: {
                labels: labelsStr,
                datasets: [
                    { label: '도심 기온 (서울)', data: seoulTemps, borderColor: '#4299e1', backgroundColor: 'transparent', borderWidth: 1.5, pointRadius: 0 },
                    { label: '교외 기온 (양평)', data: yangTemps, borderColor: '#48bb78', backgroundColor: 'transparent', borderWidth: 1.5, pointRadius: 0 },
                    { label: '열섬 강도 (서울-양평)', data: uhis, borderColor: '#e53e3e', backgroundColor: 'transparent', borderWidth: 1.5, pointRadius: 0 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { position: 'top' }
                },
                scales: {
                    x: { ticks: { maxTicksLimit: 10, display: true } },
                    y: { title: { display: true, text: '기온 (°C)' } }
                }
            }
        });

        // --- ② 전력 수요 차트 객체 빌드 ---
        if (powerChartObj) powerChartObj.destroy();
        const ctxPower = document.getElementById('powerChart').getContext('2d');
        powerChartObj = new Chart(ctxPower, {
            type: 'line',
            data: {
                labels: labelsStr,
                datasets: [{
                    label: '전력수요(MWh)',
                    data: powers,
                    borderColor: varSecondaryOrange = '#dd6b20',
                    backgroundColor: 'rgba(221, 107, 32, 0.1)',
                    borderWidth: 1.5,
                    pointRadius: 0,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } },
                scales: {
                    x: { ticks: { maxTicksLimit: 10 } },
                    y: { title: { display: true, text: '전력수요 (MWh)' } }
                }
            }
        });

        // --- ③ 산점도 및 선형 추세선 객체 빌드 ---
        if (scatterChartObj) scatterChartObj.destroy();
        const ctxScatter = document.getElementById('scatterChart').getContext('2d');
        
        // 산점도 전용 데이터 포맷 가공 [{x: 1, y: 2}]
        const scatterPoints = filtered.map(d => ({ x: d.uhi, y: d.power }));

        scatterChartObj = new Chart(ctxScatter, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: '시점별 분포 지표 데이터',
                    data: scatterPoints,
                    backgroundColor: 'rgba(43, 108, 176, 0.4)',
                    borderColor: 'rgba(43, 108, 176, 0.7)',
                    pointRadius: 3,
                    // chartjs-plugin-trendline 옵션 탑재 구동 설정
                    trendlineLinear: {
                        style: "rgba(229, 62, 62, 0.9)",
                        lineStyle: "solid",
                        width: 2.5
                    }
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `열섬강도: ${context.parsed.x.toFixed(1)}°C, 전력수요: ${context.parsed.y.toLocaleString()} MWh`;
                            }
                        }
                    }
                },
                scales: {
                    x: { title: { display: true, text: '열섬 강도 = 도심 기온 - 교외 기온 (°C)' } },
                    y: { title: { display: true, text: '전력수요 (MWh)' } }
                }
            }
        });
    }
</script>
</body>
</html>

# ---------- 마무리 질문 ----------
st.divider()
st.info("💬 **생각해 보기** — 도시는 밤에 잘 식지 않아 더 덥습니다(열섬). "
        "더우면 냉방을 켜고, 실외기는 다시 열을 내뿜죠. "
        "두 탭의 그래프를 근거로 '더위 → 냉방 → 더 큰 더위'의 고리를 설명해 봅시다.")
