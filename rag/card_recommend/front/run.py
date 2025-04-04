import streamlit as st
import requests
import json
from typing import Dict, Any, List

# 앱 제목 설정
st.title("카드 추천 시스템")
st.write("원하는 조건을 선택하고 질문을 입력하세요!")

# 사이드바 설정
st.sidebar.header("필터 설정")

# 카드 타입 선택 (2개 버튼)
st.sidebar.subheader("카드 타입")
card_type_options = ["신용카드", "체크카드"]
card_type = st.sidebar.radio("", card_type_options, index=0)

# 발급사 선택 (4개 버튼)
st.sidebar.subheader("카드 발급사")
issuer_options = ["신한", "KB국민", "우리", "하나"]
issuer = st.sidebar.radio("", issuer_options, index=None)

# 혜택 카테고리 선택
st.sidebar.subheader("혜택 카테고리")
benefit_options = ["쇼핑", "주유", "식당", "여행", "대중교통", "통신"]
benefits = st.sidebar.multiselect("원하는 혜택을 선택하세요", benefit_options)

# 연회비 범위 선택 (레인지 바)
st.sidebar.subheader("연회비 범위")
annual_fee = st.sidebar.slider(
    "연회비 범위 선택", 
    min_value=0, 
    max_value=100000, 
    value=30000, 
    step=10000,
    format="%d원"
)

# 연회비 범주화
def categorize_annual_fee(fee: int) -> str:
    if fee == 0:
        return "무료"
    elif fee <= 10000:
        return "10000원 이하"
    elif fee <= 30000:
        return "30000원 이하"
    elif fee <= 50000:
        return "50000원 이하"
    else:
        return "50000원 초과"

# 메인 컨텐츠
st.header("카드 추천 받기")

# 사용자 쿼리 입력
query = st.text_area(
    "질문을 입력하세요", 
    placeholder="예: 온라인 쇼핑몰에서 할인 혜택이 좋은 카드 추천해주세요",
    height=100
)

# 검색 버튼
if st.button("카드 추천 받기", type="primary"):
    if not query:
        st.error("질문을 입력해주세요!")
    else:
        # 로딩 표시
        with st.spinner("카드를 찾고 있습니다..."):
            try:
                # API 요청 데이터 준비
                payload = {
                    "annual_fee": categorize_annual_fee(annual_fee),
                    "card_type": card_type,
                    "benefits": ",".join(benefits) if benefits else None,
                    "issuer": issuer,
                    "query": query
                }
                
                # API 엔드포인트 - 실제 배포된 URL로 변경 필요
                api_url = "http://localhost:8000/card/recommend"
                
                # API 호출
                response = requests.post(api_url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 결과 표시
                    st.success("추천 카드를 찾았습니다!")
                    
                    # 적용된 필터 표시
                    st.subheader("적용된 필터")
                    filter_text = []
                    if payload["card_type"]:
                        filter_text.append(f"카드 타입: {payload['card_type']}")
                    if payload["issuer"]:
                        filter_text.append(f"발급사: {payload['issuer']}")
                    if payload["benefits"]:
                        filter_text.append(f"혜택: {payload['benefits']}")
                    if payload["annual_fee"]:
                        filter_text.append(f"연회비: {payload['annual_fee']}")
                    
                    st.write(", ".join(filter_text))
                    
                    # 추천 카드 표시
                    st.subheader("추천 카드 목록")
                    for i, card in enumerate(data["recommendations"]):
                        with st.expander(f"{i+1}. {card.get('title', '카드 이름')}"):
                            st.write(f"**발급사**: {card.get('issuer', '정보 없음')}")
                            st.write(f"**연회비**: {card.get('annual_fee', '정보 없음')}")
                            st.write(f"**혜택**: {card.get('benefits', '정보 없음')}")
                            st.write(f"**설명**: {card.get('description', '정보 없음')}")
                else:
                    st.error(f"API 오류: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")

# 푸터
st.markdown("---")
st.caption("© 2025 카드 추천 시스템")