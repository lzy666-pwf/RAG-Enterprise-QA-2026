<template>
  <div class="history-container">
    <div class="page-header">
      <h2>
        <el-icon><ChatLineSquare /></el-icon>
        问答历史
      </h2>
      <p class="page-desc">查看和管理您的问答记录</p>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-bar">
      <el-input
        v-model="keyword"
        placeholder="搜索问答内容..."
        style="width: 300px;"
        clearable
        @clear="loadHistory"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" @click="loadHistory">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>
    </div>

    <!-- 问答列表 -->
    <div class="history-list" v-loading="loading">
      <div v-if="historyList.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无问答记录" />
      </div>

      <el-card
        v-for="item in historyList"
        :key="item.id"
        class="history-card"
        shadow="hover"
      >
        <template #header>
          <div class="card-header">
            <div class="user-info">
              <el-avatar :size="32">{{ item.user_name?.charAt(0)?.toUpperCase() }}</el-avatar>
              <span class="username">{{ item.user_name }}</span>
              <el-tag size="small" type="info">{{ item.created_at }}</el-tag>
            </div>
            <div class="actions">
              <el-button text type="primary" @click="viewDetail(item)">
                <el-icon><View /></el-icon>
                查看
              </el-button>
              <el-button text type="danger" @click="handleDelete(item.id)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>
        </template>

        <div class="card-content">
          <div class="question">
            <div class="label">
              <el-icon><QuestionFilled /></el-icon>
              问题
            </div>
            <div class="content">{{ item.question }}</div>
          </div>

          <div class="answer">
            <div class="label">
              <el-icon><ChatDotSquare /></el-icon>
              回答
            </div>
            <div class="content">{{ item.answer }}</div>
          </div>

          <div v-if="item.sources && item.sources.length > 0" class="sources">
            <div class="label">
              <el-icon><Document /></el-icon>
              参考来源 ({{ item.sources.length }})
            </div>
            <div class="source-tags">
              <el-tag
                v-for="(source, idx) in item.sources"
                :key="idx"
                size="small"
                type="warning"
              >
                {{ source.content?.substring(0, 30) }}...
              </el-tag>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="total > 0">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="问答详情" width="700px">
      <div v-if="currentItem" class="detail-content">
        <div class="detail-item">
          <div class="detail-label">问题</div>
          <div class="detail-value question-value">{{ currentItem.question }}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label">回答</div>
          <div class="detail-value answer-value">{{ currentItem.answer }}</div>
        </div>
        <div v-if="currentItem.sources && currentItem.sources.length > 0" class="detail-item">
          <div class="detail-label">参考来源</div>
          <div class="detail-value">
            <div v-for="(source, idx) in currentItem.sources" :key="idx" class="source-detail">
              <el-tag type="warning" size="small">来源 {{ idx + 1 }}</el-tag>
              <span>{{ source.content }}</span>
              <span class="similarity">相似度: {{ (source.similarity * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>
        <div class="detail-meta">
          <span>提问时间: {{ currentItem.created_at }}</span>
          <span>提问用户: {{ currentItem.user_name }}</span>
        </div>
        <div class="detail-actions">
          <el-button type="primary" @click="continueConversation(currentItem)">
            <el-icon><ChatDotRound /></el-icon>
            继续对话
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 问答历史页面组件
 * 展示用户的问答历史记录，支持查看详情、删除和继续对话
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getChatHistory, deleteChat } from '../api/chat'
import { createSession, addSessionMessage } from '../api/chat'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

const loading = ref(false)
const historyList = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const keyword = ref('')

const detailVisible = ref(false)
const currentItem = ref(null)

/**
 * 加载历史记录
 */
const loadHistory = async () => {
  loading.value = true
  try {
    const res = await getChatHistory({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value
    })
    if (res.data) {
      historyList.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 继续对话：把当前问答记录写入一个会话，然后跳转到聊天页
 */
const continueConversation = async (item) => {
  try {
    const sessionRes = await createSession({ title: item.question.slice(0, 50) })
    const created = sessionRes?.data?.data || sessionRes?.data || {}

    await addSessionMessage(created.id, {
      role: 'user',
      content: item.question,
    })
    await addSessionMessage(created.id, {
      role: 'assistant',
      content: item.answer,
      sources: item.sources || [],
    })

    router.push({
      path: '/chat',
      query: {
        sessionId: created.id,
      },
    })
  } catch (error) {
    ElMessage.error('继续对话失败，请稍后重试')
  }
}

/**
 * 查看详情
 */
const viewDetail = (item) => {
  currentItem.value = item
  detailVisible.value = true
}

/**
 * 删除记录
 */
const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条问答记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteChat(id)
    ElMessage.success('删除成功')
    loadHistory()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

/**
 * 分页大小改变
 */
const handleSizeChange = () => {
  page.value = 1
  loadHistory()
}

/**
 * 页码改变
 */
const handlePageChange = () => {
  loadHistory()
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history-container {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.page-header h2 .el-icon {
  color: #FFB800;
}

.page-desc {
  color: #999;
  font-size: 14px;
  margin-left: 32px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-state {
  padding: 60px;
  background: white;
  border-radius: 12px;
}

.history-card {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info .el-avatar {
  background-color: #FFB800;
  color: white;
}

.username {
  font-weight: 500;
  color: #333;
}

.actions {
  display: flex;
  gap: 8px;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question, .answer, .sources {
  padding: 12px;
  background: #FAFAFA;
  border-radius: 8px;
}

.label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #666;
  margin-bottom: 8px;
}

.question .el-icon {
  color: #FFB800;
}

.answer .el-icon {
  color: #52C41A;
}

.sources .el-icon {
  color: #FAAD14;
}

.content {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}

.source-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-label {
  font-size: 14px;
  font-weight: 600;
  color: #666;
}

.detail-value {
  font-size: 14px;
  color: #333;
  line-height: 1.8;
  padding: 12px;
  background: #FAFAFA;
  border-radius: 8px;
}

.question-value {
  border-left: 3px solid #FFB800;
}

.answer-value {
  border-left: 3px solid #52C41A;
}

.source-detail {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px dashed #E6E6E6;
}

.source-detail:last-child {
  border-bottom: none;
}

.similarity {
  color: #999;
  font-size: 12px;
  margin-left: auto;
}

.detail-meta {
  display: flex;
  gap: 24px;
  font-size: 12px;
  color: #999;
  padding-top: 12px;
  border-top: 1px solid #E6E6E6;
}

.detail-actions {
  display: flex;
  justify-content: flex-end;
}
</style>
