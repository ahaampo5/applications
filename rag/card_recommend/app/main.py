from fastapi import FastAPI
from .endpoints.routers.base_router import router as base_router
# from .endpoints.routers.mago_router import router as mago_router
import logging

# logging 설정: 로그 레벨, 포맷, 파일 지정 등
logging.basicConfig(
    filename='base.log',                        # 로그를 기록할 파일 이름
    level=logging.INFO,                         # 기록할 로그 레벨 (INFO 이상)
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',  # 로그 메시지 포맷
    filemode='a'                                # 로그 파일을 append 모드로 열기 (기본값은 'a')
)

app = FastAPI()

# 엔드포인트 등록
app.include_router(base_router)
# app.include_router(mago_router)

# 예: uvicorn으로 실행할 수 있음
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=2000)