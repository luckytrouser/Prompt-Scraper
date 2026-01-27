import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from streamlit import components

# 웹 페이지 설정
st.set_page_config(page_title="Prompt Extractor", page_icon="🔍")
st.title("🔍 프롬프트 추출기")

# 1. 입력 방식 개선: 기본 주소 고정 + 숫자 입력
base_url = "https://cafe.daum.net/newsolomoon/O7LJ/"
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"**기본 주소:** `{base_url}`")
with col2:
    post_number = st.text_input("글 번호 입력", placeholder="예: 328")

full_url = base_url + post_number if post_number else ""

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://cafe.daum.net/newsolomoon/O7LJ"
}

def extract_prompt_from_article(url):
    try:
        if not post_number: return None
        # 모바일 뷰 주소로 변환
        content_url = f"https://m.cafe.daum.net/newsolomoon/O7LJ/{post_number}"
        
        response = requests.get(content_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        article_body = soup.find('div', id='article')
        
        if not article_body: return "본문을 찾을 수 없습니다."

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
    except Exception as e:
        return f"오류 발생: {e}"

# 클립보드 복사를 위한 자바스크립트 함수
def st_copy_to_clipboard(text):
    copy_js = f"""
        <script>
        function copyToClipboard() {{
            const text = `{text}`;
            navigator.clipboard.writeText(text).then(() => {{
                alert('복사되었습니다!');
            }});
        }}
        copyToClipboard();
        </script>
    """
    components.v1.html(copy_js, height=0)

# 실행 및 결과 표시
if st.button("프롬프트 추출하기"):
    if post_number:
        with st.spinner('데이터를 읽어오는 중...'):
            result = extract_prompt_from_article(full_url)
            
        if result:
            # 타이틀과 복사 버튼을 한 줄에 배치
            res_col1, res_col2 = st.columns([4, 1])
            with res_col1:
                st.subheader("✅ 추출 결과")
            with res_col2:
                # 텍스트가 있을 때만 복사 버튼 활성화 (세션 상태 활용)
                st.session_state['result_text'] = result
                if st.button("Copy!"):
                    st_copy_to_clipboard(result)

            st.text_area(label="Result", value=result, height=300, label_visibility="collapsed")
        else:
            st.warning("추출된 내용이 없습니다.")
    else:
        st.error("글 번호를 입력해주세요.")
