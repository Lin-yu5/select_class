<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Symfony\Component\Process\Process;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\DB;
use Inertia\Inertia;


class CpasResultController extends Controller
{
    // ==========================================
    // 🌟 PDF 上傳流程主程式
    // ==========================================
    public function processPdf(Request $request)
    {
        set_time_limit(120);

        $request->validate([
            'pdf_file' => 'required|mimes:pdf|max:10240',
        ]);

        $file = $request->file('pdf_file');

        // ==========================================
        // 🏃 接力棒 1：Laravel 呼叫 FastAPI 解析 PDF
        // ==========================================
        try {
            $pdfResponse = Http::timeout(180)->attach(
                'pdf_file', file_get_contents($file->getRealPath()), $file->getClientOriginalName()
            )->post('http://127.0.0.1:8000/api/upload_pdf');

        } catch (\Illuminate\Http\Client\ConnectionException $e) {
            // ✅ 只有真正連不上時才顯示「伺服器未開啟」
            Log::error('FastAPI 連線失敗: ' . $e->getMessage());
            return back()->withErrors(['msg' => '無法連線到 Python 伺服器，請確認 FastAPI 是否已啟動（port 8000）']);
        } catch (\Exception $e) {
            // ✅ 其他錯誤顯示真實訊息，方便除錯
            Log::error('呼叫 FastAPI 發生例外: ' . $e->getMessage());
            return back()->withErrors(['msg' => '呼叫 FastAPI 時發生錯誤：' . $e->getMessage()]);
        }

        // ✅ 連線成功後，再檢查回應內容
        if (!$pdfResponse->successful()) {
            Log::error('FastAPI 回應非 2xx，狀態碼：' . $pdfResponse->status() . '，內容：' . $pdfResponse->body());
            return back()->withErrors(['msg' => 'FastAPI 回應異常（HTTP ' . $pdfResponse->status() . '），請查看 FastAPI 終端機']);
        }

        $pdfData = $pdfResponse->json();

        if (!isset($pdfData['status']) || $pdfData['status'] !== 'success') {
            // ✅ 直接把 Python 的錯誤訊息傳給前端
            $errorMsg = $pdfData['message'] ?? $pdfData['msg'] ?? 'PDF 解析失敗，請確認上傳的是正確的 CPAS 報告';
            Log::error('FastAPI 解析失敗: ' . $errorMsg);
            return back()->withErrors(['msg' => $errorMsg]);
        }

        // 🌟 1. 抓取 FastAPI 回傳的「12項原始分數」
        $rawScores = $pdfData['raw_data'];

        // 🌟 2. 依照 EnterScore.vue 裡面的 12 項順序，把分數排好
        // 注意：這裡直接對應 Python 回傳的中文 Key
        $orderedScores = [
            intval($rawScores['行動性'] ?? 0),
            intval($rawScores['持續性'] ?? 0),
            intval($rawScores['指導性'] ?? 0),
            intval($rawScores['挑戰性'] ?? 0),
            intval($rawScores['共感性'] ?? 0),
            intval($rawScores['情緒安定性'] ?? 0),
            intval($rawScores['獨立自主性'] ?? 0),
            intval($rawScores['革新性'] ?? 0),
            intval($rawScores['思考性'] ?? 0),
            intval($rawScores['柔軟性'] ?? 0),
            intval($rawScores['感受性'] ?? 0),
            intval($rawScores['慎重性'] ?? 0),
        ];

        Log::info('PDF 解析成功，12 項原始分數準備跳轉手動輸入頁面', $orderedScores);

        // ==========================================
        // 🏁 終點：不直接呼叫推薦系統，而是帶著分數跳到 EnterScore 頁面！
        // ==========================================
        return Inertia::render('EnterScore', [
            'parsedScores' => $orderedScores
        ]);
    }

    // ==========================================
    // 手動輸入分數版本的推薦流程
    // ==========================================
    public function processManual(Request $request)
    {
        $request->validate([
            'scores'     => 'required|array|size:12',
            'scores.*'   => 'required|integer|min:1|max:10',
            'student_id' => 'required|string',
            'student_name'       => 'nullable|string',
            'student_department' => 'nullable|string'
        ]);

        $raw       = $request->input('scores');
        $studentId = $request->input('student_id');
        $stuName   = $request->input('student_name', '未填寫姓名');     
        $stuDept   = $request->input('student_department', '未填寫系所');

        $studentExists = DB::table('students')->where('stu_id', $studentId)->exists();
        
        if (!$studentExists) {
            DB::table('students')->insert([
                'stu_id'         => $studentId,
                'stu_name'       => $stuName,  // 🌟 存入真正的姓名
                'stu_department' => $stuDept   // 🌟 存入真正的系所
            ]);
        }

        DB::table('cpas_points')->updateOrInsert(
            ['student_id' => $studentId],
            [
                'action'      => $raw[0],  'persistence' => $raw[1],
                'leader'      => $raw[2],  'challenge'   => $raw[3],
                'empathy'     => $raw[4],  'stability'   => $raw[5],
                'independen'  => $raw[6],  'innovation'  => $raw[7],
                'thinking'    => $raw[8],  'flexibility' => $raw[9],
                'sensitivity' => $raw[10], 'prudence'    => $raw[11],
            ]
        );

        $scores = [
            ($raw[0]  + $raw[1])  / 2,  // 執行力
            ($raw[2]  + $raw[3])  / 2,  // 統御力
            ($raw[4]  + $raw[5])  / 2,  // 親和力
            ($raw[6]  + $raw[7])  / 2,  // 開創力
            ($raw[8]  + $raw[9])  / 2,  // 應變力
            ($raw[10] + $raw[11]) / 2,  // 敏感力
        ];

        DB::table('cpas_core6')->updateOrInsert(
            ['student_id' => $studentId],
            [
                'execution_power'    => $scores[0],
                'leadership_power'   => $scores[1],
                'affability_power'   => $scores[2],
                'innovation_power'   => $scores[3],
                'adaptability_power' => $scores[4],
                'sensitivity_power'  => $scores[5],
            ]
        );
// ==========================================
    // 🌟 補足 Windows 環境變數 (專治 10106 TCP/IP socket 錯誤)
    // ==========================================
        // 將系統原有的變數，與 Windows 網路底層必備的變數合併
        $windowsEnv = array_merge(getenv(), $_SERVER, $_ENV, [
            'SystemRoot'  => 'C:\Windows',
            'SystemDrive' => 'C:',
            'DB_HOST'     => config('database.connections.mysql.host', '127.0.0.1'),
            'DB_PORT'     => (string) config('database.connections.mysql.port', '3306'),
            'DB_DATABASE' => config('database.connections.mysql.database', 'select_class_db'),
            'DB_USERNAME' => config('database.connections.mysql.username', 'root'),
            'DB_PASSWORD' => (string) config('database.connections.mysql.password', ''),
        ]);

    // ==========================================
    // 🌟 1. 強關係課程推薦 (執行 strong.py)
    // ==========================================
        $strongPath = base_path('python_api/strong.py');
        
        // ⚠️ 關鍵修正：將 $windowsEnv 作為第三個參數傳入 Process
        $processStrong = new Process(
            array_merge(['python', $strongPath], array_map('strval', $scores)),
            null, // 工作目錄 (預設)
            $windowsEnv // 👈 強制灌入完整的環境變數！
        );
        $processStrong->setTimeout(60)->run(); 

        if (!$processStrong->isSuccessful()) {
            dd("🕵️‍♂️ strong.py 內部報錯當機：", $processStrong->getErrorOutput());
        }
        $strongOutput = json_decode(trim($processStrong->getOutput()), true);
        if (!$strongOutput || !isset($strongOutput['success']) || !$strongOutput['success']) {
            return back()->withErrors(['msg' => $strongOutput['error'] ?? '強關係腳本發生未知錯誤']);
        }
        $strongCourses = $strongOutput['data'] ?? [];

    // ==========================================
    // 🌟 2. 弱關係課程推薦 (執行 weak.py)
    // ==========================================
        $weakPath = base_path('python_api/weak.py');
        
        // ⚠️ 關鍵修正：弱關係也必須傳入 $windowsEnv
        $processWeak = new Process(
            array_merge(['python', $weakPath], array_map('strval', $scores)),
            null,
            $windowsEnv // 👈 一樣強制灌入
        );
        $processWeak->setTimeout(60)->run(); 

        if (!$processWeak->isSuccessful()) {
            dd("🕵️‍♂️ weak.py 執行失敗！錯誤訊息：", $processWeak->getErrorOutput());
        }

        $weakCourses = [];
        if ($processWeak->isSuccessful()) {
            $weakOutput = json_decode(trim($processWeak->getOutput()), true);
            if ($weakOutput && isset($weakOutput['success']) && $weakOutput['success']) {
                $weakCourses = $weakOutput['data'] ?? [];
            } else {
                Log::info('弱關係推薦提示：' . ($weakOutput['error'] ?? '無'));
            }
        } else {
            Log::warning('弱關係推薦執行失敗：' . $processWeak->getErrorOutput());
        }

    // ==========================================
    // 🌟 3. 合併課程，並打上「強/弱」關係標籤
    // ==========================================
        $powerMap = $this->buildPowerMap(); // 取得資料庫的職能標籤
        $allRecommendations = [];
        $seenClassIds = []; // 記錄已經存入陣列的 class_id 與其索引位置

        // 處理強關係課程
        foreach ($strongCourses as $course) {
            $cid = (int)$course['class_id'];
            $course['powers'] = $powerMap[$cid] ?? [];
            $course['relation_type'] = 'strong'; // 👈 貼上「強關係」標籤
            
            $allRecommendations[] = $course;
            $seenClassIds[$cid] = count($allRecommendations) - 1; // 記錄在陣列的第幾個位置
        }

        // 處理弱關係課程
        foreach ($weakCourses as $course) {
            $cid = (int)$course['class_id'];
            
            if (isset($seenClassIds[$cid])) {
                // 如果這門課已經在強關係出現過，就把它改為 'both' (兩者皆有)
                $index = $seenClassIds[$cid];
                $allRecommendations[$index]['relation_type'] = 'both';
                $strongScore = $allRecommendations[$index]['match_score'];
            } else {
                // 如果是新課程，就貼上「弱關係」標籤並加入陣列
                $course['powers'] = $powerMap[$cid] ?? [];
                $course['relation_type'] = 'weak';
                
                $allRecommendations[] = $course;
                $seenClassIds[$cid] = count($allRecommendations) - 1;
            }
        }
    $urlMap = DB::table('course_detail')->pluck('course_url', 'class_id')->toArray();
    foreach ($allRecommendations as &$course) {
        $cid = $course['class_id'] ?? null;
        $course['course_url'] = $urlMap[$cid] ?? ''; // 找不到就給空字串
    }
    // ==========================================
    // 🌟 新增：把這次算出來的所有結果，整包丟進歷史紀錄保險箱
    // ==========================================
    DB::table('cpas_history')->insert([
        'student_id'          => $studentId, // 剛剛拿到的學號
        'raw_scores'          => json_encode($raw), // 12項原始分數
        'core6_scores'        => json_encode($scores), // 6大能力分數
        'recommended_courses' => json_encode($allRecommendations) // 算好的強弱推薦課程包
        // created_at 資料庫會自動塞當下的時間進去，所以不用寫！
    ]);

    // ==========================================
    // 🌟 4. 將最終打包好的資料傳給前端
    // ==========================================
        return Inertia::render('Result', [
            'userScores'      => $scores,
            'recommendations' => $allRecommendations,
        ]);
    }

    // 保留：單獨查看某學生結果的頁面
    public function show($student_id)
    {
        $clean_id = trim($student_id);
        $data = DB::table('cpas_core6')
            ->where('student_id', $clean_id)
            ->first();

        return view('cpas.result', ['scores' => $data]);
    }

    // ==========================================
    // 🌟 全新修改：直接從 Laravel 資料庫撈取所有課程
    // ==========================================
    // course_power 表的結構是「橫向欄位」：
    // 每一欄（execution_power, leadership_power...）底下列出具備該職能的課程 class_id
    // 例如 execution_power 欄位裡出現 3003，代表 class_id=3003 這門課具備「執行力」
    // 這個函式把整張表轉換成 class_id => [職能英文key, ...] 的對照表，方便之後查詢
    private function buildPowerMap(): array
    {
        $rows = DB::table('course_power')->get();

        // 資料庫欄位名稱 -> 前端篩選用的英文 key
        $columnToKey = [
            'execution_power'    => 'Execution',
            'leadership_power'   => 'Leadership',
            'affability_power'   => 'Affability',
            'innovation_power'   => 'Innovation',
            'adaptability_power' => 'Adaptability',
            'sensitivity_power'  => 'Sensitivity',
        ];

        $map = []; // class_id => [power_key, power_key, ...]

        foreach ($rows as $row) {
            foreach ($columnToKey as $column => $powerKey) {
                $classId = $row->$column ?? null;

                if ($classId === null || $classId === '') {
                    continue; // 跳過 NULL（該欄位這一列沒有資料）
                }

                $classId = (int) $classId;

                if (!isset($map[$classId])) {
                    $map[$classId] = [];
                }

                if (!in_array($powerKey, $map[$classId], true)) {
                    $map[$classId][] = $powerKey;
                }
            }
        }

        return $map;
    }

    public function allCourses()
    {
        try {
            $courses  = DB::table('course_detail')->get();
            $powerMap = $this->buildPowerMap();

            Log::info('撈到課程數量：' . $courses->count());
            Log::info('course_power 對照表筆數：' . count($powerMap));

            // 將資料庫的每一筆課程，轉換成 Vue 前端預期的格式
            $formattedCourses = $courses->map(function ($course) use ($powerMap) {
                $classId = (int) ($course->class_id ?? $course->id ?? 0);

                return [
                    'class_id'            => $classId ?: rand(1000, 9999),
                    'class_name_chinese'  => $course->class_name_chinese ?? $course->class_name ?? '未知課程',
                    'class_name_english'  => $course->class_name_english ?? '',
                    'teacher_name'        => $course->teacher_name ?? $course->teacher ?? '',
                    'department'          => $course->department ?? '',
                    'credits'             => (string) ($course->credits ?? '0'),
                    'classtime_classroom' => $course->classtime_classroom ?? $course->class_time ?? '',
                    'course_outline'      => $course->course_outline ?? $course->outline ?? '',
                    'course_url'          => $course->course_url ?? '',

                    // 從 course_power 對照表查出這門課具備的職能標籤
                    'powers'              => $powerMap[$classId] ?? [],
                    'abilities'           => $powerMap[$classId] ?? [],
                ];
            });

        } catch (\Exception $e) {
            Log::error('撈取課程資料庫失敗：' . $e->getMessage());
            // 發生錯誤時回傳空陣列，避免畫面崩潰
            $formattedCourses = collect([]);
        }

        // 將格式化好的課程資料丟給 AllCourses.vue 畫面
        return Inertia::render('AllCourses', [
            'initialCourses' => $formattedCourses
        ]);
    }
    // ==========================================
    // 🌟 新增：用學號查詢歷史紀錄的 API
    // ==========================================
    public function getHistory($student_id)
    {
        // 1. 去資料庫把這個學號的所有紀錄撈出來，最新的排在最上面
        $histories = DB::table('cpas_history')
            ->where('student_id', $student_id)
            ->orderBy('created_at', 'desc')
            ->get();

        // 🌟 新增：一口氣把 course_detail 裡的 class_id 跟 course_url 抓出來做成對照表
        $urlMap = DB::table('course_detail')->pluck('course_url', 'class_id')->toArray();

        // 2. 解碼 JSON 並把 URL 塞進課程資料裡
        $formattedHistories = $histories->map(function($record) use ($urlMap) {
            $recommendedCourses = json_decode($record->recommended_courses, true);

            // 🌟 尋找對應的 URL 並塞進去
            if (is_array($recommendedCourses)) {
                foreach ($recommendedCourses as &$course) {
                    $cid = $course['class_id'] ?? null;
                    // 如果對照表裡有這個 class_id 的網址就塞進去，沒有就給空字串
                    $course['course_url'] = $urlMap[$cid] ?? ''; 
                }
            }

            return [
                'id'                  => $record->id,
                'created_at'          => $record->created_at, 
                'raw_scores'          => json_decode($record->raw_scores, true),
                'core6_scores'        => json_decode($record->core6_scores, true),
                'recommended_courses' => $recommendedCourses, // 已經補滿 URL 的課程包！
            ];
        });

        return Inertia::render('HistoryList', [
            'student_id'     => $student_id,
            'historyRecords' => $formattedHistories
        ]);
    }
    // ==========================================
    // 🌟 新增：讀取特定測驗結果並顯示在 Result.vue
    // ==========================================
    public function showResult(Request $request, $student_id)
    {
        // 1. 從網址取得你要看的是哪一次的紀錄 (例如 ?record_id=5)
        $recordId = $request->query('record_id');

        // 2. 去資料庫找紀錄
        if ($recordId) {
            // 如果有指定 ID，就抓那一筆
            $history = DB::table('cpas_history')
                ->where('id', $recordId)
                ->where('student_id', $student_id)
                ->first();
        } else {
            // 如果沒指定 ID（例如使用者直接打網址），就給他看「最新」的一筆
            $history = DB::table('cpas_history')
                ->where('student_id', $student_id)
                ->orderBy('created_at', 'desc')
                ->first();
        }

        // 3. 如果找不到紀錄（可能學號打錯），就退回上一頁並顯示錯誤
        if (!$history) {
            return redirect()->route('history.show', ['student_id' => $student_id])
                ->withErrors(['msg' => '找不到該筆測驗紀錄，請重新確認。']);
        }

        // 4. 把保險箱裡面的 JSON 字串解碼回陣列
        $scores = json_decode($history->core6_scores, true);
        $recommendations = json_decode($history->recommended_courses, true);

        // 5. 原封不動地把資料丟給 Result.vue 渲染畫面！
        return Inertia::render('Result', [
            'userScores'      => $scores,
            'recommendations' => $recommendations,
        ]);
    }
}
