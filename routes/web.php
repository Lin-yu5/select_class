<?php

use Illuminate\Support\Facades\Route;
use Inertia\Inertia;
use App\Http\Controllers\CpasResultController;

// 1. 進入首頁（打開 resources/js/Pages/Home.vue）
Route::get('/index', function () {
    return Inertia::render('Home');
});

// 2. 進入手動輸入分數頁面（打開 resources/js/Pages/EnterScore.vue）
Route::get('/cpas/enter', function () {
    return Inertia::render('EnterScore'); // 建議檔名用英文，避開中文
})->name('cpas.enter');

Route::get('/cpas/result', function () {
    return Inertia::render('Result');
})->name('cpas.result');

Route::get('/cpas/courses', [CpasResultController::class, 'allCourses'])->name('courses.all');

Route::get('/cpas/result/{student_id}', [CpasResultController::class, 'showResult'])->name('cpas.result');

// 3. POST 表單送出的路由（這些不出畫面，只處理資料，由 Controller 接手）
// PDF 上傳後端處理
Route::post('/cpas/upload', [CpasResultController::class, 'processPdf'])->name('cpas.upload');
// 手動輸入分數後端處理
Route::post('/cpas/manual', [CpasResultController::class, 'processManual'])->name('cpas.manual');

Route::get('/history/{student_id}', [\App\Http\Controllers\CpasResultController::class, 'getHistory'])->name('history.show');