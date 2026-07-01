<template>
  <div class="admin-docs-container">
    <div class="page-header">
      <h2>
        <el-icon><Document /></el-icon>
        文档管理
      </h2>
      <p class="page-desc">管理系统中的所有文档，查看文档入库状态</p>
    </div>

    <!-- 向量库状态 -->
    <el-card class="status-card" v-loading="statusLoading">
      <div class="status-header">
        <span class="status-title">向量库状态</span>
        <el-button size="small" @click="loadVectorStatus">
          <el-icon><Refresh /></el-icon>
          刷新状态
        </el-button>
      </div>
      <div class="status-body">
        <div class="status-item">
          <span class="status-label">集合名称</span>
          <span class="status-value">{{ vectorStatus.collection_name || '-' }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">向量数量</span>
          <el-tag :type="vectorStatus.vector_count > 0 ? 'success' : 'warning'">
            {{ vectorStatus.vector_count }}
          </el-tag>
        </div>
        <div class="status-item">
          <span class="status-label">所有集合</span>
          <span class="status-value">{{ vectorStatus.all_collections && vectorStatus.all_collections.length ? vectorStatus.all_collections.join(', ') : '-' }}</span>
        </div>
      </div>
    </el-card>

    <!-- 筛选区域 -->
    <div class="filter-bar">
      <el-button type="primary" @click="loadDocuments">
        <el-icon><Refresh /></el-icon>
        刷新文档
      </el-button>
      <el-button type="danger" @click="handleClearVectorStore">
        <el-icon><Delete /></el-icon>
        清空向量库
      </el-button>
    </div>

    <!-- 文档列表 -->
    <el-card v-loading="loading">
      <el-table :data="documents" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="文档标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="file_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ getFileTypeName(row.file_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'warning'" size="small">
              {{ row.status_text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="uploader_name" label="上传人" width="120" />
        <el-table-column prop="created_at" label="上传时间" min-width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="viewDetail(row)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button text type="danger" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
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
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="文档详情" width="600px">
      <div v-if="currentDoc" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文档标题">{{ currentDoc.title }}</el-descriptions-item>
          <el-descriptions-item label="文件类型">{{ getFileTypeName(currentDoc.file_type) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentDoc.status === 1 ? 'success' : 'warning'" size="small">
              {{ currentDoc.status_text }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="上传人">{{ currentDoc.uploader_name }}</el-descriptions-item>
          <el-descriptions-item label="上传时间" :span="2">{{ currentDoc.created_at }}</el-descriptions-item>
        </el-descriptions>
        <div class="content-preview">
          <h4>内容摘要</h4>
          <div class="preview-text">{{ currentDoc.content || '暂无内容摘要' }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 管理员文档管理页面组件
 * 展示系统中所有文档，支持查看详情和删除，展示向量库真实状态
 */
import { ref, onMounted } from 'vue'
import { getAdminDocuments, deleteDocument, clearVectorStore, getVectorStatus } from '../../api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const documents = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 向量库状态
const statusLoading = ref(false)
const vectorStatus = ref({
  collection_name: 'documents',
  vector_count: 0,
  all_collections: []
})

// 详情相关
const detailVisible = ref(false)
const currentDoc = ref(null)

/**
 * 加载向量库状态
 */
const loadVectorStatus = async () => {
  statusLoading.value = true
  try {
    const res = await getVectorStatus()
    if (res.data) {
      vectorStatus.value = res.data.data || vectorStatus.value
    }
  } catch (error) {
    console.error('加载向量库状态失败:', error)
  } finally {
    statusLoading.value = false
  }
}

/**
 * 加载文档列表
 */
const loadDocuments = async () => {
  loading.value = true
  try {
    const res = await getAdminDocuments({
      page: page.value,
      page_size: pageSize.value
    })
    if (res.data) {
      documents.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error('加载文档列表失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 获取文件类型名称
 */
const getFileTypeName = (type) => {
  const typeMap = {
    'txt': '文本',
    'pdf': 'PDF',
    'docx': 'Word',
    'doc': 'Word'
  }
  return typeMap[type] || type || '未知'
}

/**
 * 查看详情
 */
const viewDetail = (doc) => {
  currentDoc.value = doc
  detailVisible.value = true
}

/**
 * 删除文档
 */
const handleDelete = async (doc) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档 "${doc.title}" 吗？删除后将同步删除向量库中的数据。`,
      '警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await deleteDocument(doc.id)
    ElMessage.success('删除成功')
    loadDocuments()
    loadVectorStatus()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

/**
 * 清空向量库
 */
const handleClearVectorStore = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空向量库吗？清空后需要重新上传文档才能进行问答。',
      '警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await clearVectorStore()
    ElMessage.success('向量库已清空')
    loadVectorStatus()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败')
    }
  }
}

/**
 * 分页大小改变
 */
const handleSizeChange = () => {
  page.value = 1
  loadDocuments()
}

/**
 * 页码改变
 */
const handlePageChange = () => {
  loadDocuments()
}

onMounted(() => {
  loadDocuments()
  loadVectorStatus()
})
</script>

<style scoped>
.admin-docs-container {
  max-width: 1200px;
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

.status-card {
  margin-bottom: 20px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.status-title {
  font-weight: 600;
}

.status-body {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.status-label {
  font-size: 12px;
  color: #999;
}

.status-value {
  font-size: 14px;
  color: #333;
  word-break: break-all;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.content-preview h4 {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin-bottom: 8px;
}

.preview-text {
  font-size: 14px;
  color: #333;
  line-height: 1.8;
  padding: 12px;
  background: #FAFAFA;
  border-radius: 8px;
  max-height: 200px;
  overflow-y: auto;
}
</style>
