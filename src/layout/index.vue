<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { MagicStick, Calendar, List } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 模拟从 constantRoutes 中提取需要显示的菜单
const menuItems = [
  {
    path: '/date-formatter',
    name: 'DateFormatter',
    title: '日期转换',
    icon: Calendar
  },
  {
    path: '/text-formatter',
    name: 'TextFormatter',
    title: '文本整理',
    icon: List
  }
]

const activePath = computed(() => route.path)

const handleSelect = (path: string) => {
  router.push(path)
}
</script>

<template>
  <div class="layout">
    <!-- 顶部品牌区 -->
    <div class="topbar">
      <div class="brand">
        <div class="brand-icon">
          <el-icon size="24"><MagicStick /></el-icon>
        </div>
        <div class="brand-text">
          <h1>数据格式转换</h1>
          <p>快速处理·安全高效</p>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧侧边栏导航 -->
      <div class="sidebar">
        <div class="sidebar-tabs">
          <button
            v-for="item in menuItems"
            :key="item.path"
            :class="['sidebar-tab', { active: activePath === item.path }]"
            @click="handleSelect(item.path)"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.title }}</span>
          </button>
        </div>

        <div class="sidebar-footer">
          <div class="safety-badge">
            <el-icon color="#10b981">
              <svg width="16" height="16" viewBox="0 0 16 16">
                <circle cx="8" cy="8" r="6" fill="currentColor" />
              </svg>
            </el-icon>
            <span>纯前端处理·数据不离开您的浏览器</span>
          </div>
        </div>
      </div>

      <!-- 右侧工作区 -->
      <div class="work-area">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #f7f9fc 0%, #f0f4f8 100%);
}

.topbar {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 16px 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.brand {
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.brand-text h1 {
  font-size: 20px;
  font-weight: 700;
  color: #1a202c;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-text p {
  font-size: 12px;
  color: #718096;
  margin: 2px 0 0 0;
  font-weight: 400;
}

.main-content {
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px;
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 24px;
  min-height: calc(100vh - 80px);
}

.sidebar {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  padding: 20px 0;
  height: fit-content;
  position: sticky;
  top: 104px;
}

.sidebar-tabs {
  display: flex;
  flex-direction: column;
  padding: 0 12px;
  gap: 4px;
}

.sidebar-tab {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border: none;
  background: none;
  border-radius: 12px;
  cursor: pointer;
  color: #718096;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  text-align: left;
  position: relative;
}

.sidebar-tab:hover {
  background: #f7fafc;
  color: #4a5568;
}

.sidebar-tab.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  color: #667eea;
  font-weight: 600;
}

.sidebar-tab.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 0 2px 2px 0;
}

.sidebar-footer {
  margin-top: 20px;
  padding: 20px 12px 0;
  border-top: 1px solid #e2e8f0;
}

.safety-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 8px;
  background: #f0f9ff;
  border: 1px solid #e0f2fe;
  font-size: 11px;
  color: #0369a1;
  line-height: 1.4;
}

.work-area {
  min-height: calc(100vh - 128px);
}
</style>
