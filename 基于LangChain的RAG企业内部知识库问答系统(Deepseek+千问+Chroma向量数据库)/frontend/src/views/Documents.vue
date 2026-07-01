<template>
  <div class="documents-container">
    <div class="page-header">
      <div class="header-left">
        <h2>
          <el-icon><Document /></el-icon>
          我的文档
        </h2>
        <p class="page-desc">上传和管理您的文档，构建个人知识库</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showUploadDialog">
          <el-icon><Upload /></el-icon>
          上传文档
        </el-button>
        <el-button v-if="userStore.isAdmin" type="danger" @click="handleClearVectorStore">
          <el-icon><Delete /></el-icon>
          清空向量库
        </el-button>
      </div>
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
      <el-input
        v-model="keyword"
        placeholder="搜索文档标题..."
        style="width: 300px;"
        clearable
        @clear="loadDocuments"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- 文档列表 -->
    <div class="documents-grid" v-loading="loading">
      <div v-if="documents.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无文档，请先上传文档">
          <el-button type="primary" @click="showUploadDialog">上传文档</el-button>
        </el-empty>
      </div>

      <el-card
        v-for="doc in documents"
        :key="doc.id"
        class="document-card"
        shadow="hover"
      >
        <template #header>
          <div class="card-header">
            <div class="doc-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="doc-info">
              <h4 class="doc-title">{{ doc.title }}</h4>
              <span class="doc-type">{{ getFileTypeName(doc.file_type) }}</span>
            </div>
            <el-tag :type="doc.status === 1 ? 'success' : 'warning'" size="small">
              {{ doc.status_text }}
            </el-tag>
          </div>
        </template>

        <div class="card-body">
          <div class="doc-content">
            {{ doc.content || '暂无内容摘要' }}
          </div>
          <div class="doc-meta">
            <span>
              <el-icon><User /></el-icon>
              {{ doc.uploader_name }}
            </span>
            <span>
              <el-icon><Clock /></el-icon>
              {{ doc.created_at }}
            </span>
          </div>
        </div>

        <template #footer>
          <div class="card-footer">
            <el-button text type="primary" @click="viewDetail(doc)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button 
              text 
              type="danger" 
              @click="handleDelete(doc)"
              v-if="canDelete(doc)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </template>
      </el-card>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="total > 0">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[12, 24, 36]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传文档" width="500px">
      <el-form ref="uploadFormRef" :model="uploadForm" :rules="uploadRules">
        <el-form-item label="文档标题" prop="title">
          <el-input v-model="uploadForm.title" placeholder="请输入文档标题（可选）" />
        </el-form-item>
        <el-form-item label="选择文件" prop="file">
          <el-upload
            ref="uploadRef"
            class="upload-demo"
            drag
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".txt,.pdf,.docx,.doc"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 TXT、PDF、DOCX 格式，单个文件不超过16MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">上传</el-button>
      </template>
    </el-dialog>

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
          <el-descriptions-item label="上传时间">{{ currentDoc.created_at }}</el-descriptions-item>
        </el-descriptions>
        <div class="content-preview">
          <h4>内容预览</h4>
          <div class="preview-text">{{ currentDoc.content || '暂无内容' }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 我的文档页面组件
 * 展示系统中所有文档（共享），支持上传、查看详情和删除
 */
import { ref, onMounted } from 'vue'
import { getDocuments, uploadDocument, deleteDocument } from '../api/document'
import { clearVectorStore, getVectorStatus } from '../api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

const loading = ref(false)
const documents = ref([])
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)
const keyword = ref('')

// 向量库状态
const statusLoading = ref(false)
const vectorStatus = ref({
  collection_name: 'documents',
  vector_count: 0,
  all_collections: []
})

// 上传相关
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const uploadFormRef = ref(null)
const uploadRef = ref(null)
const uploadForm = ref({
  title: '',
  file: null
})

const uploadRules = {
  file: [{ required: true, message: '请选择文件', trigger: 'change' }]
}

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
 * 判断当前用户是否有权限删除该文档
 */
const canDelete = (doc) => {
  // 管理员可以删除所有，普通用户只能删除自己的
  return userStore.isAdmin || doc.user_id === userStore.user?.id
}

/**
 * 加载文档列表（所有用户共享）
 */
const loadDocuments = async () => {
  loading.value = true
  try {
    const res = await getDocuments({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value
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
 * 显示上传对话框
 */
const showUploadDialog = () => {
  uploadForm.value = { title: '', file: null }
  uploadDialogVisible.value = true
}

/**
 * 文件选择变化
 */
const handleFileChange = (file) => {
  uploadForm.value.file = file.raw
  // 如果标题为空，使用文件名
  if (!uploadForm.value.title) {
    uploadForm.value.title = file.name.replace(/\.[^/.]+$/, '')
  }
}

/**
 * 文件移除
 */
const handleFileRemove = () => {
  uploadForm.value.file = null
}

/**
 * 执行上传
 */
const handleUpload = async () => {
  if (!uploadForm.value.file) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadForm.value.file)
    if (uploadForm.value.title) {
      formData.append('title', uploadForm.value.title)
    }

    const res = await uploadDocument(formData)
    if (res.data) {
      ElMessage.success(res.data.msg || '上传成功')
    } else {
      ElMessage.success('上传成功')
    }
    uploadDialogVisible.value = false
    loadDocuments()
    loadVectorStatus()
  } catch (error) {
    console.error('上传失败:', error)
    if (error?.response?.data?.msg) {
      ElMessage.error(error.response.data.msg)
    } else {
      ElMessage.error('上传失败')
    }
  } finally {
    uploading.value = false
  }
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
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败')
    }
  }
}

/**
 * 获取文件类型名称
 */
const getFileTypeName = (type) => {
  const typeMap = {
    'txt': '文本文件',
    'pdf': 'PDF文档',
    'docx': 'Word文档',
    'doc': 'Word文档'
  }
  return typeMap[type] || type || '未知类型'
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
.documents-container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 60px;
  background: white;
  border-radius: 12px;
}

.document-card {
  transition: transform 0.3s, box-shadow 0.3s;
}

.document-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.doc-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #FFB800 0%, #FF9500 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.doc-icon .el-icon {
  font-size: 24px;
  color: white;
}

.doc-info {
  flex: 1;
}

.doc-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-type {
  font-size: 12px;
  color: #999;
}

.card-body {
  padding: 0 4px;
}

.doc-content {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  height: 60px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  margin-bottom: 12px;
}

.doc-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #999;
}

.doc-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
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

.upload-demo {
  width: 100%;
}

.el-icon--upload {
  font-size: 67px;
  color: #FFB800;
  margin-bottom: 16px;
}
</style>
