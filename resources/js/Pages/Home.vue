<script setup lang="ts">
import { ref } from 'vue';
// 🌟 1. 引入 Inertia 的核心工具
import { router, Link } from '@inertiajs/vue3';

// ==========================================
// 🌟 升級版：自訂結果查詢彈出視窗 (Modal)
// ==========================================
const isMenuOpen = ref(false);
const isSearchModalOpen = ref(false); 
const searchStudentId = ref('');          

const openSearchModal = () => {
  isMenuOpen.value = false; // 貼心設計：先把下拉選單收起來
  searchStudentId.value = 's12490016'; // 預設帶入的學號
  isSearchModalOpen.value = true;  // 打開彈出視窗
};

const closeSearchModal = () => {
  isSearchModalOpen.value = false;
  searchStudentId.value = ''; // 關閉時清空輸入框
};

const submitSearch = () => {
  if (searchStudentId.value && searchStudentId.value.trim()) {
    // 依照你原本的設定，跳轉到歷史紀錄頁面
    router.get(`/history/${searchStudentId.value.trim()}`);
    isSearchModalOpen.value = false; 
  } else {
    alert('請輸入學號喔！'); 
  }
};

// ==========================================
// 🌟 以下保留原本 Home.vue 的上傳與處理邏輯
// ==========================================
const isDragging = ref(false);
const selectedFile = ref<File | null>(null);
const uploadStatus = ref('');
const statusColor = ref('');
const uploadIcon = ref('');
const isUploading = ref(false);

const handleDrop = (e: DragEvent) => {
  isDragging.value = false;
  if (e.dataTransfer?.files.length) {
    processFile(e.dataTransfer.files[0]);
  }
};

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files?.length) {
    processFile(target.files[0]);
  }
};

const resetFile = () => {
  selectedFile.value = null;
  uploadStatus.value = '';
  statusColor.value = '';
  uploadIcon.value = '';
  isUploading.value = false;
};

const processFile = (file: File) => {
  if (file.type !== 'application/pdf') {
    alert('請上傳 PDF 格式的檔案喔！');
    resetFile();
    return;
  }

  selectedFile.value = file;
  uploadStatus.value = '解析與 AI 運算中...';
  statusColor.value = 'text-primary';
  uploadIcon.value = 'sync';
  isUploading.value = true;

  // 使用 Inertia 發送 POST 請求給 Laravel
  router.post('/cpas/upload', {
    pdf_file: file,
  }, {
    forceFormData: true, 
    onSuccess: () => {
      uploadStatus.value = '分析成功！準備呈現結果...';
      statusColor.value = 'text-green-600';
      uploadIcon.value = 'check_circle';
      isUploading.value = false;
    },
    onError: (errors) => {
      console.error('上傳失敗:', errors);
      uploadStatus.value = '上傳或解析失敗';
      statusColor.value = 'text-red-600';
      uploadIcon.value = 'error';
      isUploading.value = false;
      alert('發生錯誤，請確認您的 PDF 格式正確，或查看終端機錯誤訊息。');
    }
  });
};
</script>

<template>
<div class="bg-background text-on-surface min-h-screen relative">
  <header class="fixed top-0 w-full z-50 !bg-white/60 backdrop-blur-sm flex justify-between items-center px-container-margin h-16 shadow-sm border-b border-outline-variant">
      <div class="flex items-center gap-4 relative">
        <span 
          class="material-symbols-outlined text-primary cursor-pointer hover:bg-surface-container-high p-2 rounded-full transition-colors"
          @click="isMenuOpen = !isMenuOpen"
        >menu</span>
        <h1 class="font-headline-lg text-headline-lg font-bold text-primary">東海通識課程推薦系統</h1>

        <div v-if="isMenuOpen" class="absolute top-14 left-0 mt-2 w-48 glass-card !bg-white/60 !backdrop-blur-md shadow-lg overflow-hidden z-50">
          <Link href="/index" class="w-full flex items-center gap-3 px-4 py-3 text-on-surface hover:bg-surface-container-high hover:text-primary transition-colors no-underline">
            <span class="material-symbols-outlined text-[20px]">home</span>首頁
          </Link>
          <Link href="/cpas/enter" class="w-full flex items-center gap-3 px-4 py-3 text-on-surface hover:bg-surface-container-high hover:text-primary transition-colors no-underline">
            <span class="material-symbols-outlined text-[20px]">edit_note</span>分數輸入
          </Link>
          
          <button type="button" @click="openSearchModal" class="w-full flex items-center gap-3 px-4 py-3 text-on-surface hover:bg-surface-container-high hover:text-primary transition-colors text-left focus:outline-none">
            <span class="material-symbols-outlined text-[20px]">search_insights</span>歷史結果查詢
          </button>
          
          <Link href="/cpas/courses" class="w-full flex items-center gap-3 px-4 py-3 text-on-surface hover:bg-surface-container-high hover:text-primary transition-colors no-underline">
            <span class="material-symbols-outlined text-[20px]">library_books</span>瀏覽所有課程
          </Link>
        </div>
      </div>

      <nav class="hidden md:flex items-center gap-6">
        <Link href="/index" class="text-primary font-label-lg px-4 py-2 bg-primary-container/10 rounded-lg no-underline">首頁</Link>
        <button type="button" @click="openSearchModal" class="text-on-surface-variant font-label-lg px-4 py-2 hover:bg-surface-container-high rounded-lg transition-colors focus:outline-none">歷史結果查詢</button>
        <Link href="/cpas/courses" class="text-on-surface-variant font-label-lg px-4 py-2 hover:bg-surface-container-high rounded-lg no-underline transition-colors">瀏覽所有課程</Link>
      </nav>
      <div class="flex items-center gap-2"></div>
  </header>
  
  <div v-if="isMenuOpen" @click="isMenuOpen = false" class="fixed inset-0 z-40"></div>

  <main class="pt-24 max-w-6xl mx-auto px-container-margin min-h-screen pb-20 relative z-10">
    <section class="mt-xl rounded-2xl overflow-hidden relative h-[320px] flex items-center mb-xl">
      <img
        alt="Explore potential"
        class="absolute inset-0 w-full h-full object-cover -scale-x-100"
        src="https://lh3.googleusercontent.com/aida-public/AB6AXuBWLDFmAwJnUvAM4P_M_DVKabEMD-JGsoJXj6UjRCP6vu6HmK79CR4xe1UELgIcIMEJipyr3ny0EXQIKsFfKS-lxUAylx8qOHy6Jh5B_6zhOyWyrG9noWOZxwDVcB9Pfmtzb9TirP1UOdSQFOM96Ixb1zpUEXLk02M96_5CFGnU82nX8E0YuWK686vA8Jc3ugWSpT4S1PxWTYU4_8-B2aQJK77TbZoihOgfE4Oo885tvNp2wPaofUpz98lZ0jYlAaTeLi1y6Sz8VX1-"
      />
      <div class="absolute inset-0 bg-gradient-to-r from-primary/80 to-transparent flex flex-col justify-center pl-16 md:pl-24 pr-8">
        <h2 class="text-white font-bold !text-5xl mb-4 max-w-xl tracking-wide">
          探索你的職涯潛能
        </h2>
        <p class="text-white/90 font-medium !text-xl max-w-2xl leading-relaxed">
          透過 CPAS 人格特性分析，<br>
          為您精準匹配最適合的學習路徑，<br>
          開啟智慧教育的新篇章。
        </p>
      </div>
    </section>

    <div class="text-center mb-xl">
      <h3 class="font-headline-lg text-headline-lg text-on-surface mb-2">請輸入 CPAS 12 項人格特性分數</h3>
      <p class="font-body-md text-body-md text-on-surface-variant">選擇最適合您的輸入方式，開始您的精準推薦之旅</p>
    </div>

    <div class="grid grid-cols-2 gap-lg mb-2xl">
      <label
        class="group cursor-pointer bg-surface-container-lowest p-xl rounded-xl card-shadow border-2 border-dashed border-outline-variant hover:border-primary hover:bg-primary/5 transition-all duration-300 flex flex-col items-center text-center relative"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        :class="{ 'border-primary bg-primary/5': isDragging }"
      >
        <input accept=".pdf" class="hidden" type="file" @change="handleFileSelect" />

        <div v-if="!selectedFile" class="upload-placeholder flex flex-col items-center">
          <div class="w-24 h-24 bg-primary-container/10 rounded-full flex items-center justify-center mb-lg group-hover:scale-110 transition-transform duration-300">
            <span class="material-symbols-outlined text-[48px] text-primary">picture_as_pdf</span>
          </div>
          <h4 class="font-headline-md text-headline-md text-on-surface mb-md">上傳 CPAS 測驗結果.PDF</h4>
          <p class="font-body-md text-body-md text-gray-2000 text-on-surface-variant mb-lg">點擊此處或拖曳您的報告 PDF 檔案至此——系統將自動解析數據。</p>
        </div>

        <div v-else class="preview-container w-full flex flex-col items-center mb-lg">
          <div class="w-full bg-surface-container-low p-md rounded-xl border border-outline-variant flex items-center gap-md relative">
            <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
              <span class="material-symbols-outlined text-primary">description</span>
            </div>
            <div class="flex flex-col items-start">
              <span class="font-label-lg text-on-surface truncate max-w-[180px]">{{ selectedFile.name }}</span>
              <span class="flex items-center gap-1 text-[12px] font-medium" :class="statusColor">
                <span v-if="uploadIcon" class="material-symbols-outlined text-sm" :class="{ 'animate-spin': isUploading }">{{ uploadIcon }}</span>
                {{ uploadStatus }}
              </span>
            </div>
            <button type="button" @click.prevent="resetFile" class="ml-auto p-2 text-on-surface-variant hover:text-error hover:bg-error-container/10 rounded-full transition-colors">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
        </div>

        <div class="action-button w-full h-[56px] bg-primary text-on-primary rounded-lg font-label-lg flex items-center justify-center gap-2 hover:bg-primary-container transition-colors active:scale-[0.98]">
          <span class="material-symbols-outlined">upload_file</span>
          <span class="button-text">{{ selectedFile ? '重新上傳檔案' : '選擇並上傳檔案' }}</span>
        </div>
      </label>

      <Link
        href="/cpas/enter"
        class="group cursor-pointer bg-surface-container-lowest p-xl rounded-xl card-shadow border border-outline-variant hover:border-primary transition-all duration-300 flex flex-col items-center text-center no-underline"
      >
        <div class="w-24 h-24 bg-secondary-container/20 rounded-full flex items-center justify-center mb-lg group-hover:scale-110 transition-transform duration-300">
          <span class="material-symbols-outlined text-[48px] text-secondary">edit_note</span>
        </div>
        <h4 class="font-headline-md text-headline-md text-on-surface mb-md">CPAS 分數</h4>
        <p class="font-body-md text-body-md text-on-surface-variant mb-lg">如果您已有分數結果，可透過手動輸入介面逐項填入 12 項人格特性指標，進行深度適配分析。</p>
        <button type="button" class="w-full h-[56px] border-2 border-primary text-primary bg-transparent rounded-lg font-label-lg flex items-center justify-center gap-2 hover:bg-primary/5 transition-colors active:scale-[0.98]">
          <span class="material-symbols-outlined">stylus</span>
          開始手動輸入
        </button>
      </Link>
    </div>

    <section class="bg-surface-container-low py-12 px-8 rounded-2xl mb-2xl">
      <h3 class="font-bold !text-4xl text-on-surface mb-16 text-center tracking-wide">為什麼需要 CPAS？</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-8 px-4">
        <div class="flex flex-col items-center text-center">
          <span class="material-symbols-outlined text-primary !text-[64px] mb-6">insights</span>
          <h5 class="font-bold !text-2xl mb-4 text-on-surface">精準性格定位</h5>
          <p class="font-medium !text-lg text-gray-800 leading-relaxed">
            透視 12 項職業性格指標，<br>
            了解自己在團隊協作、抗壓性 <br>
            及邏輯思維的真實表現。
          </p>
        </div>

        <div class="flex flex-col items-center text-center">
          <span class="material-symbols-outlined text-secondary !text-[64px] mb-6">school</span>
          <h5 class="font-bold !text-2xl mb-4 text-on-surface">智慧課程推薦</h5>
          <p class="font-medium !text-lg text-gray-800 leading-relaxed">
            基於演算模型，<br>
            為您推薦補足短板 <br>
            或強化優勢的專業課程， <br>
            提升學習投資報酬率。
          </p>
        </div>

        <div class="flex flex-col items-center text-center">
          <span class="material-symbols-outlined text-tertiary !text-[64px] mb-6">trending_up</span>
          <h5 class="font-bold !text-2xl mb-4 text-on-surface">職涯路徑優化</h5>
          <p class="font-medium !text-lg text-gray-800 leading-relaxed">
            結合當前產業趨勢， <br>
            將個人特性與職位需求接軌， <br>
            引導您邁向最具潛力的職涯高峰。
          </p>
        </div>
      </div>
    </section>
  </main>

  <nav class="md:hidden fixed bottom-0 left-0 w-full flex justify-around items-center px-4 py-2 pb-safe bg-surface-container-lowest border-t border-outline-variant shadow-[0px_8px_24px_rgba(0,0,0,0.08)] z-50">
    <Link href="/cpas/enter" class="flex flex-col items-center justify-center text-on-surface-variant py-1 active:scale-90 transition-transform duration-150 no-underline">
      <span class="material-symbols-outlined">edit_note</span>
      <span class="font-label-sm text-label-sm">分數輸入</span>
    </Link>
    <div @click="openSearchModal" class="flex flex-col items-center justify-center text-on-surface-variant py-1 active:scale-90 transition-transform duration-150 cursor-pointer">
      <span class="material-symbols-outlined">search_insights</span>
      <span class="font-label-sm text-label-sm">結果查詢</span>
    </div>
    <div class="flex flex-col items-center justify-center text-on-surface-variant py-1 active:scale-90 transition-transform duration-150">
      <span class="material-symbols-outlined">person</span>
      <span class="font-label-sm text-label-sm">會員中心</span>
    </div>
  </nav>

  <div 
    v-if="isSearchModalOpen" 
    class="fixed inset-0 z-[100] flex items-center justify-center"
  >
    <div 
      class="absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity"
      @click="closeSearchModal"
    ></div>

    <div class="bg-surface w-full max-w-md rounded-2xl p-8 shadow-2xl border border-outline-variant relative z-10 mx-4 transform transition-all">
      
      <div class="flex justify-between items-center mb-4">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-primary text-3xl">search_insights</span>
          <h3 class="text-2xl font-bold text-primary">歷史紀錄查詢</h3>
        </div>
        <button @click="closeSearchModal" class="text-on-surface-variant hover:text-error hover:bg-error-container/10 p-1 rounded-full transition-colors">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <p class="text-base text-on-surface-variant mb-6">
        請輸入您的學號，系統將為您調出專屬的 CPAS 職能分析與課程推薦歷史紀錄。
      </p>

      <div class="mb-8">
        <label class="block text-sm font-medium text-on-surface mb-2">學號</label>
        <input 
          type="text" 
          v-model="searchStudentId" 
          @keyup.enter="submitSearch" 
          class="w-full px-4 py-3 rounded-xl border border-outline-variant focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all bg-surface-container-lowest text-lg" 
          placeholder="例如：s12490016"
          autofocus
        >
      </div>

      <div class="flex justify-end gap-3">
        <button 
          @click="closeSearchModal" 
          class="px-6 py-2.5 rounded-xl font-label-lg text-on-surface-variant hover:bg-surface-container-high transition-colors"
        >
          取消
        </button>
        <button 
          @click="submitSearch" 
          class="px-6 py-2.5 rounded-xl font-label-lg bg-primary text-on-primary hover:bg-primary-dark shadow-md hover:shadow-lg transition-all flex items-center gap-2"
        >
          <span>開始查詢</span>
          <span class="material-symbols-outlined text-sm">arrow_forward</span>
        </button>
      </div>
    </div>
  </div>

</div>
</template>