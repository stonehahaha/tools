<template>
  <div class="tool-view">
    <div class="tool-header">
      <h2>
        <el-icon><Document /></el-icon>
        PDF 行程整理
      </h2>
      <p class="tool-desc">
        同步名册与 PDF 行程，自动匹配团队、人员与票号，输出可供航旅组织使用的分组资料。
      </p>
    </div>

    <div class="tool-layout">
      <div class="tool-main">
        <div class="file-section">
          <div class="section-header">
            <h3>上传文件</h3>
            <p>请先上传团队名册和行程 PDF，支持 Excel/CSV 与任意多页行程单。</p>
          </div>
          <div class="file-grid">
            <label class="file-field">
              <span>团队名册</span>
              <div class="file-input-wrapper">
                <input
                  data-testid="roster-input"
                  type="file"
                  accept=".xls,.xlsx,.csv"
                  @change="handleRosterChange"
                />
                <span class="file-name">{{ rosterLabel }}</span>
              </div>
            </label>
            <label class="file-field">
              <span>PDF 行程</span>
              <div class="file-input-wrapper">
                <input
                  data-testid="pdf-input"
                  type="file"
                  accept=".pdf"
                  @change="handlePdfChange"
                />
                <span class="file-name">{{ pdfLabel }}</span>
              </div>
            </label>
          </div>
        </div>

        <div class="optional-section">
          <div class="section-header">
            <h3>可选参数</h3>
            <p>默认配置适用大多数表格，只有在匹配错误时再调整。</p>
          </div>
          <div class="form-grid">
            <div class="form-cell">
              <label>页签索引</label>
              <el-input-number v-model="sheet" :min="0" controls-position="right" />
              <p class="hint">从 0 开始，0 代表第一个表格页签。</p>
            </div>
            <div class="form-cell">
              <label>姓名列</label>
              <el-input v-model="nameColumn" placeholder="例如 B" />
            </div>
            <div class="form-cell">
              <label>团体列</label>
              <el-input v-model="teamColumn" placeholder="例如 C" />
            </div>
            <div class="form-cell">
              <label>模糊匹配阈值</label>
              <el-input-number v-model="fuzzyThreshold" :min="0" :max="100" controls-position="right" />
              <p class="hint">数值越高匹配越严格，默认 80。</p>
            </div>
          </div>
        </div>

        <div class="actions-section">
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            :disabled="!canSubmit"
            @click="submitSplit"
            data-testid="split-button"
          >
            <el-icon><MagicStick /></el-icon>
            拆分并下载
          </el-button>
        </div>
      </div>

      <div class="tool-guide">
        <div class="guide-card">
          <h3>使用指南</h3>
          <div class="guide-steps">
            <div class="guide-step">
              <div class="step-number">1</div>
              <div class="step-content">
                <h4>上传名册</h4>
                <p>名册需包含中英文姓名、护照或票号，支持 Excel 与 CSV 格式。</p>
              </div>
            </div>
            <div class="guide-step">
              <div class="step-number">2</div>
              <div class="step-content">
                <h4>上传 PDF</h4>
                <p>确保 PDF 为实际行程单，单页或多页均支持。</p>
              </div>
            </div>
            <div class="guide-step">
              <div class="step-number">3</div>
              <div class="step-content">
                <h4>调整参数</h4>
                <p>当默认列号无效时，通过可选参数修改姓名/团体列或阈值。</p>
              </div>
            </div>
            <div class="guide-step">
              <div class="step-number">4</div>
              <div class="step-content">
                <h4>下载结果</h4>
                <p>拆分完成后会自动下载；若未触发，可手动再次点击。</p>
              </div>
            </div>
          </div>
          <div class="quick-tip">
            <h4>提示</h4>
            <p>下载失败可尝试清除浏览器缓存或切换至桌面浏览器。</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Document, MagicStick } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import { downloadPdfTeamSplitResult, requestPdfTeamSplit } from '@/api/pdfTeamSplit'

const rosterFile = ref<File | null>(null)
const pdfFile = ref<File | null>(null)
const sheet = ref(0)
const nameColumn = ref('B')
const teamColumn = ref('C')
const fuzzyThreshold = ref(80)
const loading = ref(false)

const rosterLabel = computed(() => rosterFile.value?.name ?? '尚未选择名册文件')
const pdfLabel = computed(() => pdfFile.value?.name ?? '尚未选择 PDF 文件')
const canSubmit = computed(() => !!rosterFile.value && !!pdfFile.value && !loading.value)

const handleFileChange = (event: Event, setter: (file: File | null) => void) => {
  const target = event.target as HTMLInputElement
  setter(target.files?.[0] ?? null)
}

const handleRosterChange = (event: Event) => handleFileChange(event, (file) => (rosterFile.value = file))
const handlePdfChange = (event: Event) => handleFileChange(event, (file) => (pdfFile.value = file))

const appendOptionalFields = (formData: FormData) => {
  formData.append('name_column', nameColumn.value)
  formData.append('team_column', teamColumn.value)
  formData.append('fuzzy_threshold', String(fuzzyThreshold.value))
}

const submitSplit = async () => {
  if (!canSubmit.value) {
    ElMessage.warning('请先上传名册与 PDF 文件。')
    return
  }

  const formData = new FormData()
  formData.append('roster', rosterFile.value as File)
  formData.append('pdf', pdfFile.value as File)
  formData.append('sheet', String(sheet.value))
  appendOptionalFields(formData)

  loading.value = true
  try {
    const blob = await requestPdfTeamSplit(formData)
    downloadPdfTeamSplitResult(blob, 'pdf-team-split-result.zip')
    ElMessage.success('拆分成功，文件正在下载。')
  } catch (error) {
    const message = error instanceof Error ? error.message : 'PDF 行程整理失败，请稍后再试。'
    ElMessage.error(message)
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
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-desc {
  margin: 0;
  color: #718096;
  font-size: 14px;
  line-height: 1.5;
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
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.file-section,
.optional-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.section-header p {
  margin: 0;
  color: #718096;
  font-size: 13px;
}

.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.file-field {
  display: flex;
  flex-direction: column;
  gap: 12px;
  border: 1px dashed #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  background: #fdfdfd;
}

.file-field span {
  font-size: 14px;
  font-weight: 600;
  color: #1a202c;
}

.file-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.file-input-wrapper input[type='file'] {
  cursor: pointer;
}

.file-name {
  font-size: 12px;
  color: #4a5568;
  word-break: break-all;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.form-cell {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-cell label {
  font-size: 13px;
  font-weight: 600;
  color: #1a202c;
}

.hint {
  margin: 0;
  font-size: 12px;
  color: #9ca3af;
}

.actions-section {
  border-top: 1px solid #e2e8f0;
  padding-top: 16px;
  display: flex;
}

.tool-guide {
  position: sticky;
  top: 104px;
}

.guide-card {
  border-radius: 16px;
  background: white;
  border: 1px solid #e2e8f0;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.guide-card h3 {
  margin: 0;
  font-size: 18px;
}

.guide-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.guide-step {
  display: flex;
  gap: 12px;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.step-content h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1a202c;
}

.step-content p {
  margin: 2px 0 0 0;
  color: #718096;
  font-size: 13px;
  line-height: 1.5;
}

.quick-tip {
  border-top: 1px solid #e2e8f0;
  padding-top: 12px;
}

.quick-tip h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1a202c;
}

.quick-tip p {
  margin: 6px 0 0;
  color: #718096;
  font-size: 13px;
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
