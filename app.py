import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

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
        for l in lines:
            line = l.strip()
            if len(line) > 50:
                # 정규식 r'' 접두사로 SyntaxWarning 방지
                eng_chars = len(re.findall(r'[a-zA-Z0-9\s\(\)\,\.\:\/]', line))
                if eng_chars / len(line) > 0.8:
                    extracted_prompts.append(line)
        
        return "\n".join(filter(None, extracted_prompts))
    except:
        return None

# 실행 로직
if st.button("프롬프트 추출하기"):
    if post_number:
        with st.spinner('데이터 추출 중...'):
            result = extract_prompt_from_article(post_number)
            if result:
                st.session_state['current_result'] = result
                st.toast("추출 성공! 아래 코드를 복사하세요.", icon="✅")
            else:
                st.warning("프롬프트를 찾지 못했습니다.")
    else:
        st.error("글 번호를 입력해주세요.")

# 결과 표시 영역
if 'current_result' in st.session_state:
    st.divider()
    st.subheader("📋 추출 결과")
    st.info("우측 상단의 복사 아이콘(📋)을 클릭하면 바로 복사됩니다.")
    
    # st.code는 복사 버튼이 내장되어 있어 가장 안정적입니다.
    st.code(st.session_state['current_result'], language="text")
