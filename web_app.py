import streamlit as st

# 1. 대표님이 찾으신 이미지 주소 (보안상 직접 입력)
LOGO_URL = "https://github.com/malcolm-jin/kicol-fee-checker/blob/main/logo.png?raw=true"

# 2. 웹 앱 설정 (상단 탭 아이콘 변경)
st.set_page_config(
    page_title="키즈스콜레 리딩클럽 교습비 계산기",
    page_icon=LOGO_URL, 
    layout="centered"
)

# 3. 중요: 휴대폰(갤럭시/아이폰) 홈 화면 아이콘을 강제로 고정하는 코드
# 이 코드가 있어야 휴대폰이 '돛단배' 대신 대표님의 로고를 아이콘으로 사용합니다.
st.markdown(f"""
    <head>
        <link rel="apple-touch-icon" href="{LOGO_URL}">
        <link rel="icon" href="{LOGO_URL}">
    </head>
    """, unsafe_allow_html=True)

# ====== 1. 고정 값 및 로직 설정 ======
LESSON_MINUTES = 45
MONTHLY_FEE_WON = 110_000
SEARCH_MAX_SESSIONS = 20

def fmt_won(n: float) -> str:
    return f"{int(round(n)):,}원"

def fmt_num(n: float, digits: int = 2) -> str:
    return f"{n:.{digits}f}".rstrip("0").rstrip(".")

def eval_min(rate: int, weeks: float, sessions: int):
    mins = weeks * sessions * LESSON_MINUTES
    per_min = MONTHLY_FEE_WON / mins
    per_hour = per_min * 60
    max_fee = rate * mins
    ok = max_fee >= MONTHLY_FEE_WON
    return ok, per_min, per_hour, max_fee

def eval_hour(rate: int, weeks: float, sessions: int):
    hours = weeks * sessions * (LESSON_MINUTES / 60)
    per_hour = MONTHLY_FEE_WON / hours
    per_min = per_hour / 60
    max_fee = rate * hours
    ok = max_fee >= MONTHLY_FEE_WON
    return ok, per_min, per_hour, max_fee

def find_sessions(is_min_mode: bool, rate: int, weeks: float):
    for s in range(1, SEARCH_MAX_SESSIONS + 1):
        if is_min_mode:
            ok, per_min, per_hour, max_fee = eval_min(rate, weeks, s)
        else:
            ok, per_min, per_hour, max_fee = eval_hour(rate, weeks, s)
        if ok:
            return s, ok, per_min, per_hour, max_fee
    return SEARCH_MAX_SESSIONS, False, 0, 0, 0

# ====== 2. 웹 화면 구성 (UI) ======
st.set_page_config(
    page_title="키즈스콜레 리딩클럽 교습비 계산기",
    page_icon="logo.png",
    layout="centered"
)

st.title("키즈스콜레 리딩클럽 교습비 계산기")

st.markdown(
"""
**<사용 방법>** ① 관할 교육지원청 연락하여 '교습과정의 교습비 단가'와 '1개월 주 환산 값' 찾기  
② 아래 입력 후 **판정하기** 클릭  
③ TYPE 1 및 TYPE 2 참고하여 신고서에 작성
"""
)

# ✅ 핵심: 리셋용 카운터 설정 (에러 방지용)
if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0

# 계산 방식 선택
mode = st.radio("계산 방식", ["분당 단가 기준(원/분)", "시간당 단가 기준(원/시간)"], horizontal=True)
is_min = mode.startswith("분당")

# ✅ 입력창: key 이름에 숫자를 붙여 리셋 버튼 누를 때마다 새로 생성되게 함
rate_input = st.text_input(
    "① 최대 단가 입력", 
    placeholder="분당: 1~999 / 시간당: 1000 이상", 
    key=f"rate_{st.session_state.reset_counter}"
)
weeks_input = st.text_input(
    "② 한 달 주 환산 수", 
    placeholder="예: 4, 4.2, 4.3, 4.5", 
    key=f"weeks_{st.session_state.reset_counter}"
)

col1, col2 = st.columns(2)

with col1:
    btn_calc = st.button("판정하기", use_container_width=True)

with col2:
    # ✅ 리셋 버튼: 카운터 숫자를 바꿔서 입력창을 '새 걸'로 교체함
    if st.button("다시 계산하기", use_container_width=True):
        st.session_state.reset_counter += 1
        st.rerun()

# 판정 결과 실행
if btn_calc:
    if not rate_input or not weeks_input:
        st.error("① 최대 단가와 ② 한 달 주 환산 수를 모두 입력해 주세요.")
    else:
        try:
            rate_num = int(rate_input.replace(",", "").strip())
            weeks_num = float(weeks_input.replace(",", "").strip())
            
            # 유효성 검사 및 계산
            if is_min and not (1 <= rate_num <= 999):
                st.error("분당 단가 기준일 때는 1~999 사이만 입력 가능합니다.")
            elif not is_min and rate_num < 1000:
                st.error("시간당 단가 기준일 때는 1000 이상만 입력 가능합니다.")
            else:
                sessions, ok, per_min, per_hour, max_fee = find_sessions(is_min, rate_num, weeks_num)

                st.markdown("---")
                st.subheader("📋 신고서 작성용")
                
                type1_text = f"""**TYPE 1 (시간당 단가 기입)**
                
월 {fmt_won(MONTHLY_FEE_WON)}
    
시간 당 {fmt_won(round(per_hour))}"""

                type2_text = f"""**TYPE 2 (산식 기입)**
                
월 {fmt_won(MONTHLY_FEE_WON)}
    
({LESSON_MINUTES}분 * {sessions}회 * {fmt_num(weeks_num)}주)"""

                st.info(type1_text)
                st.info(type2_text)

                st.subheader("🔍 판정 상세")
                st.write(f"- 결과: **{'✅ 신고 가능' if ok else '⚠️ 조정 필요'}**")
                st.write(f"- 한 달 주 환산 수: {fmt_num(weeks_num)}주")
                st.write(f"- 주 수업수(자동 조정됨): {sessions}회")
                st.write(f"- 현재 분당 단가: {per_min:.2f}원/분")
                st.write(f"- 현재 시간당 단가: {per_hour:.0f}원/시간")
                st.write(f"- 최대 교습비(입력 단가 기준): {fmt_won(max_fee)}")
        except ValueError:
            st.error("숫자로만 정확히 입력해 주세요.")