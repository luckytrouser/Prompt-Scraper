import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# 웹 페이지 제목 설정
st.set_page_config(page_title="Prompt Extractor", page_icon="🔍")
st.title("🔍 카페 프롬프트 추출기")
st.markdown("다음 카페 게시글 주소를 입력하면 프롬프트만 쏙 뽑아드립니다.")

# 입력창 (UI)
test_url = st.text_input("카페 게시글 주소를 입력하세요", placeholder="https://cafe.daum.net/...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://cafe.daum.net/newsolomoon/O7LJ"
}

def extract_prompt_from_article(url):
    try:
        # URL에서 ID 추출 로직 개선
        if not url or '/' not in url: return None
        dataid = url.split('/')[-1].split('?')[0]
        content_url = f"https://m.cafe.daum.net/newsolomoon/O7LJ/{dataid}"
        
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

# 버튼 클릭 시 실행
if st.button("프롬프트 추출하기"):
    if test_url:
        with st.spinner('데이터를 읽어오는 중...'):
            result = extract_prompt_from_article(test_url)
            
        if result:
            st.subheader("✅ 추출 결과")
            # 텍스트 영역에 표시하여 복사하기 쉽게 만듦
            st.text_area(label="Result", value=result, height=300, label_visibility="collapsed")
            st.success("위 텍스트를 복사해서 사용하세요!")
        else:
            st.warning("추출된 내용이 없습니다.")
    else:
        st.error("주소를 입력해주세요.")
