<template>
  <div class="admin-chats-container">
    <div class="page-header">
      <h2>
        <el-icon><ChatLineSquare /></el-icon>
        问答记录
      </h2>
      <p class="page-desc">查看所有用户的问答记录，了解知识库使用情况</p>
    </div>

    <!-- 问答列表 -->
    <el-card v-loading="loading">
      <el-table :data="chats" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user_name" label="提问用户" width="120">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="28">{{ row.user_name?.charAt(0)?.toUpperCase() }}</el-avatar>
              <span>{{ row.user_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="question" label="问题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="answer" label="回答" min-width="300" show-overflow-tooltip />
        <el-table-column prop="created_at" label="提问时间" min-width="180" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="viewDetail(row)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="问答详情" width="700px">
      <div v-if="currentChat" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="提问用户">{{ currentChat.user_name }}</el-descriptions-item>
          <el-descriptions-item label="提问时间">{{ currentChat.created_at }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-label">
            <el-icon><QuestionFilled /></el-icon>
            问题
          </div>
          <div class="section-value question-value">{{ currentChat.question }}</div>
        </div>

        <div class="detail-section">
          <div class="section-label">
            <el-icon><ChatDotSquare /></el-icon>
            AI回答
          </div>
          <div class="section-value answer-value">{{ currentChat.answer }}</div>
        </div>

        <div v-if="currentChat.sources && currentChat.sources.length > 0" class="detail-section">
          <div class="section-label">
            <el-icon><Document /></el-icon>
            参考来源 ({{ currentChat.sources.length }})
          </div>
          <div class="sources-list">
            <div v-for="(source, idx) in currentChat.sources" :key="idx" class="source-item">
              <el-tag type="warning" size="small">来源 {{ idx + 1 }}</el-tag>
              <span class="source-content">{{ source.content }}</span>
              <span class="similarity">相似度: {{ (source.similarity * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 管理员问答记录页面组件
 * 展示系统中所有用户的问答记录，支持查看详情
 */
import { ref, onMounted } from 'vue'
import { getAdminChats } from '../../api/admin'

const loading = ref(false)
const chats = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 详情相关
const detailVisible = ref(false)
const currentChat = ref(null)

/**
 * 加载问答记录
 */
const loadChats = async () => {
  loading.value = true
  try {
    const res = await getAdminChats({
      page: page.value,
      page_size: pageSize.value
    })
    if (res.data) {
      chats.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error('加载问答记录失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 查看详情
 */
const viewDetail = (chat) => {
  currentChat.value = chat
  detailVisible.value = true
}

/**
 * 分页大小改变
 */
const handleSizeChange = () => {
  page.value = 1
  loadChats()
}

/**
 * 页码改变
 */
const handlePageChange = () => {
  loadChats()
}

onMounted(() => {
  loadChats()
})
</script>

<style scoped>
.admin-chats-container {
  max-width: 1400px;
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

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-cell .el-avatar {
  background-color: #FFB800;
  color: white;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
  color: #666;
}

.section-label .el-icon {
  color: #FFB800;
}

.section-value {
  padding: 12px;
  background: #FAFAFA;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.8;
}

.question-value {
  border-left: 3px solid #FFB800;
}

.answer-value {
  border-left: 3px solid #52C41A;
}

.sources-list {
  background: #FFF8E6;
  padding: 12px;
  border-radius: 8px;
}

.source-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px dashed #E6D9B8;
}

.source-item:last-child {
  border-bottom: none;
}

.source-content {
  flex: 1;
  font-size: 13px;
  color: #666;
}

.similarity {
  color: #999;
  font-size: 12px;
}
</style>
