from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class CardQueryInput(BaseModel):
    # 4개의 카테고리를 정의합니다 - 필요에 따라 수정하세요
    annual_fee: Optional[str] = None  # 예: "무료", "10000원", "30000원"
    card_type: Optional[str] = None   # 예: "신용카드", "체크카드"
    benefits: Optional[str] = None    # 예: "쇼핑", "주유", "항공", "식당"
    issuer: Optional[str] = None      # 예: "신한", "국민", "우리", "하나"
    
    # 사용자 쿼리
    query: str
    
    class Config:
        schema_extra = {
            "example": {
                "annual_fee": "무료",
                "card_type": "신용카드",
                "benefits": "쇼핑",
                "issuer": "신한",
                "query": "온라인 쇼핑몰에서 할인 혜택이 좋은 카드 추천해주세요"
            }
        }

class CardRecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    query: str
    filters: Dict[str, Optional[str]]