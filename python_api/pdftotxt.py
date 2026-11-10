import fitz  # PyMuPDF
import re
import unicodedata
import numpy as np
from rapidocr_onnxruntime import RapidOCR
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, UploadFile, File


router = APIRouter()
ocr_engine = RapidOCR()
ocr_executor = ThreadPoolExecutor(max_workers=2)

# 定義我們要抓的 12 項特質
TRAITS = ["行動性", "持續性", "指導性", "挑戰性", "共感性", "情緒安定性", 
          "獨立自主性", "革新性", "思考性", "柔軟性", "感受性", "慎重性"]

# =========================================================
# 方法一：Fast Path (純文字 + 正規表達式)
# =========================================================
def parse_by_regex(pdf_bytes: bytes) -> dict:
    extracted_text = ""
    with fitz.open("pdf", pdf_bytes) as doc:
        for page in doc:
            extracted_text += page.get_text()

    # 標準化與清理
    normalized_text = unicodedata.normalize('NFKC', extracted_text)
    clean_text = re.sub(r'[\s\"\'\,\:：]+', '', normalized_text)

    scores = {t: 0 for t in TRAITS}
    for trait in TRAITS:
        # 正規表達式：尋找特質名稱，然後往後抓取 6 個字元內的數字
        pattern = rf"{trait}[^\d]{{0,6}}(\d+)"
        match = re.search(pattern, clean_text)
        if match:
            scores[trait] = int(match.group(1))
            
    return scores

# =========================================================
# 方法二：Slow Path (圖檔 OCR + XY 座標定位法)
# =========================================================
def parse_by_xy_and_ocr(pdf_bytes: bytes) -> dict:
    blocks = []
    # 執行 OCR 抓取座標
    with fitz.open("pdf", pdf_bytes) as doc:
        for page in doc:
            zoom = 300 / 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            result, _ = ocr_engine(img_array)

            if result:
                for line in result:
                    box = line[0] 
                    blocks.append({
                        'text': line[1], 
                        'x0': min(p[0] for p in box) / zoom,
                        'y0': min(p[1] for p in box) / zoom,
                        'y1': max(p[1] for p in box) / zoom
                    })

    scores = {t: 0 for t in TRAITS}
    
    # 先處理黏在一起的情況 (例如 "行動性7")
    for b in blocks:
        clean = re.sub(r'[\s:：,]', '', b['text'])
        for t in TRAITS:
            m = re.search(rf"{t}(\d+)", clean)
            if m: scores[t] = int(m.group(1))

    # 再利用 XY 座標尋找正右方的分數
    for t in TRAITS:
        if scores[t] != 0: continue 
        
        t_block = next((b for b in blocks if t in re.sub(r'\s', '', b['text'])), None)
        if not t_block: continue
        
        t_cy = (t_block['y0'] + t_block['y1']) / 2 
        valid_nums = []
        for b in blocks:
            clean_val = re.sub(r'\s', '', b['text'])
            if re.fullmatch(r'\d+', clean_val): 
                b_cy = (b['y0'] + b['y1']) / 2
                if abs(b_cy - t_cy) < 15 and b['x0'] > t_block['x0']:
                    valid_nums.append(b)
        
        if valid_nums:
            valid_nums.sort(key=lambda b: b['x0'] - t_block['x0'])
            scores[t] = int(re.sub(r'\s', '', valid_nums[0]['text']))
            
    return scores

# =========================================================
# 主程式：智慧派發邏輯
# =========================================================
async def cpas_points(pdf_bytes):
    # 策略 1：先用最快的 Regex 跑一次
    scores_dict = parse_by_regex(pdf_bytes)
    
    # 如果抓出來的分數總和是 0 (代表 Regex 抓不到，可能是圖片或排版異常)
    if sum(scores_dict.values()) == 0:
        print("⚠️ Regex 抓取失敗，啟動 OCR 空間座標分析...")
        loop = asyncio.get_event_loop()
        scores_dict = await loop.run_in_executor(ocr_executor, parse_by_xy_and_ocr, pdf_bytes)
    else:
        print("✅ 成功使用 Regex 快速抓取資料！")

    # 如果連 OCR 都抓不到，拋出錯誤
    if sum(scores_dict.values()) == 0:
        raise ValueError("無法在檔案中找到任何 CPAS 分數，請確認您上傳的是否為正確的測驗報告！")

    # 🌟 這裡原本算六大能力的程式碼已經刪除！
    # 直接回傳 12 項原始分數的字典就好
    return scores_dict

# =========================================================
# FastAPI 路由
# =========================================================
@router.post("/api/upload_pdf")
async def upload_pdf(pdf_file: UploadFile = File(...)):
    try:
        if not pdf_file.filename.lower().endswith('.pdf'):
            return {"status": "error", "message": "只能上傳 PDF 檔案喔！"}

        pdf_bytes = await pdf_file.read()
        result = await cpas_points(pdf_bytes)

        return {
            "status": "success",
            "filename": pdf_file.filename,
            # 🌟 這裡也把 "data" 拔掉了，只留下 "raw_data"
            "raw_data": result 
        }

    except ValueError as ve:
        return {"status": "error", "message": str(ve)}
    except Exception as e:
        return {"status": "error", "message": f"解析過程發生錯誤：{str(e)}"}