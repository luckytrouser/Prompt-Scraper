import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from streamlit import components

# 페이지 설정
st.set_page_config(page_title="Prompt Extractor", page_icon="🔍")
st.title("🔍 프롬프트 추출기")

# 1. 입력 방식: 기본 주소 고정 + 숫자 입력
base_url = "https://cafe.daum.net/newsolomoon/O7LJ/"
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"**기본 주소:** `{base_url}`")
with col2:
    post_number = st.text_input("글 번호 입력", placeholder="328")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://cafe.daum.net/newsolomoon/O7LJ"
}

def extract_prompt_from_article(post_id):
    try:
        content_url = f"https://m.cafe.daum.net/newsolomoon/O7LJ/{post_id}"
        response = requests.get(content_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        article_body = soup.find('div', id='article')
        
        if not article_body: return None

        content_text = article_body.get_text(separator='\n')
        lines = content_text.split('\n')
        extracted_prompts = []

        for line in lines:
            line = line.strip()
            if len(line) > 50:
                eng_chars = len(re.findall(r'[a-zA-Z0-9\s\(\)\,\.\:\/]', line))
                if eng_chars / len(line) > 0.8:
                    extracted_prompts.append(line)

        return "\n".join(filter(None, extracted_prompts))
    except Exception:
        return None

# 실행 로직
if st.button("프롬프트 추출하기"):
    if post_number:
        with st.spinner('추출 중...'):
            result = extract_prompt_from_article(post_number)
            if result:
                st.session_state['current_result'] = result
            else:
                st.warning("프롬프트를 찾지 못했습니다.")
    else:
        st.error("글 번호를 입력하세요.")

# 결과 표시 영역
if 'current_result' in st.session_state:
    st.divider()
    res_col1, res_col2 = st.columns([4, 1])
    
    with res_col1:
        st.subheader("✅ 추출 결과")
    
    with res_col2:
        # 2. 클립보드 복사 버튼 (자바스크립트 활용하되 Alert 제거)
        if st.button("Copy!"):
            js_code = f"""
                <script>
                navigator.clipboard.writeText(`{st.session_state['current_result']}`);
                </script>
            """
            components.v1.html(js_code, height=0)
            # 화면 구석에 뜨는 세련된 메시지
            st.toast("클립보드에 복사되었습니다!", icon="📋")

    # 결과물 출력 (코드 블록 형태 혹은 텍스트 영역)
    st.text_area(label="Result", value=st.session_state['current_result'], height=300, label_visibility="collapsed")
