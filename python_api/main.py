from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#把其他 .py 檔案裡面的 router 匯入進來，並幫它們取個好辨識的別名
from pdftotxt import router as pdf_router

app = FastAPI()

# 加入 CORS 設定 (寫在 main.py 這裡就好，子程式不用寫)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 把所有子程式碼的路由「掛載」到主程式上
app.include_router(pdf_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
