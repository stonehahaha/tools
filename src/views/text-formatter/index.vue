<template>
  <div class="tool-view">
    <!-- 工具标题 -->
    <div class="tool-header">
      <h2>
        <el-icon><Document /></el-icon>
        文本数据整理
      </h2>
      <p class="tool-desc">去除空行并格式化文本，适合Excel粘贴</p>
    </div>

    <!-- 功能模式切换 -->
    <div class="mode-switcher">
      <el-radio-group v-model="mode" size="large">
        <el-radio-button label="basic">基础整理</el-radio-button>
        <el-radio-button label="passenger">旅客信息整理</el-radio-button>
      </el-radio-group>
    </div>

    <div class="tool-layout">
      <!-- 工具主内容 -->
      <div class="tool-main">
        <!-- 输入区域 -->
        <div class="input-section">
          <div class="section-header">
            <h3>{{ mode === 'basic' ? '输入文本' : '粘贴旅客信息' }}</h3>
            <div class="actions">
              <el-button type="text" @click="clearAll" :icon="Delete"> 清空 </el-button>
              <el-button
                v-if="mode === 'passenger'"
                type="text"
                @click="loadExample"
                :icon="DocumentCopy"
              >
                加载示例
              </el-button>
            </div>
          </div>
          <el-input
            v-model="inputText"
            type="textarea"
            :rows="12"
            :placeholder="inputPlaceholder"
            resize="vertical"
            class="input-area"
          />
        </div>

        <!-- 处理选项 -->
        <div class="options-section" v-if="mode === 'basic'">
          <div class="option-item">
            <el-switch
              v-model="autoCopy"
              inline-prompt
              active-text="自动复制"
              inactive-text="手动复制"
            />
            <span class="option-label">转换后自动复制结果</span>
          </div>
        </div>

        <div class="actions-section">
          <el-button
            type="primary"
            size="large"
            :icon="MagicStick"
            @click="processData"
            :loading="loading"
          >
            {{ mode === 'basic' ? '整理文本' : '提取旅客信息' }}
          </el-button>
          <el-button
            v-if="!autoCopy && outputText"
            type="success"
            size="large"
            :icon="CopyDocument"
            @click="copyResult"
          >
            复制结果
          </el-button>
        </div>

        <!-- 输出区域 -->
        <div class="output-section">
          <div class="section-header">
            <h3>{{ mode === 'basic' ? '整理结果' : '提取结果' }}</h3>
            <div class="stats" v-if="stats.processed > 0">
              <span class="stat-item">处理: {{ stats.processed }} 行</span>
              <span class="stat-item">成功: {{ stats.success }} 个</span>
              <span class="stat-item">失败: {{ stats.failed }} 个</span>
            </div>
          </div>
          <el-input
            v-model="outputText"
            type="textarea"
            :rows="12"
            placeholder="处理结果将显示在这里..."
            readonly
            resize="vertical"
            class="output-area"
          />
        </div>
      </div>

      <!-- 右侧指南区 -->
      <div class="tool-guide">
        <div class="guide-card">
          <h3>{{ mode === 'basic' ? '基础整理' : '旅客信息整理' }}</h3>

          <div v-if="mode === 'basic'" class="guide-steps">
            <div class="guide-step">
              <div class="step-number">1</div>
              <div class="step-content">
                <h4>粘贴数据</h4>
                <p>粘贴姓名和编号，支持制表符或空格分隔</p>
              </div>
            </div>
            <div class="guide-step">
              <div class="step-number">2</div>
              <div class="step-content">
                <h4>点击整理</h4>
                <p>去除空行，统一用制表符分隔两列</p>
              </div>
            </div>
            <div class="guide-step">
              <div class="step-number">3</div>
              <div class="step-content">
                <h4>使用数据</h4>
                <p>整理完成后将自动复制结果并提示</p>
              </div>
            </div>
          </div>

          <div v-else class="guide-steps">
            <div class="guide-step">
              <div class="step-number">1</div>
              <div class="step-content">
                <h4>复制数据</h4>
                <p>从厦航官网复制完整的旅客信息</p>
              </div>
            </div>
            <div class="guide-step">
              <div class="step-number">2</div>
              <div class="step-content">
                <h4>粘贴整理</h4>
                <p>粘贴到左侧输入框，点击"提取旅客信息"</p>
              </div>
            </div>
            <div class="guide-step">
              <div class="step-number">3</div>
              <div class="step-content">
                <h4>获取结果</h4>
                <p>自动提取姓名和乘客号，格式化为三列表格</p>
              </div>
            </div>
          </div>

          <div class="quick-example">
            <h4>快速示例</h4>
            <pre v-if="mode === 'basic'">
姓名1  123456
姓名2	789012

姓名3  abcdef</pre
            >
            <pre v-else>
ZHENG/YANQING
成人
ER0775485
380
988.00
CNY
1368
7312180801003
SONG/MEIZHU
成人
ER0775139
380
988.00
CNY
1368
7312180801000</pre
            >
          </div>

          <div class="format-example" v-if="mode === 'passenger'">
            <h4>输出格式</h4>
            <pre>
1	ZHENG/YANQING	7312180801003
2	SONG/MEIZHU	7312180801000
3	ZHANG/ZHIRONG	7312180801002
4	ZHANG/XUEMEI	7312180801001
5	MA/YONGXING	7312180800999</pre
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Document, MagicStick, CopyDocument, Delete, DocumentCopy } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 模式：basic(基础整理) 或 passenger(旅客信息整理)
const mode = ref<'basic' | 'passenger'>('basic')
const inputText = ref('')
const outputText = ref('')
const loading = ref(false)
const autoCopy = ref(true)

// 处理统计
const stats = ref({
  processed: 0,
  success: 0,
  failed: 0,
})

// 根据模式计算输入框提示
const inputPlaceholder = computed(() => {
  if (mode.value === 'basic') {
    return '粘贴文本数据，每行格式：姓名 编号（支持制表符或空格分隔）\n\n示例：\nZHANG/SAN 7312180751638\nLI/SI 7312180751639\n\n注意：\n1. 空行会自动去除\n2. 多空格会自动转换为制表符\n3. 可直接复制到Excel'
  } else {
    return '粘贴从厦航官网复制的旅客信息，格式如下：\n\nZHENG/YANQING\n成人\nER0775485\n380\n988.00\nCNY\n1368\n7312180801003\nSONG/MEIZHU\n成人\nER0775139\n380\n988.00\nCNY\n1368\n7312180801000\n\n系统将自动提取姓名和乘客号，格式化为：序号\\t姓名\\t乘客号'
  }
})

// 加载旅客信息示例
const loadExample = () => {
  inputText.value = `ZHENG/YANQING
成人
ER0775485
380
988.00
CNY
1368
7312180801003
SONG/MEIZHU
成人
ER0775139
380
988.00
CNY
1368
7312180801000
ZHANG/ZHIRONG
成人
ER0770869
380
988.00
CNY
1368
7312180801002
ZHANG/XUEMEI
成人
ER0775177
380
988.00
CNY
1368
7312180801001
MA/YONGXING
成人
ER0777495
380
988.00
CNY
1368
7312180800999`
  ElMessage.success('已加载示例数据')
}

// 清除所有内容
const clearAll = () => {
  inputText.value = ''
  outputText.value = ''
  resetStats()
}

// 重置统计
const resetStats = () => {
  stats.value = {
    processed: 0,
    success: 0,
    failed: 0,
  }
}

// 复制结果到剪贴板
const copyResult = async () => {
  if (!outputText.value) {
    ElMessage.warning('没有可复制的内容')
    return
  }

  try {
    await navigator.clipboard.writeText(outputText.value)
    ElMessage.success('已复制到剪贴板')
  } catch (_err) {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = outputText.value
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    ElMessage.success('已复制到剪贴板')
  }
}

// 基础文本整理功能
const processBasicText = () => {
  if (!inputText.value.trim()) {
    ElMessage.warning('请输入要处理的文本')
    return
  }

  const lines = inputText.value.split('\n')
  const result: string[] = []
  let processed = 0
  let success = 0
  let failed = 0

  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) continue // 跳过空行

    processed++

    // 分割姓名和数字
    const parts = trimmed.split(/\t| {2,}|\s(?=\d)/)
    if (parts.length >= 2) {
      result.push(`${parts[0]}\t${parts[1]}`)
      success++
    } else {
      result.push(trimmed)
      failed++
    }
  }

  outputText.value = result.join('\n')
  stats.value = { processed, success, failed }

  if (autoCopy.value) {
    copyResult()
  }

  ElMessage.success(`已整理 ${success} 行数据`)
}

// 旅客信息整理功能
const processPassengerInfo = () => {
  if (!inputText.value.trim()) {
    ElMessage.warning('请输入旅客信息')
    return
  }

  // 先过滤掉所有空行和仅包含空白字符的行
  const lines = inputText.value
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)

  const result: string[] = []
  let processed = 0
  let success = 0
  let failed = 0
  let passengerIndex = 0

  // 正则表达式匹配
  // 姓名：包含字母和斜杠，通常是 LAST/FIRST 或 LAST/FIRST/MIDDLE
  const namePattern = /^[A-Z]+\/[A-Z/]+$/
  // 票号：13位数字，通常以7312开头
  const passengerNumberPattern = /^7312\d{9}$/

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    // 检查是否是姓名行
    if (namePattern.test(line)) {
      processed++
      let passengerNumber = ''

      // 在后续行中查找票号，直到遇到下一个姓名或文件末尾
      // 限制查找范围为接下来的 15 行有效数据，防止跨度过大
      for (let j = i + 1; j < Math.min(i + 15, lines.length); j++) {
        // 如果遇到了下一个姓名，说明当前旅客的票号可能漏了
        if (namePattern.test(lines[j])) {
          break
        }
        if (passengerNumberPattern.test(lines[j])) {
          passengerNumber = lines[j]
          break
        }
      }

      passengerIndex++
      if (passengerNumber) {
        result.push(`${passengerIndex}\t${line}\t${passengerNumber}`)
        success++
      } else {
        result.push(`${passengerIndex}\t${line}\tMISSING`)
        failed++
      }
    }
  }

  outputText.value = result.join('\n')
  stats.value = { processed, success, failed }

  if (autoCopy.value) {
    copyResult()
  }

  if (success > 0) {
    ElMessage.success(`已提取 ${success} 个旅客信息`)
  } else {
    ElMessage.warning('未找到有效的旅客信息，请检查格式')
  }
}

// 处理数据
const processData = () => {
  loading.value = true
  resetStats()

  try {
    if (mode.value === 'basic') {
      processBasicText()
    } else {
      processPassengerInfo()
    }
  } catch (error) {
    ElMessage.error('处理数据时出错：' + error)
  } finally {
    loading.value = false
  }
}

// 监听模式变化
onMounted(() => {
  // 从localStorage加载设置
  const savedMode = localStorage.getItem('textFormatterMode')
  if (savedMode === 'basic' || savedMode === 'passenger') {
    mode.value = savedMode
  }
})

watch(mode, (newMode) => {
  localStorage.setItem('textFormatterMode', newMode)
})
</script>

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

/* 模式切换器 */
.mode-switcher {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.mode-switcher .el-radio-group {
  width: 100%;
  display: flex;
}

.mode-switcher .el-radio-button {
  flex: 1;
  text-align: center;
}

.mode-switcher .el-radio-button__inner {
  width: 100%;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 500;
}

/* 主布局 */
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
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 输入输出区域 */
.input-section,
.output-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.actions {
  display: flex;
  gap: 8px;
}

.stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #718096;
}

.stat-item {
  padding: 2px 8px;
  border-radius: 4px;
  background: #f7fafc;
}

.input-area,
.output-area {
  width: 100%;
}

/* 选项区域 */
.options-section {
  padding: 16px;
  background: #f7fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.option-label {
  font-size: 13px;
  color: #4a5568;
}

/* 操作区域 */
.actions-section {
  display: flex;
  gap: 12px;
  padding: 16px 0;
  border-top: 1px solid #e2e8f0;
  border-bottom: 1px solid #e2e8f0;
}

/* 指南区域 */
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

.quick-example,
.format-example {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.quick-example h4,
.format-example h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1a202c;
  margin: 0 0 12px 0;
}

.quick-example pre,
.format-example pre {
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
  white-space: pre-wrap;
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
