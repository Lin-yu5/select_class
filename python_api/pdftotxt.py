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

# 定義 12 項特質標準名稱及其常見辨識別名 / 錯字容錯正則
TRAIT_RULES = {
    "行動性": r"行[動动]性?",
    "持續性": r"持[續续績绩]性?",
    "指導性": r"指[導导尊]性?",
    "挑戰性": r"挑[戰战]性?",
    "共感性": r"共感性?",
    "情緒安定性": r"情[緒绪]安[定走]性?|安[定走]性?",
    "獨立自主性": r"[獨独][立立][自互]主性?|[獨独][立立]性?",
    "革新性": r"革新性?",
    "思考性": r"思考性?",
    "柔軟性": r"柔[軟软款]性?",
    "感受性": r"感受性?",
    "慎重性": r"慎重性?",
}
TRAITS = list(TRAIT_RULES.keys())

# =========================================================
# 方法一：Fast Path (純文字萃取與正則比對，針對數位 PDF)
# =========================================================
def parse_by_regex(pdf_bytes: bytes) -> dict:
    scores = {t: 0 for t in TRAITS}
    extracted_text = ""
    try:
        with fitz.open("pdf", pdf_bytes) as doc:
            for page in doc:
                extracted_text += "\n" + page.get_text()
    except Exception:
        return scores

    # 標準化與全形轉半形
    normalized_text = unicodedata.normalize('NFKC', extracted_text)

    # 針對每一項特質比對分數 (限定分數範圍 1~10，排除年份或百分比干擾)
    for trait, rule in TRAIT_RULES.items():
        # 1. 優先匹配：特質名稱直接接著 1~10 分 (如 "行動性 7"、"行動性: 8分")
        m = re.search(rf"(?:{rule})[^\d\n\r]{{0,15}}?(?<!\d)(10|[1-9])(?!\d)", normalized_text)
        if m:
            scores[trait] = int(m.group(1))
            continue

        # 2. 次優先：特質名稱同一行內的任何獨立 1~10 數字
        m_line = re.search(rf"^(?:.*)(?:{rule})(?:.*)$", normalized_text, re.MULTILINE)
        if m_line:
            nums = re.findall(r"(?<!\d)(?:10|[1-9])(?!\d)", m_line.group(0))
            if nums:
                scores[trait] = int(nums[0])

    return scores

# =========================================================
# 方法二：Slow Path (圖檔 OCR + 雙向空間座標定位法，針對掃描檔)
# =========================================================
def parse_by_xy_and_ocr(pdf_bytes: bytes) -> dict:
    blocks = []
    try:
        with fitz.open("pdf", pdf_bytes) as doc:
            for page in doc:
                # 150 DPI (zoom=2.08) 是 RapidOCR 最佳辨識解析度，比 300 DPI 快 3 倍且辨識更精準
                zoom = 150 / 72
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

                # 若為單通道灰階，轉成三通道
                if pix.n == 1:
                    img_array = np.repeat(img_array, 3, axis=2)

                result, _ = ocr_engine(img_array)
                if result:
                    for line in result:
                        box = line[0]
                        text = unicodedata.normalize('NFKC', line[1].strip())
                        x0 = min(p[0] for p in box) / zoom
                        y0 = min(p[1] for p in box) / zoom
                        x1 = max(p[0] for p in box) / zoom
                        y1 = max(p[1] for p in box) / zoom
                        blocks.append({
                            'text': text,
                            'x0': x0,
                            'y0': y0,
                            'x1': x1,
                            'y1': y1,
                            'cx': (x0 + x1) / 2,
                            'cy': (y0 + y1) / 2,
                        })
    except Exception as e:
        print(f"OCR 執行異常: {e}")
        return {t: 0 for t in TRAITS}

    scores = {t: 0 for t in TRAITS}

    # 階段 1：同一個文字塊內已包含特質與分數 (例如 "行動性 7" 或 "行動性:8")
    for b in blocks:
        for trait, rule in TRAIT_RULES.items():
            if scores[trait] != 0:
                continue
            m = re.search(rf"(?:{rule})[^\d]{{0,10}}?(?<!\d)(10|[1-9])(?!\d)", b['text'])
            if m:
                scores[trait] = int(m.group(1))

    # 階段 2：空間座標匹配 (特質在左，分數在右；或特質在上，分數在下)
    for trait, rule in TRAIT_RULES.items():
        if scores[trait] != 0:
            continue

        matched_trait_blocks = [b for b in blocks if re.search(rule, b['text'])]
        if not matched_trait_blocks:
            continue

        for t_block in matched_trait_blocks:
            candidates = []
            for b in blocks:
                if b == t_block:
                    continue
                # 嚴格限定為 1~10 分
                m_score = re.search(r"(?<!\d)(10|[1-9])(?!\d)", b['text'])
                if not m_score:
                    continue
                score_val = int(m_score.group(1))

                # 條件 A：水平右側同行 (垂直差距 < 25pt，右側 0 ~ 350pt)
                is_same_row = abs(b['cy'] - t_block['cy']) < 25
                is_to_right = 0 < (b['x0'] - t_block['x0']) < 350
                if is_same_row and is_to_right:
                    dist = b['x0'] - t_block['x1']
                    candidates.append((dist, score_val))

                # 條件 B：垂直下方同欄 (水平差距 < 30pt，下方 0 ~ 50pt)
                is_same_col = abs(b['cx'] - t_block['cx']) < 30
                is_below = 0 < (b['y0'] - t_block['y1']) < 50
                if is_same_col and is_below:
                    dist = b['y0'] - t_block['y1']
                    candidates.append((dist + 50, score_val))

            if candidates:
                candidates.sort(key=lambda c: c[0])
                scores[trait] = candidates[0][1]
                break

    return scores

# =========================================================
# 主程式：智慧派發邏輯
# =========================================================
async def cpas_points(pdf_bytes: bytes) -> dict:
    # 策略 1：先用速度最快的文字正則比對 (適用於直接匯出的數位 PDF)
    scores_dict = parse_by_regex(pdf_bytes)
    valid_count = sum(1 for v in scores_dict.values() if 1 <= v <= 10)

    # 策略 2：若文字分析未抓滿 10 項 (代表可能是掃描圖片或排版特殊)，啟動 OCR 空間座標分析
    if valid_count < 10:
        print(f"⚠️ 文字解析僅抓取到 {valid_count}/12 項，啟動 RapidOCR 空間座標分析...")
        loop = asyncio.get_event_loop()
        ocr_scores = await loop.run_in_executor(ocr_executor, parse_by_xy_and_ocr, pdf_bytes)
        # 截長補短：以 OCR 結果填補未辨識到的特質
        for trait in TRAITS:
            if scores_dict.get(trait, 0) == 0 and ocr_scores.get(trait, 0) != 0:
                scores_dict[trait] = ocr_scores[trait]
    else:
        print("✅ 成功使用純文字快速精準抓取！")

    final_valid_count = sum(1 for v in scores_dict.values() if 1 <= v <= 10)
    if final_valid_count == 0:
        raise ValueError("無法在檔案中找到任何 CPAS 分數，請確認您上傳的是否為正確的測驗報告！")

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
            "raw_data": result 
        }

    except ValueError as ve:
        return {"status": "error", "message": str(ve)}
    except Exception as e:
        return {"status": "error", "message": f"解析過程發生錯誤：{str(e)}"}
