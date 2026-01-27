import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="Prompt Extractor", page_icon="🔍")
st.markdown('<h1 style="font-size: 12px;">🔍 프롬프트 추출기</h1>', unsafe_allow_html=True)

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
        extracted_prompts = [l.strip() for l in lines if len(l.strip()) > 50 and (len(re.findall(r'[a-zA-Z0-9\s\(\)\,\.\:\/]', l)) / len(l.strip()) > 0.8)]
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

# 결과 표시 영역
if 'current_result' in st.session_state:
    st.divider()
    res_col1, res_col2 = st.columns([4, 1])
    with res_col1:
        st.subheader("✅ 추출 결과")
    
    # --- 핵심: 자바스크립트 직접 주입 복사 버튼 ---
    with res_col2:
        # 이스케이프 처리를 위해 결과값 정제
        safe_result = st.session_state['current_result'].replace("`", "\\`").replace("$", "\\$")
        
        copy_button_html = f"""
            <button id="copyBtn" style="
                background-color: #ff4b4b; color: white; border: none; 
                padding: 8px 16px; border-radius: 5px; cursor: pointer;
                font-weight: bold; width: 100%;">Copy!</button>
            <script>
            document.getElementById('copyBtn').onclick = function() {{
                const text = `{safe_result}`;
                navigator.clipboard.writeText(text).then(() => {{
                    window.parent.postMessage({{type: 'streamlit:toast', data: '복사되었습니다! ✅'}}, '*');
                }}).catch(err => {{
                    console.error('복사 실패:', err);
                }});
            }}
            </script>
        """
        components.html(copy_button_html, height=45)

    st.text_area(label="Result", value=st.session_state['current_result'], height=300, label_visibility="collapsed")
