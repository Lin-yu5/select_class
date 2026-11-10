<template>
  <div class="bg-background text-on-surface min-h-screen">
    <canvas ref="canvasRef" class="fixed inset-0 w-full h-full z-[0] pointer-events-none"></canvas>
    
  <header class="fixed top-0 w-full z-50 bg-surface/90 backdrop-blur-sm flex justify-between items-center px-container-margin h-16 shadow-sm border-b border-outline-variant">
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
            <span class="material-symbols-outlined text-[20px]">search_insights</span>結果查詢
          </button>
          
          <Link href="/cpas/courses" class="w-full flex items-center gap-3 px-4 py-3 text-on-surface hover:bg-surface-container-high hover:text-primary transition-colors no-underline">
            <span class="material-symbols-outlined text-[20px]">library_books</span>瀏覽所有課程
          </Link>
        </div>
      </div>

      <nav class="hidden md:flex items-center gap-6">
        <Link href="/index" class="text-primary font-label-lg px-4 py-2 bg-primary-container/10 rounded-lg no-underline">首頁</Link>
        <button type="button" @click="openSearchModal" class="text-on-surface-variant font-label-lg px-4 py-2 hover:bg-surface-container-high rounded-lg transition-colors focus:outline-none">結果查詢</button>
        <Link href="/cpas/courses" class="text-on-surface-variant font-label-lg px-4 py-2 hover:bg-surface-container-high rounded-lg no-underline transition-colors">瀏覽所有課程</Link>
      </nav>
      <div class="flex items-center gap-2"></div>
  </header>
    
    <div v-if="isMenuOpen" @click="isMenuOpen = false" class="fixed inset-0 z-40"></div>

    <main class="pt-24 pb-32 px-md max-w-6xl mx-auto relative z-10">
      <section class="mb-12 text-center md:text-left">
        <h2 class="text-3xl font-bold text-on-background mb-4">請輸入 CPAS 12項人格特性分數</h2>
        <p class="text-base text-on-surface-variant">請根據您的測驗結果，填寫對應的 1-10 分評分，我們將為您量身打造學習路徑。</p>
      </section>

      <div class="mb-8 bg-surface-container-lowest rounded-xl p-md shadow-md border border-outline-variant">
        <h3 class="text-lg font-semibold text-on-surface mb-4">請輸入基本資料：</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-on-surface-variant mb-1">學號 <span class="text-red-500">*</span></label>
            <input v-model="studentId" type="text" class="w-full px-4 py-2 rounded-lg border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary outline-none bg-surface" placeholder="例如：s12490016">
          </div>
          <div>
            <label class="block text-sm font-medium text-on-surface-variant mb-1">姓名</label>
            <input v-model="studentName" type="text" class="w-full px-4 py-2 rounded-lg border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary outline-none bg-surface" placeholder="例如：林軒宇">
          </div>
          <div>
            <label class="block text-sm font-medium text-on-surface-variant mb-1">系所</label>
            <input v-model="studentDepartment" type="text" class="w-full px-4 py-2 rounded-lg border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary outline-none bg-surface" placeholder="例如：資訊管理學系">
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-lg">
        <div v-for="(trait, index) in traits" :key="index" class="bg-surface-container-lowest rounded-xl p-md shadow-md border border-outline-variant hover:border-primary hover:shadow-lg transition-all duration-300">
          <div class="flex justify-between items-center mb-md">
            <h3 class="text-lg font-semibold text-on-surface">{{ trait.name }}</h3>
            <span class="text-xs font-medium text-on-surface-variant bg-surface-container px-3 py-1 rounded-full">
              {{ scores[index] > 0 ? scores[index] : '未評' }} / 10
            </span>
          </div>
          
          <div class="space-y-2">
            <div class="flex justify-between gap-1">
              <button 
                v-for="n in 5" :key="n"
                @click="scores[index] = n"
                :class="['w-10 h-10 flex items-center justify-center rounded-lg border text-sm font-medium transition-all active:scale-90', 
                         scores[index] === n ? 'bg-primary text-on-primary border-primary hover:bg-primary-dark' : 'border-outline-variant text-on-surface-variant hover:bg-surface-container-high bg-surface']"
              >{{ n }}</button>
            </div>
            <div class="flex justify-between gap-1">
              <button 
                v-for="n in 5" :key="n+5"
                @click="scores[index] = n+5"
                :class="['w-10 h-10 flex items-center justify-center rounded-lg border text-sm font-medium transition-all active:scale-90', 
                         scores[index] === n+5 ? 'bg-primary text-on-primary border-primary hover:bg-primary-dark' : 'border-outline-variant text-on-surface-variant hover:bg-surface-container-high bg-surface']"
              >{{ n + 5 }}</button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <button 
      @click="submitScores"
      :disabled="!isAllFilled"
      :class="['fixed bottom-8 right-8 bg-primary text-on-primary text-sm font-semibold px-8 py-3 rounded-full flex items-center gap-2 shadow-lg transition-all duration-200 z-50', 
               { 'opacity-50 cursor-not-allowed': !isAllFilled, 'hover:bg-primary-dark': isAllFilled }]"
    >
      <span>開始分析</span>
      <span class="material-symbols-outlined">chevron_right</span>
    </button>
  </div>

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
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount  } from 'vue';
import { useForm } from '@inertiajs/vue3';
import { router,Link } from '@inertiajs/vue3';

const isMenuOpen = ref(false);
const isSearchModalOpen = ref(false); 
const searchStudentId = ref('');

const props = defineProps<{
  parsedScores?: number[];
}>();

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

const studentId = ref('');
const studentName = ref('');       
const studentDepartment = ref('');
const traits = [
  { name: "行動性", key: "action" }, { name: "持續性", key: "persistence" },
  { name: "指導性", key: "leadership" }, { name: "挑戰性", key: "challenge" },
  { name: "共感性", key: "empathy" }, { name: "情緒安定性", key: "stability" },
  { name: "獨立自主性", key: "independence" }, { name: "革新性", key: "innovation" },
  { name: "思考性", key: "thinking" }, { name: "柔軟性", key: "flexibility" },
  { name: "感受性", key: "sensitivity" }, { name: "慎重性", key: "caution" }
];

const scores = reactive<number[]>(
  props.parsedScores && props.parsedScores.length === 12
    ? [...props.parsedScores] 
    : new Array(12).fill(0)
);

// Vue computed 自動判斷是否全填完
const isAllFilled = computed(() => scores.every(s => s > 0));

const submitScores = () => {
  if (!studentId.value.trim()) {
    alert('請先填寫學號！');
    return;
  }

  const form = useForm({
    student_id: studentId.value.trim(),
    student_name: studentName.value.trim(),             
    student_department: studentDepartment.value.trim(),
    scores: [...scores],
  });

  form.post('/cpas/manual', {
    onError: (errors) => {
      alert(errors.msg ?? '送出失敗，請確認分數是否都已填寫。');
    },
  });
};
// ==========================================
// 🌟 背景粒子邏輯
// ==========================================
const canvasRef = ref<HTMLCanvasElement | null>(null);
let animationFrameId: number;

onMounted (() => {
  // 1. 初始化畫布 (Canvas)
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // 設定畫布大小為目前視窗的寬高
  let width = window.innerWidth;
  let height = window.innerHeight;
  canvas.width = width;
  canvas.height = height;

  const particles: any[] = [];
  
  // ⚙️ 【可調整】粒子的總數量
  // 數值越大：畫面越擁擠、線條越密集（但太高可能會讓網頁變卡）
  // 數值越小：畫面越乾淨清爽
  const particleCount = 100; 

  // 滑鼠的初始位置（設為 -1000 是為了讓一開始畫面沒有滑鼠干擾）
  const mouse = { x: -1000, y: -1000 };

  // 2. 隨機生成所有的粒子
  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * width,  // 隨機的 X 座標
      y: Math.random() * height, // 隨機的 Y 座標
      
      // ⚙️ 【可調整】粒子的移動速度 (vx 是水平速度, vy 是垂直速度)
      // 目前的 1.5 是最大速度。如果把 1.5 改成 3.0，粒子就會飛得兩倍快！
      // 如果改成 0.5，粒子就會像灰塵一樣緩慢飄動。
      vx: (Math.random() - 0.5) * 1.5,
      vy: (Math.random() - 0.5) * 1.5,
      
      // ⚙️ 【可調整】粒子(圓點)的半徑大小
      // Math.random() * 2 + 1 代表半徑介於 1px 到 3px 之間
      // 如果想要大一點的圓點，可以改成 Math.random() * 4 + 2
      radius: Math.random() * 2 + 1 
    });
  }

  // 3. 監聽滑鼠移動，隨時更新滑鼠的座標
  const handleMouseMove = (e: MouseEvent) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  };
  window.addEventListener('mousemove', handleMouseMove);

  // 當瀏覽器視窗大小改變時，重新調整畫布大小
  const handleResize = () => {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
  };
  window.addEventListener('resize', handleResize);

  // 4. 動畫的核心迴圈 (每一幀都會執行一次)
  const animate = () => {
    // 每次畫新的一幀前，先把舊的畫面擦乾淨
    ctx.clearRect(0, 0, width, height);
    
    // 🎨 【可調整】圓點粒子的顏色與透明度
    // 目前是灰色 'rgba(150, 150, 150, 0.4)'
    // 如果要換成藍色，可以改為 'rgba(59, 130, 246, 0.5)'
    ctx.fillStyle = 'rgba(150, 150, 150, 0.4)';
    
    // ⚙️ 【可調整】所有連線的粗細
    // 預設是 1px。如果改成 2，線條會變得很粗很明顯
    ctx.lineWidth = 1;

    // 處理每一個粒子的移動與繪製
    particles.forEach((p, index) => {
      // 讓粒子依照自己的速度移動
      p.x += p.vx;
      p.y += p.vy;

      // 如果粒子撞到螢幕左邊或右邊，就反彈 (速度乘上 -1)
      if (p.x < 0 || p.x > width) p.vx *= -1;
      // 如果粒子撞到螢幕上面或下面，就反彈
      if (p.y < 0 || p.y > height) p.vy *= -1;

      // 把圓點畫出來
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fill();

      // 5. 繪製：粒子與粒子之間的連線
      for (let j = index + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy); // 計算兩個粒子的距離
        
        // ⚙️ 【可調整】粒子之間產生連線的「感應距離」
        // 目前是 120。如果改成 200，即使相隔很遠的粒子也會連線，畫面會像蜘蛛網一樣密集。
        if (dist < 150) {
          ctx.beginPath();
          // 🎨 【可調整】粒子間連線的顏色
          // 後面的 `${1 - dist / 120}` 是一個數學公式，代表「距離越遠，透明度越低(越淡)」
          ctx.strokeStyle = `rgba(150, 150, 150, ${1 - dist / 120})`;
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }
      }

      // 6. 繪製：粒子與「滑鼠」之間的連線
      const dxMouse = p.x - mouse.x;
      const dyMouse = p.y - mouse.y;
      const distMouse = Math.sqrt(dxMouse * dxMouse + dyMouse * dyMouse); // 計算粒子離滑鼠多遠
      
      // ⚙️ 【可調整】滑鼠的「吸附/感應距離」
      // 目前是 150。改成 300 的話，滑鼠的引力範圍會變得超大！
      if (distMouse < 150) {
        ctx.beginPath();
        // 🎨 【可調整】滑鼠互動連線的顏色
        // 預設是偏紫色 'rgba(100, 100, 255, ...)'
        // 後面的 0.8 是最大透明度（讓它看起來比普通的線更明顯亮眼）
        ctx.strokeStyle = `rgba(100, 100, 255, ${0.8 - distMouse / 150})`; 
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(mouse.x, mouse.y);
        ctx.stroke();
      }
    });

    // 不斷呼叫自己，讓畫面一直動下去
    animationFrameId = requestAnimationFrame(animate);
  };

  animate(); // 啟動動畫

  // 離開這個頁面時，記得清除監聽器跟動畫，避免網頁變卡或當機
  onBeforeUnmount(() => {
    window.removeEventListener('mousemove', handleMouseMove);
    window.removeEventListener('resize', handleResize);
    cancelAnimationFrame(animationFrameId);
  });
});
</script>
