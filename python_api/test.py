import fitz  # PyMuPDF
import re
import unicodedata
from fastapi import APIRouter, UploadFile, File

# 1. 初始化 FastAPI 應用程式
router = APIRouter()

# ---------------------------------------------------------
# 解析 PDF 內容與抓取分數
# ---------------------------------------------------------
def cpas_points(pdf_bytes):
    extracted_text = ""
    
    # 直接在記憶體中讀取前端傳來的 PDF 位元組
    with fitz.open("pdf", pdf_bytes) as doc:
        for page in doc:
            extracted_text += page.get_text()
            
    # 將特殊字元或全形字標準化，並清除所有空白與標點符號
    normalized_text = unicodedata.normalize('NFKC', extracted_text)
    clean_text = re.sub(r'[\s\"\'\,\:：]+', '', normalized_text)
    
    # 定義要抓取的 12 項 CPAS 人格特質
    traits = [
        "行動性", "持續性", "指導性", "挑戰性", 
        "共感性", "情緒安定性", "獨立自主性", "革新性", 
        "思考性", "柔軟性", "感受性", "慎重性"
    ]

    scores_dict = {}
    count = 0
    
    # 🌟 步驟 1：先去 PDF 抓分數
    for trait in traits:
        pattern = rf"{trait}[^\d]{{0,6}}(\d+)"
        match = re.search(pattern, clean_text)
        
        if match:
            scores_dict[trait] = int(match.group(1))
            count += 1
        else:
            scores_dict[trait] = 0  # ⚠️ 防呆：沒抓到時給 0，絕不能給 None
    
    # 🌟 步驟 2：確認是不是有效的報告
    if count == 0:
        raise ValueError("無法在檔案中找到任何 CPAS 分數，請確認您上傳的是否為正確的測驗報告！")

    # 🌟 步驟 3：回傳計算後的 6 大能力給前端
    return scores_dict

# ---------------------------------------------------------
# 接收前端的 POST 請求與實體檔案
# ---------------------------------------------------------
@router.post("/api/upload_pdf") # 注意：這裡的路由要跟 HTML 裡 fetch 的網址一致
async def upload_pdf(pdf_file: UploadFile = File(...)):
    try:
        # 防呆：確認是不是 PDF
        if not pdf_file.filename.lower().endswith('.pdf'):
            return {"status": "error", "message": "只能上傳 PDF 檔案喔！"}

        # 讀取前端用 FormData 傳來的檔案內容，轉換為 Bytes
        pdf_bytes = await pdf_file.read()
        
        # 呼叫上方的函式進行解析
        result = cpas_points(pdf_bytes)
        
        # 自動轉為 JSON 格式回傳給前端
        return {
            "status": "success", 
            "filename": pdf_file.filename,
            "raw_data": result
        }
        
    except ValueError as ve:
         # 自訂的「內容格式不符」錯誤
        return {"status": "error", "message": str(ve)}

    except Exception as e:
        return {"status": "error", "message": f"解析過程發生錯誤：{str(e)}"}