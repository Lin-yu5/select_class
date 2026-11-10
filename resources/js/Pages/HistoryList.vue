<template>
  <div class="min-h-screen bg-background relative pb-20">
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

    <main class="pt-24 max-w-6xl mx-auto px-container-margin relative z-10">
      
      <div class="mb-xl text-center md:text-left">
        <h2 class="font-display-lg text-display-lg text-on-surface mb-2">歷史測驗紀錄</h2>
        <p class="font-body-lg text-body-lg text-on-surface-variant">學號：<span class="font-bold text-primary">{{ student_id }}</span> 的專屬職能成長路徑與推薦歷程。</p>
      </div>

      <div v-if="historyRecords.length === 0" class="bg-surface p-xl rounded-2xl card-shadow text-center">
        <p class="font-headline-md text-headline-md text-on-surface-variant mb-lg">目前還沒有測驗紀錄喔！趕快去進行第一次測驗吧！</p>
        <Link href="/cpas/enter" class="primary-btn px-lg py-sm rounded-lg font-label-lg transition no-underline">
          前往測驗
        </Link>
      </div>

      <div v-else class="flex flex-col gap-xl">
        <div 
          v-for="(record, index) in historyRecords" 
          :key="record.id" 
          class="bg-surface p-xl rounded-2xl card-shadow border border-outline-variant hover:border-primary transition-all duration-300"
        >
          <div class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-outline-variant pb-md mb-lg">
            <h3 class="font-headline-lg text-headline-lg text-primary">第 {{ historyRecords.length - index }} 次分析結果</h3>
            <span class="font-label-sm text-on-surface-variant mt-2 md:mt-0 bg-surface-container-low px-md py-sm rounded-full">
              測驗時間：{{ record.created_at }}
            </span>
          </div>

          <div class="mb-xl">
            <h4 class="font-headline-md text-headline-md text-on-surface mb-md">核心能力分數</h4>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-md">
              <div class="bg-surface-container-lowest border border-outline-variant p-md rounded-xl flex flex-col items-center text-center">
                <span class="font-label-lg text-on-surface-variant mb-1">執行力</span>
                <span class="text-2xl font-bold text-on-surface">{{ record.core6_scores[0] }}</span>
              </div>
              <div class="bg-surface-container-lowest border border-outline-variant p-md rounded-xl flex flex-col items-center text-center">
                <span class="font-label-lg text-on-surface-variant mb-1">統御力</span>
                <span class="text-2xl font-bold text-on-surface">{{ record.core6_scores[1] }}</span>
              </div>
              <div class="bg-surface-container-lowest border border-outline-variant p-md rounded-xl flex flex-col items-center text-center">
                <span class="font-label-lg text-on-surface-variant mb-1">親和力</span>
                <span class="text-2xl font-bold text-on-surface">{{ record.core6_scores[2] }}</span>
              </div>
              <div class="bg-surface-container-lowest border border-outline-variant p-md rounded-xl flex flex-col items-center text-center">
                <span class="font-label-lg text-on-surface-variant mb-1">開創力</span>
                <span class="text-2xl font-bold text-on-surface">{{ record.core6_scores[3] }}</span>
              </div>
              <div class="bg-surface-container-lowest border border-outline-variant p-md rounded-xl flex flex-col items-center text-center">
                <span class="font-label-lg text-on-surface-variant mb-1">應變力</span>
                <span class="text-2xl font-bold text-on-surface">{{ record.core6_scores[4] }}</span>
              </div>
              <div class="bg-surface-container-lowest border border-outline-variant p-md rounded-xl flex flex-col items-center text-center">
                <span class="font-label-lg text-on-surface-variant mb-1">敏感力</span>
                <span class="text-2xl font-bold text-on-surface">{{ record.core6_scores[5] }}</span>
              </div>
            </div>
          </div>

          <div>
            <h4 class="font-headline-md text-headline-md text-on-surface mb-md">
              推薦通識課程 <span class="font-body-md text-on-surface-variant">(共 {{ record.recommended_courses.length }} 門)</span>
            </h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-md">
              <div 
                v-for="course in record.recommended_courses" 
                :key="course.class_id" 
                class="bg-surface border border-outline-variant hover:border-primary transition-all duration-300 rounded-xl p-md flex flex-col justify-between"
              >
                <div class="font-headline-md text-on-surface mb-3">
                  {{ course.class_name_chinese || course.class_name || '未知課程' }} 
                </div>
                
                <div class="mt-auto flex justify-between items-center w-full">
                  <span v-if="course.relation_type === 'strong'" class="bg-primary-container text-primary px-3 py-1 rounded-full font-label-sm">
                    強關係推薦
                  </span>
                  <span v-else-if="course.relation_type === 'weak'" class="bg-secondary-container/20 text-secondary px-3 py-1 rounded-full font-label-sm">
                    弱關係推薦
                  </span>
                  <span v-else-if="course.relation_type === 'both'" class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full font-label-sm">
                    強弱綜合推薦
                  </span>
                  <span v-else></span>

                  <a 
                    v-if="course.course_url" 
                    :href="course.course_url" 
                    target="_blank" 
                    class="inline-flex items-center gap-1 text-sm text-primary hover:text-primary-dark transition-colors no-underline font-medium"
                  >
                    查看課程大綱
                    <span class="material-symbols-outlined text-sm">open_in_new</span>
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-8 pt-6 border-t border-outline-variant flex justify-center md:justify-end">
            <Link 
              :href="`/cpas/result/${student_id}?record_id=${record.id}`" 
              class="bg-primary text-on-primary px-6 py-2.5 rounded-full font-label-lg flex items-center gap-2 hover:bg-primary-dark hover:-translate-y-0.5 hover:shadow-lg transition-all duration-300 no-underline"
            >
              <span>查看此測驗完整分析</span>
              <span class="material-symbols-outlined text-sm">arrow_forward</span>
            </Link>
          </div>

        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { Link } from '@inertiajs/vue3';

const isMenuOpen = ref(false);

const props = defineProps({
  student_id: String,
  historyRecords: {
    type: Array,
    default: () => []
  }
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
  
  const particleCount = 100; 

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
        
        if (dist < 150) {
          ctx.beginPath();
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