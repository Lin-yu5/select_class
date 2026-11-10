<template>
  <div class="bg-gray-100 text-on-surface min-h-screen relative">
    <canvas ref="canvasRef" class="fixed inset-0 w-full h-full z-[0] pointer-events-none"></canvas>

    <header class="fixed top-0 w-full z-50 bg-surface/90 backdrop-blur-sm flex justify-between items-center px-container-margin h-16 shadow-sm border-b border-outline-variant">
      <div class="flex items-center gap-4 relative">
        <span 
          class="material-symbols-outlined text-primary cursor-pointer hover:bg-surface-container-high p-2 rounded-full transition-colors"
          @click="isMenuOpen = !isMenuOpen"
        >menu</span>
        <h1 class="font-headline-lg text-headline-lg font-bold text-primary">東海通識課程推薦系統</h1>

        <div v-if="isMenuOpen" class="absolute top-14 left-0 mt-2 w-48 glass-card !bg-white/90 !backdrop-blur-md shadow-lg overflow-hidden z-50">
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
        <Link href="/index" class="text-on-surface font-label-lg px-4 py-2 hover:bg-surface-container-high rounded-lg no-underline text-primary font-bold">首頁</Link>
      </nav>
    </header>

    <div v-if="isMenuOpen" @click="isMenuOpen = false" class="fixed inset-0 z-40"></div>

    <main class="max-w-[1440px] mx-auto px-container-margin pb-xl pt-[100px] relative z-10">
      <div class="mb-xl flex flex-col sm:flex-row sm:justify-between sm:items-end gap-4">
        <div>
          <h2 class="font-display-lg text-display-lg mb-2">Analysis Results</h2>
          <p class="text-on-surface-variant font-body-lg">根據您的核心能力分析，我們為您規劃了專屬的職能成長路徑。</p>
        </div>
        
        <button 
          @click="handlePrint" 
          class="print-hidden flex items-center justify-center gap-2 px-6 py-3 bg-primary text-on-primary rounded-xl font-label-lg hover:bg-[#103489] shadow-md hover:shadow-lg transition-all active:scale-[0.98]"
        >
          <span class="material-symbols-outlined">print</span>
          匯出報告 (列印 / PDF)
        </button>
      </div>

      <section class="mb-2xl">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div
            v-for="(val, key) in competencyScores"
            :key="key"
            class="glass-card p-lg rounded-xl border-l-4 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300 bg-surface"
            :class="getBorderColor(key)"
          >
            <h4 class="font-headline-md mb-sm">{{ val.name }}</h4>
            <span class="text-display-lg leading-none">{{ val.score }}</span>
          </div>
        </div>
      </section>

      <section>
        <div class="flex items-center justify-between mb-lg">
          <h3 class="font-headline-lg text-headline-lg font-bold">推薦通識課程</h3>
        </div>

        <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 mb-4 print-hidden">
          <span class="font-bold text-on-surface-variant whitespace-nowrap">職能篩選：</span>
          <div class="flex items-center gap-3 flex-wrap">
            <button
              v-for="opt in strengthOptions"
              :key="opt.id"
              @click="activeStrength = opt.id"
              :class="[
                'px-4 py-1.5 rounded-full border transition-colors text-sm font-medium',
                activeStrength === opt.id
                  ? 'bg-primary text-on-primary border-primary shadow-sm'
                  : 'border-outline-variant text-on-surface hover:bg-primary/5'
              ]"
            >{{ opt.label }}</button>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 mb-lg print-hidden">
          <span class="font-bold text-on-surface-variant whitespace-nowrap">領域篩選：</span>
          <div class="flex items-center gap-3 flex-wrap">
            <button
              v-for="tab in filterTabs"
              :key="tab.id"
              @click="activeDepartment = tab.id"
              :class="[
                'px-4 py-1.5 rounded-full border transition-colors text-sm font-medium',
                activeDepartment === tab.id
                  ? 'bg-primary text-on-primary border-primary shadow-sm'
                  : 'border-outline-variant text-on-surface hover:bg-primary/5'
              ]"
            >{{ tab.label }}</button>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-lg">
          <div
            v-for="course in filteredCourses"
            :key="course.class_id"
            class="flex flex-col bg-surface border border-outline-variant rounded-xl overflow-hidden hover:shadow-lg transition-all p-lg"
          >
            <div class="flex flex-col gap-1 mb-2">
              <div class="flex flex-wrap gap-2 mb-2 items-center">
                <span class="text-[11px] bg-secondary/10 text-black px-2 py-0.5 rounded-md font-medium">
                  {{ course.department }}
                </span>
                <span class="text-[11px] bg-outline-variant/30 text-black px-2 py-0.5 rounded-md font-medium">
                  {{ course.credits }} 學分
                </span>
                
                <span 
                  v-if="course.relation_type === 'strong' || course.relation_type === 'both'" 
                  class="text-[11px] bg-blue-100 text-blue-800 border border-blue-200 px-2 py-0.5 rounded-md font-bold tracking-wide"
                >
                  強關係推薦
                </span>
                <span 
                  v-if="course.relation_type === 'weak' || course.relation_type === 'both'" 
                  class="text-[11px] bg-orange-100 text-orange-800 border border-orange-200 px-2 py-0.5 rounded-md font-bold tracking-wide"
                >
                  弱關係推薦
                </span>
              </div>
              <span class="font-headline-md">{{ course.class_name }}</span>
              <span v-if="course.class_name_en" class="text-sm text-black truncate">{{ course.class_name_en }}</span>
            </div>

            <div class="flex flex-col gap-1 text-black mb-md mt-2">
              <div v-if="course.teacher" class="flex items-center gap-sm">
                <span class="material-symbols-outlined text-[18px]">person</span>
                授課教師: {{ course.teacher }}
              </div>
              <div v-if="course.class_time" class="flex items-center gap-sm">
                <span class="material-symbols-outlined text-[18px]">schedule</span>
                時間教室: {{ course.class_time }}
              </div>
            </div>

            <div v-if="course.outline" class="text-body-sm text-gray-700 bg-surface-container-low p-md rounded-lg max-h-50 overflow-y-auto mb-md [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-track]:bg-gray-200 [&::-webkit-scrollbar-thumb]:bg-gray-400 [&::-webkit-scrollbar-thumb]:rounded-full" :title="course.outline">
              <strong>大綱摘要：</strong>{{ course.outline }}
            </div>

            <div class="mt-auto pt-md border-t border-outline-variant flex items-center justify-between">
              <p class="text-on-surface-variant font-body-md">
                <strong>適配度：</strong><span class="text-primary font-bold text-lg">{{ course.match_score }}%</span>
              </p>
              
              <a 
                v-if="course.course_url" 
                :href="course.course_url" 
                target="_blank" 
                class="text-sm text-primary flex items-center gap-0.5 hover:underline font-medium"
              >
                課程詳情 <span class="material-symbols-outlined text-sm">open_in_new</span>
              </a>
            </div>
          </div>
        </div>

        <div v-if="filteredCourses.length === 0" class="text-center py-xl text-on-surface-variant border-2 border-dashed border-outline-variant rounded-xl mt-4">
          目前沒有符合此篩選條件的推薦課程
        </div>
      </section>
    </main>
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

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { Link, router } from '@inertiajs/vue3';

// 🌟 1. 定義完整的 Recommendation 介面 (加入 relation_type)
interface Recommendation {
  class_id:      string;
  class_name:    string;
  class_name_en: string;
  department:    string;
  teacher:       string;
  credits:       string;
  class_time:    string;
  outline:       string;
  course_url:    string;
  match_score:   number;
  relation_type?: string;
}

const props = defineProps<{
  userScores:      number[];           
  recommendations: Recommendation[];
}>();

// 🌟 處理列印與匯出 PDF 的功能
const handlePrint = () => {
  window.print();
};

// 選單控制
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
    router.get(`/history/${searchStudentId.value.trim()}`);
    isSearchModalOpen.value = false; 
  } else {
    alert('請輸入學號喔！'); 
  }
};

// 🌟 2. 能力分數卡片映射
const competencyScores = computed(() => ({
  execution:    { name: '執行力', score: props.userScores[0] ?? 0 },
  leadership:   { name: '統御力', score: props.userScores[1] ?? 0 },
  affability:   { name: '親和力', score: props.userScores[2] ?? 0 },
  innovation:   { name: '開創力', score: props.userScores[3] ?? 0 },
  adaptability: { name: '應變力', score: props.userScores[4] ?? 0 },
  sensitivity:  { name: '敏感力', score: props.userScores[5] ?? 0 },
}));

const getBorderColor = (key: string) => {
  const colors: Record<string, string> = {
    execution:    'border-primary',
    leadership:   'border-secondary',
    affability:   'border-green-500',
    innovation:   'border-amber-500',
    adaptability: 'border-blue-500',
    sensitivity:  'border-red-500',
  };
  return colors[key] || 'border-gray-300';
};

// 🌟 3. 強弱項篩選器選項
const activeStrength = ref<string>('');
const strengthOptions = [
  { id: '', label: '全部顯示' },
  { id: 'strong', label: '強關係推薦' },
  { id: 'weak', label: '弱關係推薦' }
];

// 🌟 4. 領域篩選器
const activeDepartment = ref<string>('');
const filterTabs = computed(() => {
  const tabs = [{ id: '', label: '全部領域' }];
  const uniqueDeps = new Set(props.recommendations.map(c => c.department));
  uniqueDeps.forEach(dep => {
    if (dep && dep !== '未知系所') tabs.push({ id: dep, label: dep });
  });
  return tabs;
});

// 🌟 5. 雙重過濾邏輯 (直接用 relation_type 判斷)
const filteredCourses = computed(() => {
  let result = props.recommendations;

  // 過濾強弱關係 (如果課程是 both，則點選強或弱都會顯示)
  if (activeStrength.value === 'strong') {
    result = result.filter(c => c.relation_type === 'strong' || c.relation_type === 'both');
  } else if (activeStrength.value === 'weak') {
    result = result.filter(c => c.relation_type === 'weak' || c.relation_type === 'both');
  }

  // 過濾領域
  if (activeDepartment.value) {
    result = result.filter(c => c.department === activeDepartment.value);
  }

  return result;
});

// ==========================================
// 🌟 背景粒子邏輯
// ==========================================
const canvasRef = ref<HTMLCanvasElement | null>(null);
let animationFrameId: number;

onMounted (() => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  let width = window.innerWidth;
  let height = window.innerHeight;
  canvas.width = width;
  canvas.height = height;

  const particles: any[] = [];
  const particleCount = 70;
  const mouse = { x: -1000, y: -1000 };

  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 1.5,
      vy: (Math.random() - 0.5) * 1.5,
      radius: Math.random() * 2 + 1
    });
  }

  const handleMouseMove = (e: MouseEvent) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  };
  window.addEventListener('mousemove', handleMouseMove);

  const handleResize = () => {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
  };
  window.addEventListener('resize', handleResize);

  const animate = () => {
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = 'rgba(150, 150, 150, 0.4)';
    ctx.lineWidth = 1;

    particles.forEach((p, index) => {
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0 || p.x > width) p.vx *= -1;
      if (p.y < 0 || p.y > height) p.vy *= -1;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fill();

      for (let j = index + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        if (dist < 120) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(150, 150, 150, ${1 - dist / 120})`;
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }
      }

      const dxMouse = p.x - mouse.x;
      const dyMouse = p.y - mouse.y;
      const distMouse = Math.sqrt(dxMouse * dxMouse + dyMouse * dyMouse);
      
      if (distMouse < 150) {
        ctx.beginPath();
        ctx.strokeStyle = `rgba(100, 100, 255, ${0.8 - distMouse / 150})`; 
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(mouse.x, mouse.y);
        ctx.stroke();
      }
    });

    animationFrameId = requestAnimationFrame(animate);
  };

  animate();

  onBeforeUnmount(() => {
    window.removeEventListener('mousemove', handleMouseMove);
    window.removeEventListener('resize', handleResize);
    cancelAnimationFrame(animationFrameId);
  });
});
</script>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
}

/* 🌟 專屬列印與 PDF 匯出排版設定 */
@media print {
  /* 1. 隱藏不需要印出的元素：導覽列、背景粒子、篩選按鈕、列印按鈕本身 */
  header, canvas, .print-hidden {
    display: none !important;
  }
  
  /* 2. 重置背景色為純白，節省使用者的墨水並讓文字更清晰 */
  body, .bg-gray-100 {
    background-color: #ffffff !important;
  }
  
  /* 3. 移除原本為了導覽列留的頂部空間，讓 PDF 第一頁從最上面開始 */
  main {
    padding-top: 0 !important;
    margin-top: 0 !important;
  }

  /* 4. 關鍵魔法：讓卡片不會在一半被切斷（跨頁防護） */
  .glass-card, .bg-surface {
    page-break-inside: avoid !important;
    break-inside: avoid !important;
    border: 1px solid #e5e7eb !important; /* 確保列印時有淡淡的邊框區隔 */
    box-shadow: none !important; /* 移除陰影讓列印更乾淨 */
    margin-bottom: 16px !important;
  }
  
  /* 5. 強制瀏覽器印出背景顏色（例如我們設計的標籤底色） */
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
}
</style>