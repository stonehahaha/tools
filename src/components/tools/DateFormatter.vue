<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElNotification, ElMessage } from 'element-plus'

const inputText = ref('')
const outputText = ref('')
const targetFormat = ref<'YYYY/MM/DD' | 'YYYY-MM-DD' | 'YYYY年MM月DD日'>('YYYY/MM/DD')
const loading = ref(false)

const stats = reactive({
  total: 0,
  padded: 0,
})

const clearInput = () => {
  inputText.value = ''
  outputText.value = ''
  stats.total = 0
  stats.padded = 0
}

const pad2 = (n: number) => (n < 10 ? `0${n}` : `${n}`)

const formatOne = (line: string) => {
  const trimmed = line.trim()
  if (!trimmed) return ''

  const patterns: RegExp[] = [
    /(\d{4})[\.\/-](\d{1,2})[\.\/-](\d{1,2})/,
    /(\d{4})年(\d{1,2})月(\d{1,2})日/,
    /(\d{4})\s+(\d{1,2})\s+(\d{1,2})/,
  ]

  let y = 0,
    m = 0,
    d = 0,
    matched = false,
    paddedCount = 0

  for (const re of patterns) {
    const match = trimmed.match(re)
    if (match) {
      y = Number(match[1])
      m = Number(match[2])
      d = Number(match[3])
      matched = true
      break
    }
  }

  if (!matched) return line

  const mm = pad2(m)
  const dd = pad2(d)
  if (mm !== `${m}`) paddedCount++
  if (dd !== `${d}`) paddedCount++

  stats.padded += paddedCount

  switch (targetFormat.value) {
    case 'YYYY/MM/DD':
      return `${y}/${mm}/${dd}`
    case 'YYYY-MM-DD':
      return `${y}-${mm}-${dd}`
    case 'YYYY年MM月DD日':
      return `${y}年${mm}月${dd}日`
    default:
      return `${y}/${mm}/${dd}`
  }
}

const formatDates = async () => {
  loading.value = true
  stats.total = 0
  stats.padded = 0
  try {
    const lines = inputText.value.split('\n')
    stats.total = lines.length
    const result = lines.map(formatOne).join('\n')
    outputText.value = result
    try {
      await navigator.clipboard.writeText(result)
      ElMessage.success('转换成功并自动复制结果')
    } catch {
      const textarea = document.createElement('textarea')
      textarea.value = result
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      ElMessage.success('转换成功并自动复制结果')
    }
  } catch {
    ElNotification({
      title: '转换失败',
      message: '请检查输入内容',
      type: 'error',
    })
  } finally {
    loading.value = false
  }
}

const copyResult = async () => {
  const text = outputText.value
  if (!text) return
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch {
    const textarea = document.createElement('textarea')
    textarea.value = text
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    ElMessage.success('已复制到剪贴板')
  }
}
</script>

<template>
  <el-row :gutter="20">
    <el-col :span="12">
      <div class="section">
        <div class="section-header">
          <span>输入日期</span>
          <el-button type="text" @click="clearInput">清空</el-button>
        </div>
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="15"
          placeholder="请输入日期，每行一个..."
          resize="vertical"
        />
        <div class="options">
          <el-select v-model="targetFormat" placeholder="选择格式" class="format-select">
            <el-option label="YYYY/MM/DD" value="YYYY/MM/DD" />
            <el-option label="YYYY-MM-DD" value="YYYY-MM-DD" />
            <el-option label="YYYY年MM月DD日" value="YYYY年MM月DD日" />
          </el-select>
          <el-button type="primary" @click="formatDates" :loading="loading">转换</el-button>
        </div>
      </div>
    </el-col>
    <el-col :span="12">
      <div class="section">
        <div class="section-header">
          <span>转换结果</span>
          <el-button type="primary" plain @click="copyResult" :disabled="!outputText"
            >复制</el-button
          >
        </div>
        <el-input v-model="outputText" type="textarea" :rows="15" readonly resize="vertical" />
        <div class="stats">
          <el-alert
            :title="`总行数：${stats.total}，补零次数：${stats.padded}`"
            type="info"
            :closable="false"
            show-icon
          />
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<style scoped>
.section {
  padding: 8px 0;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.options {
  margin-top: 12px;
  display: flex;
  gap: 12px;
}
.format-select {
  width: 220px;
}
.stats {
  margin-top: 12px;
}
</style>
