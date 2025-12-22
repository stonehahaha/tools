<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const inputText = ref('')
const outputText = ref('')
const loading = ref(false)

const stats = reactive({
  total: 0,
})

const clearInput = () => {
  inputText.value = ''
  outputText.value = ''
  stats.total = 0
}

const formatText = (text: string) => {
  return text
    .split('\n')
    .filter((line) => line.trim())
    .map((line) => {
      const parts = line.split(/\t| {2,}/).filter((p) => p.trim() !== '')
      if (parts.length >= 2) {
        return `${parts[0]}\t${parts[1]}`
      }
      return line
    })
    .join('\n')
}

const format = async () => {
  loading.value = true
  try {
    stats.total = inputText.value.split('\n').length
    const result = formatText(inputText.value)
    outputText.value = result
    try {
      await navigator.clipboard.writeText(result)
      ElMessage.success('整理成功并自动复制结果')
    } catch {
      const textarea = document.createElement('textarea')
      textarea.value = result
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      ElMessage.success('整理成功并自动复制结果')
    }
  } catch {
    ElMessage.error('整理失败，请检查输入')
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
          <span>输入文本</span>
          <el-button type="text" @click="clearInput">清空</el-button>
        </div>
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="15"
          placeholder="每行：姓名 + 制表符/多个空格 + 数字"
          resize="vertical"
        />
        <div class="options">
          <el-button type="primary" @click="format" :loading="loading">整理</el-button>
        </div>
      </div>
    </el-col>
    <el-col :span="12">
      <div class="section">
        <div class="section-header">
          <span>整理结果</span>
          <el-button type="primary" plain @click="copyResult" :disabled="!outputText"
            >复制</el-button
          >
        </div>
        <el-input v-model="outputText" type="textarea" :rows="15" readonly resize="vertical" />
        <div class="stats">
          <el-alert :title="`总行数：${stats.total}`" type="info" :closable="false" show-icon />
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
.stats {
  margin-top: 12px;
}
</style>
