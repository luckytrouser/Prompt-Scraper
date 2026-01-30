import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="Prompt Extractor", page_icon="🔍")

# 봇 차단 방지용 헤더 (함수 밖으로 이동하여 공용 사용)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://cafe.daum.net/newsolomoon/O7LJ"
}

# --- [신규 함수] 최신 글 번호 탐색 ---
def get_latest_post_ids():
    try:
        list_url = "https://m.cafe.daum.net/newsolomoon/O7LJ/"
        response = requests.get(list_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=re.compile(r'/newsolomoon/O7LJ/\d+'))
        
        post_ids = []
        for link in links:
            href = link.get('href')
            match = re.search(r'/O7LJ/(\d+)', href)
            if match:
                post_ids.append(match.group(1))
        
        # 중복 제거 및 순서 유지
        unique_ids = []
        for pid in post_ids:
            if pid not in unique_ids:
                unique_ids.append(pid)
        return unique_ids
    except:
        return []

# --- UI 레이아웃 시작 ---
st.markdown('<h1 style="font-size: 12px;">🔍 프롬프트 추출기</h1>', unsafe_allow_html=True)

# [요청사항] 타이틀과 기본주소 사이에 최신 글 번호 결과 표시
latest_ids = get_latest_post_ids()
if latest_ids:
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
        <p style="margin: 0; font-size: 14px;">✅ <b>탐색 완료!</b> 가장 최근 글 번호: <b>{latest_ids[0]}</b></p>
        <p style="margin: 0; font-size: 14px;">📋 <b>상위 5개 목록:</b> {latest_ids[:5]}</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ 최신 글 번호를 불러올 수 없습니다.")

# 1. 입력 방식
base_url = "https://cafe.daum.net/newsolomoon/O7LJ/"
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"**기본 주소:** `{base_url}`")
with col2:
    # 최신 글 번호가 있으면 자동으로 기본값(value)에 채워줌
    default_id = latest_ids[0] if latest_ids else "328"
    post_number = st.text_input("글 번호 입력", value=default_id)

# --- 기존 로직 유지 ---
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

if st.button("프롬프트 추출하기"):
    if post_number:
        result = extract_prompt_from_article(post_number)
        if result:
            st.session_state['current_result'] = result
        else:
            st.warning("프롬프트를 찾지 못했습니다.")
    else:
        st.error("글 번호를 입력하세요.")

if 'current_result' in st.session_state:
    st.divider()
    res_col1, res_col2 = st.columns([4, 1])
    with res_col1:
        st.subheader("✅ 추출 결과")
    
    with res_col2:
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
