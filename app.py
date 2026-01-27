import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from st_copy_to_clipboard import st_copy_to_clipboard

# 페이지 설정
st.set_page_config(page_title="Prompt Extractor", page_icon="🔍")
st.title("🔍 프롬프트 추출기")

# 1. 입력 방식
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
        
        # 프롬프트 추출 로직
        extracted_prompts = []
        for l in lines:
            line = l.strip()
            if len(line) > 50:
                eng_ratio = len(re.findall(r'[a-zA-Z0-9\s\(\)\,\.\:\/]', line)) / len(line)
                if eng_ratio > 0.8:
                    extracted_prompts.append(line)
        
        return "\n".join(filter(None, extracted_prompts))
    except:
        return None

# 실행 로직
if st.button("프롬프트 추출하기"):
    if post_number:
        result = extract_prompt_from_article(post_number)
        if result:
            st.session_state['current_result'] = result
        else:
            st.warning("프롬프트를 찾지 못했습니다.")
    else:
        st.error("글 번호를 입력하세요.")

# 결과 표시 및 복사 영역
if 'current_result' in st.session_state:
    st.divider()
    res_col1, res_col2 = st.columns([4, 1.2])
    
    with res_col1:
        st.subheader("✅ 추출 결과")
    
    with res_col2:
        # 이 함수가 클릭 시 복사와 토스트 기능을 동시에 수행합니다.
        st_copy_to_clipboard(
            st.session_state['current_result'], 
            before_text="Copy!", 
            after_text="Copied! ✅"
        )

    st.text_area(label="Result", value=st.session_state['current_result'], height=300, label_visibility="collapsed")
