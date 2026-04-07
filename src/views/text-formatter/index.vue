<template>
  <div class="tool-view">
    <div class="tool-header">
      <h2>
        <el-icon><Document /></el-icon>
        旅客信息整理
      </h2>
      <p class="tool-desc">从旅客订单文本中提取姓名与乘客号，整理为可直接粘贴到 Excel 的表格</p>
    </div>

    <div class="tool-layout">
      <div class="tool-main">
        <div class="input-section">
          <div class="section-header">
            <h3>粘贴旅客信息</h3>
            <div class="actions">
              <el-button link @click="clearAll" :icon="Delete">清空</el-button>
              <el-button link @click="loadExample" :icon="DocumentCopy">加载示例</el-button>
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

        <div class="actions-section">
          <el-button
            type="primary"
            size="large"
            :icon="MagicStick"
            @click="processData"
            :loading="loading"
          >
            提取旅客信息
          </el-button>
          <el-button
            v-if="outputText"
            type="success"
            size="large"
            :icon="CopyDocument"
            @click="copyResult"
          >
            复制结果
          </el-button>
        </div>

        <div class="output-section">
          <div class="section-header">
            <h3>提取结果</h3>
            <div class="stats" v-if="stats.processed > 0">
              <span class="stat-item">处理: {{ stats.processed }} 个</span>
              <span class="stat-item">成功: {{ stats.success }} 个</span>
              <span class="stat-item">失败: {{ stats.failed }} 个</span>
            </div>
          </div>
          <el-input
            v-model="outputText"
            type="textarea"
            :rows="12"
            placeholder="提取结果将显示在这里..."
            readonly
            resize="vertical"
            class="output-area"
          />
        </div>
      </div>

      <div class="tool-guide">
        <div class="guide-card">
          <h3>旅客信息整理</h3>

          <div class="guide-steps">
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
                <p>粘贴到左侧输入框，点击“提取旅客信息”</p>
              </div>
            </div>
            <div class="guide-step">
              <div class="step-number">3</div>
              <div class="step-content">
                <h4>获取结果</h4>
                <p>系统会自动提取姓名和乘客号，并按制表符分隔输出</p>
              </div>
            </div>
          </div>

          <div class="quick-example">
            <h4>快速示例</h4>
            <pre>{{ samplePassengerInfo }}</pre>
          </div>

          <div class="format-example">
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
import { ref } from 'vue'
import { Document, MagicStick, CopyDocument, Delete, DocumentCopy } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const samplePassengerInfo = `ZHENG/YANQING
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

const inputPlaceholder = `粘贴从厦航官网复制的旅客信息，格式如下：

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
7312180801000

系统将自动提取姓名和乘客号，格式化为：序号\\t姓名\\t乘客号`

const inputText = ref('')
const outputText = ref('')
const loading = ref(false)
const stats = ref({
  processed: 0,
  success: 0,
  failed: 0,
})

const resetStats = () => {
  stats.value = {
    processed: 0,
    success: 0,
    failed: 0,
  }
}

const clearAll = () => {
  inputText.value = ''
  outputText.value = ''
  resetStats()
}

const loadExample = () => {
  inputText.value = samplePassengerInfo
  ElMessage.success('已加载示例数据')
}

const copyResult = async () => {
  if (!outputText.value) {
    ElMessage.warning('没有可复制的内容')
    return
  }

  try {
    await navigator.clipboard.writeText(outputText.value)
    ElMessage.success('已复制到剪贴板')
  } catch {
    const textarea = document.createElement('textarea')
    textarea.value = outputText.value
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    ElMessage.success('已复制到剪贴板')
  }
}

const processPassengerInfo = () => {
  if (!inputText.value.trim()) {
    ElMessage.warning('请输入旅客信息')
    return
  }

  const lines = inputText.value
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)

  const result: string[] = []
  let processed = 0
  let success = 0
  let failed = 0
  let passengerIndex = 0

  const namePattern = /^[A-Z]+\/[A-Z/]+$/
  const passengerNumberPattern = /^7312\d{9}$/

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (line === undefined || !namePattern.test(line)) {
      continue
    }

    processed++
    passengerIndex++
    let passengerNumber = ''

    for (let j = i + 1; j < Math.min(i + 15, lines.length); j++) {
      const currentLine = lines[j]
      if (currentLine === undefined) {
        continue
      }
      if (namePattern.test(currentLine)) {
        break
      }
      if (passengerNumberPattern.test(currentLine)) {
        passengerNumber = currentLine
        break
      }
    }

    if (passengerNumber) {
      result.push(`${passengerIndex}\t${line}\t${passengerNumber}`)
      success++
    } else {
      result.push(`${passengerIndex}\t${line}\tMISSING`)
      failed++
    }
  }

  outputText.value = result.join('\n')
  stats.value = { processed, success, failed }

  if (outputText.value) {
    void copyResult()
  }

  if (success > 0) {
    ElMessage.success(`已提取 ${success} 个旅客信息`)
  } else {
    ElMessage.warning('未找到有效的旅客信息，请检查格式')
  }
}

const processData = () => {
  loading.value = true
  resetStats()

  try {
    processPassengerInfo()
  } catch (error) {
    ElMessage.error('处理数据时出错：' + error)
  } finally {
    loading.value = false
  }
}
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
