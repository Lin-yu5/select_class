<template>
  <div class="bg-background text-on-surface min-h-screen relative">
    <canvas ref="canvasRef" class="fixed inset-0 w-full h-full z-[0] pointer-events-none"></canvas>
    
    <header class="fixed top-0 w-full z-50 bg-surface/90 backdrop-blur-sm flex justify-between items-center px-container-margin h-16 shadow-sm border-b border-outline-variant">
      <div class="flex items-center gap-4 relative">
        <span 
          class="material-symbols-outlined text-primary cursor-pointer hover:bg-surface-container-high p-2 rounded-full transition-colors"
          @click="isMenuOpen = !isMenuOpen"
        >menu</span>
        <h1 class="font-headline-lg text-headline-lg font-bold text-primary">東海通識課程推薦系統</h1>

        <div v-if="isMenuOpen" class="absolute top-14 left-0 mt-2 w-48 glass-card !bg-white/90 !backdrop-blur-xl shadow-lg overflow-hidden z-50">
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

    <main style="padding-top: 100px;" class="max-w-7xl mx-auto px-container-margin min-h-screen pb-20 relative z-10">
      <section class="mb-6">
        <div class="relative max-w-xl">
          <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-xl">search</span>
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜尋課名、教師或課程介紹..."
            class="w-full pl-10 pr-10 py-3 rounded-full border-2 border-outline-variant bg-surface text-on-surface focus:outline-none focus:border-primary transition-colors"
          />
          <button
            v-if="searchKeyword"
            @click="searchKeyword = ''"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-primary"
          >
            <span class="material-symbols-outlined text-xl">close</span>
          </button>
        </div>
      </section>

      <section class="mb-6">
        <h3 class="text-lg font-semibold text-on-surface mb-4">依領域篩選課程</h3>
        <div class="flex flex-wrap gap-3">
          <button
            v-for="domain in domainTabs"
            :key="domain.id"
            @click="toggleDomain(domain.id)"
            :class="[
              'px-5 py-2 rounded-full text-sm font-semibold border-2 transition-all duration-200 cursor-pointer',
              selectedDomains.includes(domain.id)
                ? getDomainColor(domain.id, 'btn')
                : 'bg-surface text-on-surface-variant border-outline-variant hover:border-primary hover:text-primary'
            ]"
          >
            {{ domain.label }}
          </button>
        </div>
      </section>

      <section class="mb-8">
        <div class="flex items-center gap-2 mb-4">
          <h3 class="text-lg font-semibold text-on-surface">依職能篩選課程</h3>
          
          <!--  提示小圖示 (Tooltip) 區塊 -->
          <div class="relative group flex items-center cursor-help">
            <span class="material-symbols-outlined text-on-surface-variant text-[20px] hover:text-primary transition-colors">info</span>
            
            <!-- 滑鼠懸浮時顯示的黑色提示框 -->
            <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 bg-gray-800 text-white rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 pointer-events-none text-20 font-medium leading-relaxed tracking-wide">
              以 CPAS 測驗的六大職能為基準，再透過專家問卷制定權重矩陣，接著計算出各課程的職能績效分數，最後運用 K-means 分群演算法，將通識課程精準分類到這六大能力指標中。
              <!-- 提示框下方的小三角形 -->
              <div class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-gray-800 rotate-45"></div>
            </div>
          </div>
        </div>
        <div class="flex flex-wrap gap-3">
          <button
            v-for="power in powerTags"
            :key="power.key"
            @click="togglePower(power.key)"
            :class="[
              'px-5 py-2 rounded-full text-sm font-semibold border-2 transition-all duration-200 cursor-pointer',
              selectedPowers.includes(power.key)
                ? 'bg-primary text-on-primary border-primary shadow-md scale-105'
                : 'bg-surface text-on-surface-variant border-outline-variant hover:border-primary hover:text-primary'
            ]"
          >
            {{ power.label }}
          </button>
          <button
            @click="toggleUnclassified"
            :class="[
              'px-5 py-2 rounded-full text-sm font-semibold border-2 transition-all duration-200 cursor-pointer',
              showUnclassifiedOnly
                ? 'bg-primary text-on-primary border-primary shadow-md scale-105'
                : 'bg-surface text-on-surface-variant border-outline-variant hover:border-primary hover:text-primary'
            ]"
          >
            未分類職能
          </button>
          <button
            v-if="selectedPowers.length > 0 || selectedDomains.length > 0 || showUnclassifiedOnly || searchKeyword"
            @click="selectedPowers = []; selectedDomains = []; showUnclassifiedOnly = false; searchKeyword = ''"
            class="px-5 py-2 rounded-full text-sm font-semibold border-2 border-red-300 text-red-500 hover:bg-red-50 transition-all duration-200 cursor-pointer"
          >
            ✕ 清除篩選
          </button>
        </div>
        <p class="mt-3 text-sm text-on-surface-variant text-gray-800">
          <span v-if="selectedPowers.length === 0 && selectedDomains.length === 0 && !showUnclassifiedOnly && !searchKeyword">目前顯示所有課程（共 {{ courses.length }} 門）</span>
          <span v-else>篩選結果：共 {{ filteredCourses.length }} 門課程</span>
        </p>
      </section>

      <div v-if="filteredCourses.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="course in filteredCourses" :key="course.class_id" 
            :class="[
            'rounded-xl p-6 shadow-sm border transition-all duration-300 flex flex-col',
            getDomainColor(course.department, 'card')
          ]">
          <div class="mb-4">
            <h3 class="text-xl font-bold text-on-surface mb-1">{{ course.class_name_chinese }}</h3>
            <p class="text-sm text-gray-600 line-clamp-1">{{ course.class_name_english || '無英文名稱' }}</p>
          </div>
          
          <div class="text-sm text-gray-700 font-medium mb-4 space-y-2 flex-grow">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-base">person</span>
              <span>{{ course.teacher_name || '未指定授課教師' }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-base">domain</span>
              <span>{{ course.department || '未指定開課單位' }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-base">schedule</span>
              <span>{{ course.classtime_classroom || '未定' }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-base">school</span>
              <span>學分：{{ course.credits || '未知' }}</span>
            </div>
          </div>

          <div v-if="course.powers && course.powers.length > 0" class="mb-3">
            <span class="px-3 py-1 bg-primary-container text-on-primary-container text-xs rounded-full font-medium">
              {{ course.powers.map(p => powerLabelMap[p] || p).join(' / ') }}
            </span>
          </div>

          <div class="mt-auto border-t border-outline-variant pt-4">
            <h4 class="text-sm font-semibold text-on-surface mb-2">課程介紹</h4>
            <div class="text-sm text-gray-700 leading-relaxed">
              <div v-if="course.course_outline" class="max-h-32 overflow-y-auto [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-gray-300 [&::-webkit-scrollbar-thumb]:rounded-full pr-2">
                <p>{{ course.course_outline }}</p>
              </div>
              <p v-else class="italic">無相關內容</p>
            </div>

            <div v-if="course.course_url" class="mt-3 text-right">
              <a
                :href="course.course_url"
                target="_blank"
                class="text-sm text-primary inline-flex items-center gap-0.5 hover:underline"
              >
                課程詳情 <span class="material-symbols-outlined text-sm">open_in_new</span>
              </a>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-20 text-on-surface-variant">
        <span class="material-symbols-outlined text-4xl mb-2">search_off</span>
        <p>目前沒有符合此篩選條件的課程。</p>
      </div>
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
            <h3 class="text-2xl font-bold text-primary">結果查詢</h3>
          </div>
          <button @click="closeSearchModal" class="text-on-surface-variant hover:text-error hover:bg-error-container/10 p-1 rounded-full transition-colors">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <p class="text-base text-on-surface-variant mb-6">
          請輸入您的學號，系統將為您調出專屬的 CPAS 職能分析與課程推薦紀錄。
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
import { Link, router } from '@inertiajs/vue3'; // 🌟 記得引入 router

interface Course {
  class_id: number;
  class_name_chinese: string;
  class_name_english: string;
  teacher_name: string;
  department: string;
  credits: string;
  classtime_classroom: string;
  course_outline: string;
  course_url: string;
  abilities: string[];
  powers: string[];
}

const props = defineProps<{
  initialCourses: Course[];
}>();

const powerLabelMap: Record<string, string> = {
  'Execution': '執行力',
  'Leadership': '領導力',
  'Affability': '親和力',
  'Innovation': '開創力',
  'Adaptability': '應變力',
  'Sensitivity': '敏銳力',
};

const powerTags = [
  { key: 'Execution', label: '執行力' },
  { key: 'Leadership', label: '領導力' },
  { key: 'Affability', label: '親和力' },
  { key: 'Innovation', label: '開創力' },
  { key: 'Adaptability', label: '應變力' },
  { key: 'Sensitivity', label: '敏銳力' },
];

const isMenuOpen = ref(false);

// ==========================================
// 🌟 升級版：自訂結果查詢彈出視窗 (Modal)
// ==========================================
const isSearchModalOpen = ref(false); 
const searchStudentId = ref('');          

const openSearchModal = () => {
  isMenuOpen.value = false; 
  searchStudentId.value = 's12490016'; 
  isSearchModalOpen.value = true;  
};

const closeSearchModal = () => {
  isSearchModalOpen.value = false;
  searchStudentId.value = ''; 
};

const submitSearch = () => {
  if (searchStudentId.value && searchStudentId.value.trim()) {
   router.get(`/history/${searchStudentId.value.trim()}`);
    isSearchModalOpen.value = false; 
  } else {
    alert('請輸入學號喔！'); 
  }
};

// 課程與搜尋邏輯
const courses = ref<Course[]>(props.initialCourses || []);
const selectedPowers = ref<string[]>([]);
const showUnclassifiedOnly = ref(false);
const searchKeyword = ref('');
const selectedDomains = ref<string[]>([]);
const domainTabs = [
  { id: '人文領域', label: '人文領域' },
  { id: '自然領域', label: '自然領域' },
  { id: '社會領域', label: '社會領域' },
];

const getDomainColor = (domain: string, type: 'btn' | 'card') => {
  const colors: Record<string, Record<'btn' | 'card', string>> = {
    '人文領域': {
      btn: 'bg-orange-100 text-orange-800 border-orange-300 shadow-md scale-105',
      card: 'bg-orange-50 border-orange-200 hover:border-orange-400 hover:shadow-md'
    },
    '自然領域': {
      btn: 'bg-emerald-100 text-emerald-800 border-emerald-300 shadow-md scale-105',
      card: 'bg-emerald-50 border-emerald-200 hover:border-emerald-400 hover:shadow-md'
    },
    '社會領域': {
      btn: 'bg-blue-100 text-blue-800 border-blue-300 shadow-md scale-105',
      card: 'bg-blue-50 border-blue-200 hover:border-blue-400 hover:shadow-md'
    }
  };
  
  // 如果遇到未知的領域，就使用原本的預設樣式
  const defaultColors = {
    btn: 'bg-primary text-on-primary border-primary shadow-md scale-105',
    card: 'bg-surface-container-lowest border-outline-variant hover:border-primary hover:shadow-md'
  };

  return colors[domain]?.[type] || defaultColors[type];
};

const toggleDomain = (domain: string) => {
  const idx = selectedDomains.value.indexOf(domain);
  if (idx === -1) {
    selectedDomains.value.push(domain);
  } else {
    selectedDomains.value.splice(idx, 1);
  }
};

const toggleUnclassified = () => {
  showUnclassifiedOnly.value = !showUnclassifiedOnly.value;
  if (showUnclassifiedOnly.value) {
    selectedPowers.value = [];
  }
};

const togglePower = (power: string) => {
  showUnclassifiedOnly.value = false; 
  const idx = selectedPowers.value.indexOf(power);
  if (idx === -1) {
    selectedPowers.value.push(power);
  } else {
    selectedPowers.value.splice(idx, 1);
  }
};

const filteredCourses = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase();

  return courses.value.filter(course => {
    const matchDomain = selectedDomains.value.length === 0 ||
      selectedDomains.value.includes(course.department);

    const matchSearch = keyword === '' || [
      course.class_name_chinese,
      course.class_name_english,
      course.teacher_name,
      course.course_outline,
    ].some(field => (field || '').toLowerCase().includes(keyword));

    if (showUnclassifiedOnly.value) {
      const isUnclassified = !course.powers || course.powers.length === 0;
      return matchDomain && matchSearch && isUnclassified;
    }

    const matchPower = selectedPowers.value.length === 0 ||
      selectedPowers.value.every(p => course.powers && course.powers.includes(p));

    return matchDomain && matchSearch && matchPower;
  });
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
  const particleCount = 50; 
  const mouse = { x: -1000, y: -1000 };

  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * width,  
      y: Math.random() * height, 
      vx: (Math.random() - 0.5) * 3.0,
      vy: (Math.random() - 0.5) * 3.0,
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
        
        if (dist < 150) {
          ctx.beginPath();
          // ⚠️ 已經幫你修正這裡的透明度計算公式
          ctx.strokeStyle = `rgba(150, 150, 150, ${1 - dist / 150})`;
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