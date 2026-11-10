import os
import sys
import numpy as np
import pandas as pd
import json
import mysql.connector

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def output_error(message):
    """統一輸出 JSON 格式的錯誤訊息給 Laravel 解析"""
    print(json.dumps({"success": False, "error": message}, ensure_ascii=True))
    sys.exit(0)

def load_env_file():
    """自動讀取專案根目錄的 .env 檔案 (便於本機執行，不外洩密碼到代碼中)"""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("'\"")
                        if key not in os.environ:
                            os.environ[key] = val
        except Exception:
            pass

load_env_file()

# 1. 連線資料庫 (由 Laravel 環境變數或 .env 注入，絕不硬編碼任何密碼)
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_USER = os.environ.get("DB_USERNAME", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_DATABASE = os.environ.get("DB_DATABASE", "select_class_db")

try:
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        use_pure=True
    )
    cursor = db.cursor(buffered=True)
except Exception as e:
    output_error(f"資料庫連線失敗: {str(e)}")

try:
    # 2. 撈取 course_power
    cursor.execute("SELECT * FROM course_power")
    kmean = cursor.fetchall()

    # 3. 接收分數
    if len(sys.argv) < 7:
        output_error(f"參數數量不足，需要 6 項分數，實際收到 {len(sys.argv) - 1} 項")

    try:
        user_scores = tuple(float(sys.argv[i]) for i in range(1, 7))
    except ValueError as e:
        output_error(f"分數格式錯誤，必須是數字：{str(e)}")

    print(f"✅ 接收到的能力分數: {user_scores}", file=sys.stderr)

    # 4. 處理分數與篩選強項
    listr = []
    polist = []

    for i, po in enumerate(user_scores):
        if float(po) >= 5.0:
            polist.append(float(po))
            for row in kmean:
                if row[i] is not None:
                    listr.append(str(row[i]))
        else:
            polist.append(0.0)

    listr = list(set(listr))

    if sum(polist) == 0:
        output_error("各項能力數值皆未達強項門檻 (>=5)，無法進行課程推薦")

    print(f"篩選出的強項權重 (polist): {polist}", file=sys.stderr)
    print(f"初步符合條件的課程數量: {len(listr)} 筆", file=sys.stderr)

    # 5. 從資料庫抓取完整課程資訊並計算分數
    if not listr:
        output_error("沒有符合條件的課程，請確認課程資料庫是否有資料")

    format_strings = ','.join(['%s'] * len(listr))

    query_course = f"""
        SELECT
            p.class_id,
            d.department,
            d.class_name_chinese,
            d.class_name_english,
            d.teacher_name,         
            d.credits,
            d.classtime_classroom,
            d.course_outline,
            d.course_url,
            p.execution_power,
            p.leadership_power,
            p.affability_power,
            p.innovation_power,
            p.adaptability_power,
            p.sensitivity_power
        FROM course_plus p
        LEFT JOIN course_detail d ON p.class_id = d.class_id
        WHERE p.class_id IN ({format_strings})
    """

    cursor.execute(query_course, tuple(listr))
    db_results = cursor.fetchall()

    data_dict = {}
    course_info = {}  
    polistarr = np.array(polist)

    # ✅ 修復中斷的迴圈：補上分數計算與存入暫存字典的邏輯
    for row in db_results:
        class_id = row[0]
        department = row[1] if row[1] else "未知系所"
        course_name = row[2] if row[2] else "未知課程名稱" 
        course_name_en = row[3] if row[3] else ""
        teacher = row[4] if row[4] else "未定"             
        credits = row[5] if row[5] else "0"
        classtime = row[6] if row[6] else "未定"           
        outline = row[7] if row[7] else "暫無大綱"
        course_url = row[8] if row[8] else ""

        # 分數在 row 的第 9 到 14 格
        course_scores = np.array(row[9:], dtype=float)
        score = float(np.dot(polistarr, course_scores))
        
        data_dict[class_id] = score
        course_info[class_id] = {
            'class_name': course_name,
            'class_name_en': course_name_en,
            'department': department,
            'teacher': teacher,
            'credits': credits,
            'class_time': classtime,
            'outline': outline,
            'course_url': course_url,
        }

    # 6. 分數正規化並輸出 JSON
    data_values = list(data_dict.values())

    if not data_values:
        output_error("計算後沒有任何課程結果，請確認資料庫資料")

    old_min = min(data_values)
    old_max = max(data_values)

    last = []
    for class_id, score in data_dict.items():
        if old_max == old_min:
            new_score = 60.0
        else:
            new_score = (score - old_min) / (old_max - old_min) * (100 - 20) + 20

        # ✅ 修復：完整打包所有新欄位
        last.append({
            'class_id': str(class_id),
            'class_name': course_info[class_id]['class_name'],
            'class_name_en': course_info[class_id]['class_name_en'],
            'department': course_info[class_id]['department'],
            'teacher': course_info[class_id]['teacher'],
            'credits': course_info[class_id]['credits'],
            'class_time': course_info[class_id]['class_time'],
            'outline': course_info[class_id]['outline'],
            'course_url': course_info[class_id]['course_url'],
            'match_score': round(new_score, 2)
        })

    result_df = pd.DataFrame(last)
    result_df = result_df.sort_values(by='match_score', ascending=False)

    print(json.dumps({
        "success": True,
        "data": result_df.head(10).to_dict(orient='records')
    }, ensure_ascii=True))

except mysql.connector.Error as err:
    output_error(f"資料庫錯誤: {str(err)}")
except Exception as e:
    output_error(f"發生未預期的錯誤: {str(e)}")
finally:
    if 'cursor' in locals() and cursor is not None:
        cursor.close()
    if 'db' in locals() and db.is_connected():
        db.close()
    print("資料庫連線已安全關閉。", file=sys.stderr)