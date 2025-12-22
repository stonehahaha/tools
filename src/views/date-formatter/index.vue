<script setup lang="ts">
import DateFormatter from '@/components/tools/DateFormatter.vue'
import { Document } from '@element-plus/icons-vue'
</script>

<template>
  <div class="tool-view">
    <!-- 工具标题 -->
    <div class="tool-header">
      <h2>
        <el-icon><Document /></el-icon>
        日期格式转换
      </h2>
      <p class="tool-desc">支持多种日期格式混合输入，统一转换为标准格式</p>
    </div>

    <div class="tool-layout">
      <!-- 工具主内容 -->
      <div class="tool-main">
        <DateFormatter />
      </div>

      <!-- 右侧指南区 -->
      <div class="tool-guide">
        <div class="guide-card">
          <h3>使用指南</h3>
          <div class="guide-steps">
            <div class="guide-step">
              <div class="step-number">1</div>
              <div class="step-content">
                <h4>输入日期</h4>
                <p>每行一个日期，支持：<br />2025.12.31、2025/12/31、2025-12-31、2025年12月31日</p>
              </div>
            </div>
            <div class="guide-step">
              <div class="step-number">2</div>
              <div class="step-content">
                <h4>选择格式</h4>
                <p>选择输出格式，默认YYYY/MM/DD（Excel兼容）</p>
              </div>
            </div>
            <div class="guide-step">
              <div class="step-number">3</div>
              <div class="step-content">
                <h4>点击转换</h4>
                <p>转换完成后将自动复制结果并提示</p>
              </div>
            </div>
          </div>
          <div class="quick-example">
            <h4>快速示例</h4>
            <pre>
2025.12.31
2025/1/5
2034-4-6
2028年5月23日</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tool-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.tool-header {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.tool-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-desc {
  color: #718096;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
}

.tool-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  align-items: start;
}

.tool-main {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 24px;
  min-height: 600px;
}

.tool-guide {
  position: sticky;
  top: 104px;
}

.guide-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 24px;
  border: 1px solid #e2e8f0;
}

.guide-card h3 {
  font-size: 18px;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 20px 0;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.guide-steps {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.guide-step {
  display: flex;
  gap: 12px;
}

.step-number {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
}

.step-content h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1a202c;
  margin: 0 0 4px 0;
}

.step-content p {
  font-size: 13px;
  color: #718096;
  line-height: 1.5;
  margin: 0;
}

.quick-example {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.quick-example h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1a202c;
  margin: 0 0 12px 0;
}

.quick-example pre {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  font-size: 12px;
  color: #4a5568;
  line-height: 1.5;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  overflow-x: auto;
  margin: 0;
}

@media (max-width: 1200px) {
  .tool-layout {
    grid-template-columns: 1fr;
  }
  .tool-guide {
    position: static;
  }
}
</style>
