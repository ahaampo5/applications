from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any

from app.endpoints.items.items import CardQueryInput, CardRecommendationResponse
from app.services.domain.retrieve import retrieve_similar_passages

router = APIRouter(
    prefix="/card",
    tags=["card"],
    responses={404: {"description": "Not found"}},
)

@router.post("/recommend", response_model=CardRecommendationResponse)
async def recommend_cards(card_query: CardQueryInput):
    try:
        # 카테고리를 필터로 사용하여 검색 결과를 필터링합니다
        filters = {
            "annual_fee": card_query.annual_fee,
            "card_type": card_query.card_type,
            "benefits": card_query.benefits,
            "issuer": card_query.issuer
        }
        
        # 필터와 쿼리를 사용하여 유사한 카드를 검색합니다
        recommendations = await retrieve_similar_passages(
            query=card_query.query,
            filters=filters
        )
        
        return CardRecommendationResponse(
            recommendations=recommendations,
            query=card_query.query,
            filters={k: v for k, v in filters.items() if v is not None}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"카드 추천 중 오류가 발생했습니다: {str(e)}")