# 東海大學通識課程推薦系統 (CPAS Course Recommendation System)

本專案是一套結合 **CPAS 職業適性測驗** 與 **通識課程推薦演算法** 的智慧選課平台。系統支援上傳 CPAS 評測報告 PDF 自動辨識（OCR / 正則定位）、手動輸入 12 項職業特質分數，並透過核心能力量化模型為學生推薦最契合的通識課程與職能成長路徑。

---

## 🛠️ 系統架構與技術棧

- **後端主框架 (Web Backend)**: [Laravel 11](https://laravel.com/) (PHP 8.2+)
- **前端呈現 (Frontend)**: [Vue 3](https://vuejs.org/) + [Inertia.js](https://inertiajs.com/) + [Tailwind CSS v4](https://tailwindcss.com/)
- **前端建置工具 (Build Tool)**: [Vite](https://vitejs.dev/)
- **分析與 OCR 服務 (Python Service)**: 
  - [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) (Port: 8000)
  - [PyMuPDF](https://pymupdf.readthedocs.io/) & [RapidOCR](https://github.com/RapidAI/RapidOCR) (PDF 文字解析與光學文字辨識)
  - [NumPy](https://numpy.org/) & [Pandas](https://pandas.pydata.org/) (強弱項職能矩陣計算)
- **資料庫 (Database)**: MySQL 8.0+ (以後會陸續更新)

---

## 📁 專案目錄結構

```text
├── app/                  # Laravel 核心後端代碼 (Controllers, Models, Middleware)
├── bootstrap/            # 應用程式啟動與設定引導
├── config/               # 系統設定檔
├── database/             # 資料庫遷移檔與 SQL 資料匯入檔
│   └── select_class_db.sql  # (需自行匯入/導出的資料庫結構與初始資料)
├── public/               # 公開資源目錄 (入口 index.php)
├── python_api/           # Python 推薦演算法與 PDF 解析微服務
│   ├── main.py           # FastAPI 入口程式
│   ├── pdftotxt.py       # PDF 辨識與 OCR 模組
│   ├── strong.py         # 強關係職能推薦演算法
│   ├── weak.py           # 弱關係職能推薦演算法
│   └── requirements.txt  # Python 依賴清單
├── resources/            # 前端頁面資源
│   ├── css/              # 全域樣式與 Tailwind 設定
│   ├── js/
│   │   ├── Pages/        # Vue 頁面組件 (Home, EnterScore, Result, AllCourses)
│   │   └── app.js        # Inertia 前端進入點
│   └── views/            # Blade 模板視圖
├── routes/               # 路由定義 (web.php, console.php)
├── star_dev.bat          # Windows 一鍵啟動所有開發環境批次檔
└── .env.example          # 環境變數範本檔
```

---

## ⚙️ 環境需求 (Prerequisites)

在開始安裝前，請確認你的電腦已安裝以下環境：

1. **PHP**: >= 8.2 (需啟用 `pdo_mysql`, `mbstring`, `openssl`, `curl` 等擴充套件)
2. **Composer**: >= 2.0 (PHP 套件管理工具)
3. **Node.js**: >= 18.0 & **npm**
4. **Python**: >= 3.10 (建議 3.11 ~ 3.14) & **pip**
5. **MySQL**: >= 8.0

---

## 🚀 快速安裝與建置步驟

### 1. 複製專案 (Clone Repository)
```bash
git clone https://github.com/你的帳號/你的專案名稱.git
cd 你的專案名稱
```

### 2. 安裝 PHP 與 Node.js 套件
```bash
# 安裝 Laravel 後端相依套件
composer install

# 安裝 Vue 前端相依套件
npm install
```

### 3. 安裝 Python 分析服務相依套件
```bash
pip install -r python_api/requirements.txt
```

### 4. 設定環境變數 (.env)
複製環境變數範本檔：
```bash
copy .env.example .env
```
編輯 `.env` 檔案，設定你的 MySQL 資料庫連線資訊：
```ini
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=select_class_db
DB_USERNAME=root
DB_PASSWORD=你的MySQL密碼
```

產生應用程式金鑰：
```bash
php artisan key:generate
```

### 5. 還原與設定資料庫
1. 在 MySQL 中建立名為 `select_class_db` 的資料庫。
2. 將 `database/select_class_db.sql` 匯入至 `select_class_db` 資料庫中（亦可執行 `php artisan migrate` 建立系統預設表）。

---

## 🏃 啟動系統

### 方法 A：Windows 一鍵啟動（推薦）
直接雙擊專案根目錄的 **`star_dev.bat`**：
- 自動啟動 Python FastAPI 伺服器 (`http://127.0.0.1:8000`)
- 自動啟動 Laravel 後端伺服器 (`http://127.0.0.1:8001`)
- 自動啟動 Vite 前端熱更新服務 (`http://localhost:5173`)
- 5 秒暖機後自動使用瀏覽器開啟首頁 `http://127.0.0.1:8001/index`

---

### 方法 B：手動分開啟動
若在 Linux / macOS 或想手動管理終端機，可開啟 3 個獨立終端機視窗分別執行：

1. **終端機 1：啟動 Python FastAPI 微服務 (Port 8000)**
   ```bash
   cd python_api
   python -m uvicorn main:app --reload --port 8000
   ```

2. **終端機 2：啟動 Laravel 後端 (Port 8001)**
   ```bash
   php artisan serve --port 8001
   ```

3. **終端機 3：啟動 Vite 前端熱更新**
   ```bash
   npm run dev
   ```

啟動完成後，開啟瀏覽器造訪 **`http://127.0.0.1:8001/index`** 即可開始使用！

---

## 📌 服務通訊埠一覽表 (Port Mapping)

| 服務名稱 | 預設網址 / 通訊埠 | 作用說明 |
| :--- | :--- | :--- |
| **Laravel Web** | `http://127.0.0.1:8001` | 主系統網站入口、路由管理與業務邏輯處理 |
| **Python FastAPI** | `http://127.0.0.1:8000` | PDF 解析與 OCR 座標文字辨識 API |
| **Vite Dev Server**| `http://localhost:5173` | Vue 3 前端組件熱更新與樣式編譯 |
| **MySQL Database** | `127.0.0.1:3306`        | 存放課程資料、職能矩陣與測驗歷史紀錄 |

---

## 🔒 隱私與安全性提醒
- 敏感資訊（如 `.env` 中的 `APP_KEY`、資料庫密碼）不會且不應提交至版本控制庫中。
- Python 推薦腳本 (`strong.py` / `weak.py`) 預設支援讀取 `DB_HOST`、`DB_USERNAME`、`DB_PASSWORD`、`DB_DATABASE` 等環境變數。
