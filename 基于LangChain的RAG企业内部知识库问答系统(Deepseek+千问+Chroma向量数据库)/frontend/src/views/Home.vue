<template>
  <div class="home-container">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="welcome-title">
          欢迎回来，{{ userStore.username }}
        </h1>
        <p class="welcome-desc">企业知识库智能问答平台，让信息获取更高效</p>
      </div>
      <div class="quick-actions">
        <el-button type="primary" size="large" @click="goToChat">
          <el-icon><ChatDotRound /></el-icon>
          开始问答
        </el-button>
        <el-button size="large" @click="goToDocuments">
          <el-icon><Upload /></el-icon>
          上传文档
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card clickable" @click="goToDocuments">
          <div class="stat-icon" style="background: #FFF8E6;">
            <el-icon style="color: #FFB800;"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.docCount }}</div>
            <div class="stat-label">我的文档</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card clickable" @click="goToHistory">
          <div class="stat-icon" style="background: #E8F4FF;">
            <el-icon style="color: #1890FF;"><ChatDotRound /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.chatCount }}</div>
            <div class="stat-label">问答记录</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card clickable" @click="goToDocuments">
          <div class="stat-icon" style="background: #F0FFF4;">
            <el-icon style="color: #52C41A;"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.indexedCount }}</div>
            <div class="stat-label">已入库</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 最近问答 -->
    <div class="section-card">
      <div class="section-header">
        <h3><el-icon><ChatLineSquare /></el-icon> 最近问答</h3>
        <el-button text type="primary" @click="goToHistory">查看更多</el-button>
      </div>
      <div class="recent-list" v-if="recentChats.length > 0">
        <div v-for="chat in recentChats" :key="chat.id" class="recent-item" @click="goToChat">
          <div class="recent-question">
            <el-icon><QuestionFilled /></el-icon>
            {{ chat.question }}
          </div>
          <div class="recent-answer">{{ chat.answer }}</div>
          <div class="recent-time">{{ chat.created_at }}</div>
        </div>
      </div>
      <el-empty v-else description="暂无问答记录，试试提问吧！" />
    </div>

    <!-- 功能介绍 -->
    <el-row :gutter="20" class="features-row">
      <el-col :span="8">
        <div class="feature-card clickable" @click="goToChat">
          <div class="feature-icon">
            <el-icon><ChatLineRound /></el-icon>
          </div>
          <h4>智能问答</h4>
          <p>基于RAG技术，精准理解问题，从企业知识库中检索相关内容生成准确答案</p>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="feature-card clickable" @click="goToDocuments">
          <div class="feature-icon">
            <el-icon><Document /></el-icon>
          </div>
          <h4>文档管理</h4>
          <p>支持上传TXT、PDF、DOCX格式文档，自动解析入库，构建专属知识库</p>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="feature-card clickable" @click="goToAdmin">
          <div class="feature-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <h4>数据统计</h4>
          <p>实时统计问答数据，了解知识库使用情况，优化知识管理策略</p>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
/**
 * 用户首页组件
 * 展示欢迎信息、统计数据、最近问答等内容
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import request from '../api/request'

const router = useRouter()
const userStore = useUserStore()

// 统计数据
const stats = ref({
  docCount: 0,
  chatCount: 0,
  indexedCount: 0
})

// 最近问答
const recentChats = ref([])

/**
 * 加载统计数据
 */
const loadStats = async () => {
  try {
    const res = await request.get('/stats')
    if (res.data) {
      stats.value.docCount = res.data.docCount || 0
      stats.value.indexedCount = res.data.indexedCount || 0
      stats.value.chatCount = res.data.chatCount || 0
      recentChats.value = res.data.recentChats || []
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

/**
 * 跳转到问答页面
 */
const goToChat = () => {
  router.push('/chat')
}

/**
 * 跳转到文档页面
 */
const goToDocuments = () => {
  router.push('/documents')
}

/**
 * 跳转到历史记录页面
 */
const goToHistory = () => {
  router.push('/history')
}

/**
 * 跳转到管理后台
 */
const goToAdmin = () => {
  router.push('/admin')
}

// 组件挂载时加载数据
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* 欢迎区域 */
.welcome-section {
  background: linear-gradient(135deg, #FFB800 0%, #FF9500 100%);
  border-radius: 12px;
  padding: 40px;
  color: white;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 8px;
}

.welcome-desc {
  font-size: 16px;
  opacity: 0.9;
}

.quick-actions {
  display: flex;
  gap: 12px;
}

.quick-actions .el-button {
  padding: 12px 24px;
  font-size: 16px;
}

.quick-actions .el-button--primary {
  background: white;
  color: #FFB800;
  border-color: white;
}

.quick-actions .el-button--primary:hover {
  background: #FFF8E6;
  color: #E6A600;
}

.quick-actions .el-button:not(.el-button--primary) {
  background: transparent;
  color: white;
  border-color: rgba(255, 255, 255, 0.5);
}

.quick-actions .el-button:not(.el-button--primary):hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: white;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card.clickable:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-card:not(.clickable):hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon .el-icon {
  font-size: 28px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}

/* 区域卡片 */
.section-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.section-header .el-icon {
  color: #FFB800;
}

/* 最近问答列表 */
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recent-item {
  padding: 16px;
  background: #FAFAFA;
  border-radius: 8px;
  border-left: 3px solid #FFB800;
  cursor: pointer;
  transition: all 0.2s;
}

.recent-item:hover {
  background: #FFF8E6;
  border-left-color: #E6A600;
}

.recent-question {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.recent-question .el-icon {
  color: #FFB800;
}

.recent-answer {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.recent-time {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

/* 功能介绍 */
.features-row {
  margin-bottom: 24px;
}

.feature-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card.clickable {
  cursor: pointer;
}

.feature-card.clickable:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #FFB800 0%, #FF9500 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.feature-icon .el-icon {
  font-size: 32px;
  color: white;
}

.feature-card h4 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.feature-card p {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}
</style>
