<template>
  <div class="chat-container">
    <!-- 左侧会话列表 -->
    <div class="session-sidebar">
      <div class="session-header">
        <h3>
          <el-icon><ChatLineSquare /></el-icon>
          对话列表
        </h3>
        <el-button type="primary" size="small" @click="newSession">
          <el-icon><Plus /></el-icon>
          新建
        </el-button>
      </div>

      <div class="session-list">
        <div
          v-for="item in sessions"
          :key="item.id"
          :class="['session-item', { active: currentSessionId === item.id }]"
          @click="switchSession(item.id)"
        >
          <div class="session-title">{{ item.title }}</div>
          <div class="session-meta">
            <span>{{ item.message_count || 0 }} 条消息</span>
            <span class="session-time">{{ item.updated_at }}</span>
            <el-button
              text
              type="danger"
              size="small"
              @click.stop="handleDeleteSession(item.id)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>

        <div v-if="sessions.length === 0 && !loadingSessions" class="empty-tip">
          暂无对话，点击右上角新建
        </div>
      </div>
    </div>

    <!-- 主聊天区域 -->
    <div class="chat-main">
      <div class="chat-header">
        <h2>
          <el-icon><ChatDotRound /></el-icon>
          {{ currentSessionTitle || '智能问答' }}
        </h2>
        <div class="header-actions">
          <p class="chat-tip">基于RAG技术，从企业知识库中检索相关信息生成准确答案</p>
          <el-button v-if="messages.length > 0" text type="danger" @click="clearConversation">
            <el-icon><Delete /></el-icon>
            清空当前
          </el-button>
        </div>
      </div>

      <!-- 消息列表 -->
      <div class="message-list" ref="messageListRef">
        <div v-if="loadingMessages" class="loading-messages">
          <el-icon class="is-loading"><Loading /></el-icon>
          正在加载会话消息...
        </div>

        <div v-else-if="messages.length === 0" class="empty-chat">
          <div class="empty-icon">
            <el-icon><ChatLineRound /></el-icon>
          </div>
          <h3>开始提问吧</h3>
          <p>输入您的问题，AI助手将基于知识库内容为您解答</p>
          <div class="suggest-questions">
            <el-tag
              v-for="q in suggestQuestions"
              :key="q"
              class="suggest-tag"
              @click="handleSuggest(q)"
            >
              {{ q }}
            </el-tag>
          </div>
        </div>

        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message-item', msg.role]"
        >
          <div class="message-avatar">
            <el-avatar :size="40" :class="msg.role === 'user' ? 'user-avatar' : 'ai-avatar'">
              {{ msg.role === 'user' ? userStore.username?.charAt(0)?.toUpperCase() : 'AI' }}
            </el-avatar>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(msg.content)"></div>
            <div v-if="msg.sources && msg.sources.length > 0" class="message-sources">
              <div class="sources-title">
                <el-icon><Document /></el-icon>
                参考来源
              </div>
              <div v-for="(source, idx) in msg.sources" :key="idx" class="source-item">
                <span class="source-content">{{ source.content }}</span>
                <span class="source-similarity">相似度: {{ (source.similarity * 100).toFixed(1) }}%</span>
              </div>
            </div>
            <div class="message-time">{{ msg.time }}</div>
          </div>
        </div>

        <!-- 加载中/流式输出中 -->
        <div v-if="streaming" class="message-item assistant">
          <div class="message-avatar">
            <el-avatar :size="40" class="ai-avatar">AI</el-avatar>
          </div>
          <div class="message-content">
            <div class="message-text">
              <span v-if="streamText">{{ streamText }}</span>
              <span v-else class="streaming-dots">
                <span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
              </span>
              <span class="cursor-blink">|</span>
            </div>
            <div v-if="streamSources && streamSources.length > 0" class="message-sources">
              <div class="sources-title">
                <el-icon><Document /></el-icon>
                参考来源
              </div>
              <div v-for="(source, idx) in streamSources" :key="idx" class="source-item">
                <span class="source-content">{{ source.content }}</span>
                <span class="source-similarity">相似度: {{ (source.similarity * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <div class="input-wrapper">
          <el-input
            v-model="question"
            type="textarea"
            :rows="2"
            placeholder="请输入您的问题，按Enter发送，Shift+Enter换行..."
            resize="none"
            :disabled="streaming"
            @keydown.enter.exact.prevent="handleSend"
          />
          <el-button
            type="primary"
            :loading="streaming"
            :disabled="!question.trim()"
            class="send-button"
            @click="handleSend"
          >
            <el-icon v-if="!streaming"><Promotion /></el-icon>
            <span v-if="!streaming">发送</span>
          </el-button>
        </div>
        <div class="input-tip">
          <el-icon><InfoFilled /></el-icon>
          AI会基于已入库的文档内容进行回答
        </div>
      </div>
    </div>

    <!-- 右侧知识库状态 -->
    <div class="chat-sidebar">
      <div class="sidebar-card">
        <h3>
          <el-icon><Document /></el-icon>
          知识库状态
        </h3>
        <div class="status-item">
          <span class="status-label">文档总数</span>
          <span class="status-value">{{ docStats.total }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">已入库</span>
          <span class="status-value success">{{ docStats.indexed }}</span>
        </div>
      </div>

      <div class="sidebar-card">
        <h3>
          <el-icon><Clock /></el-icon>
          快捷操作
        </h3>
        <div class="action-buttons">
          <el-button type="primary" plain @click="goToDocuments">
            <el-icon><Upload /></el-icon>
            上传文档
          </el-button>
          <el-button type="info" plain @click="goToHistory">
            <el-icon><ChatLineRound /></el-icon>
            查看历史
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 智能问答页面组件（支持多轮对话记忆 + 流式输出）
 */
import { ref, reactive, nextTick, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
import { getDocuments } from '../api/document'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import {
  getSessions,
  createSession,
  deleteSession,
  getSessionMessages,
} from '../api/chat'

const docStats = reactive({
  total: 0,
  indexed: 0,
})

const suggestQuestions = [
  '公司的上班时间是怎么规定的？',
  '年假是怎么计算的？',
  '如何申请病假？',
  '工资什么时候发放？',
]

const currentSessionTitle = ref('')
const currentController = ref(null)
const loadingMessages = ref(false)
const messages = ref([])
const question = ref('')
const sessions = ref([])
const currentSessionId = ref(null)
const streaming = ref(false)
const streamText = ref('')
const streamSources = ref([])
const loadingSessions = ref(false)
const messageListRef = ref(null)

const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

const formatMessage = (content) => {
  if (!content) return ''
  return content.replace(/\n/g, '<br>')
}

const MAX_HISTORY_ROUNDS = 3
const buildHistory = () => {
  return messages.value
    .filter((m) => m.role === 'user' || m.role === 'assistant')
    .slice(-MAX_HISTORY_ROUNDS * 2)
    .map((m) => ({
      role: m.role === 'user' ? 'user' : 'assistant',
      content: m.content,
    }))
}

const appendMessage = (role, content, sources = [], time) => {
  messages.value.push({
    role,
    content,
    sources,
    time: time || new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
  })
}

const loadSessions = async () => {
  loadingSessions.value = true
  try {
    const res = await getSessions()
    const payload = res?.data ?? res
    const list = payload?.data ?? payload
    if (Array.isArray(list)) {
      sessions.value = list.map((item) => ({
        ...item,
        updatedAt: item.updated_at
          ? new Date(item.updated_at).toLocaleString('zh-CN', {
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
            })
          : '',
      }))
      if (!currentSessionId.value && list.length) {
        currentSessionId.value = list[0].id
        currentSessionTitle.value = list[0].title || '对话'
        await loadSessionMessages(list[0].id)
        scrollToBottom()
      }
    }
  } catch (e) {
    console.error('加载会话列表失败:', e)
    sessions.value = []
  } finally {
    loadingSessions.value = false
  }
}

const loadSessionMessages = async (sessionId) => {
  try {
    const res = await getSessionMessages(sessionId)
    const payload = res?.data ?? res
    const list = payload?.data ?? payload?.messages ?? payload
    const normalized = Array.isArray(list) ? list : []
    messages.value = normalized.map((m) => {
      let sources = []
      if (Array.isArray(m.sources)) {
        sources = m.sources
      } else if (typeof m.sources === 'string' && m.sources.trim()) {
        try {
          sources = JSON.parse(m.sources)
        } catch (e) {
          sources = []
        }
      }
      return {
        role: m.role,
        content: m.content,
        sources,
        time: m.created_at
          ? new Date(m.created_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
          : '',
      }
    })
  } catch (e) {
    console.error('加载会话消息失败:', e)
    ElMessage.error('加载会话消息失败')
    messages.value = []
  }
}

const newSession = async () => {
  try {
    const res = await createSession({ title: '新对话' })
    if (res.data) {
      await loadSessions()
      const created = res.data.data || res.data
      currentSessionId.value = created.id
      currentSessionTitle.value = created.title || '新对话'
      messages.value = []
      await loadSessionMessages(created.id)
      scrollToBottom()
    }
  } catch (e) {
    ElMessage.error('创建会话失败')
  }
}

const switchSession = async (sessionId) => {
  console.log('[switchSession] clicked sessionId=', sessionId)
  if (streaming.value && currentController.value) {
    currentController.value.abort()
  }

  loadingMessages.value = true
  try {
    currentSessionId.value = sessionId
    streamText.value = ''
    streamSources.value = ''

    const item = sessions.value.find((s) => s.id === sessionId)
    console.log('[switchSession] found item=', item)
    currentSessionTitle.value = item?.title || '对话'
    await loadSessionMessages(sessionId)
  } finally {
    loadingMessages.value = false
    scrollToBottom()
  }
}

const handleDeleteSession = async (sessionId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个对话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteSession(sessionId)
    ElMessage.success('删除成功')
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = null
      currentSessionTitle.value = ''
      messages.value = []
    }
    await loadSessions()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const clearConversation = () => {
  if (streaming.value && currentController.value) {
    currentController.value.abort()
  }
  messages.value = []
  streamText.value = ''
  streamSources.value = []
}

const updateChatSession = async (sessionId, title) => {
  try {
    await updateSession(sessionId, { title })
    await loadSessions()
    if (currentSessionId.value === sessionId) {
      const item = sessions.value.find((s) => s.id === sessionId)
      currentSessionTitle.value = item?.title || title || '对话'
    }
  } catch (e) {
    console.error('更新会话标题失败:', e)
  }
}

const handleSuggest = (q) => {
  question.value = q
}

const handleSend = async () => {
  const q = question.value.trim()
  if (!q || streaming.value) return

  if (!currentSessionId.value) {
    await newSession()
  }

  appendMessage('user', q)
  question.value = ''
  streaming.value = true
  streamText.value = ''
  streamSources.value = []
  scrollToBottom()

  const history = buildHistory()
  const controller = new AbortController()
  currentController.value = controller

  let streamAccumulated = ''
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: q,
        history,
        session_id: currentSessionId.value,
      }),
      signal: controller.signal,
    })

    if (!res.ok) {
      throw new Error(`请求失败: ${res.status}`)
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let finalAnswer = ''
    let finalSources = []

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed || !trimmed.startsWith('data:')) continue

        const raw = trimmed.slice(5).trim()
        if (!raw) continue

        try {
          const data = JSON.parse(raw)
          if (data.delta) {
            streamAccumulated += data.delta
            streamText.value = streamAccumulated
            scrollToBottom()
          }
          if (data.answer) {
            finalAnswer = data.answer
          }
          if (data.sources) {
            finalSources = data.sources
          }
          if (data.doc_count !== undefined) {
            streamSources.value = finalSources
          }
        } catch (e) {
          console.error('解析流式数据失败:', e)
        }
      }
    }

    appendMessage('assistant', finalAnswer || streamAccumulated, finalSources || streamSources.value)
    streamText.value = ''
    streamSources.value = []
    if (currentSessionTitle.value === '新对话') {
      updateChatSession(currentSessionId.value, q)
    }
    loadSessions()
    scrollToBottom()
  } catch (e) {
    console.error('发起流式问答失败:', e)
    appendMessage('assistant', '抱歉，服务出现异常，请稍后重试。')
    streamText.value = ''
    streamSources.value = []
    scrollToBottom()
  } finally {
    streaming.value = false
    currentController.value = null
  }
}

const goToDocuments = () => {
  router.push('/documents')
}

const goToHistory = () => {
  router.push('/history')
}

const loadDocStats = async () => {
  try {
    const res = await getDocuments({ page: 1, page_size: 100 })
    if (res.data) {
      docStats.total = res.data.total || 0
      docStats.indexed = res.data.items?.filter((d) => d.status === 1).length || 0
    }
  } catch (error) {
    console.error('加载文档统计失败:', error)
  }
}

onMounted(async () => {
  await loadSessions()
  await loadDocStats()

  const querySessionId = route.query?.sessionId
  if (querySessionId) {
    await switchSession(Number(querySessionId))
  }
})
</script>

<style scoped>
.chat-container {
  display: flex;
  gap: 16px;
  height: calc(100vh - 108px);
}

/* 会话侧边栏 */
.session-sidebar {
  width: 240px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.session-header {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f0f0f0;
}

.session-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.session-header h3 .el-icon {
  color: #ffb800;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: background 0.2s;
}

.session-item:hover {
  background: #fafafa;
}

.session-item.active {
  background: #fff7e6;
}

.session-title {
  font-size: 14px;
  color: #333;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 12px;
  color: #999;
  gap: 6px;
}

.session-time {
  font-size: 11px;
  color: #bbb;
  white-space: nowrap;
}

.empty-tip {
  text-align: center;
  padding: 24px 8px;
  font-size: 12px;
  color: #999;
}

/* 主聊天区域 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.chat-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.chat-header h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.chat-header h2 .el-icon {
  color: #ffb800;
}

.header-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-tip {
  font-size: 14px;
  color: #999;
}

/* 消息列表 */
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.empty-chat {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #ffb800 0%, #ff9500 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

.empty-icon .el-icon {
  font-size: 40px;
  color: white;
}

.empty-chat h3 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.empty-chat p {
  font-size: 14px;
  color: #999;
  margin-bottom: 24px;
}

.suggest-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.suggest-tag {
  cursor: pointer;
  padding: 8px 16px;
  font-size: 14px;
  transition: all 0.3s;
}

.suggest-tag:hover {
  background-color: #ffb800;
  color: white;
  border-color: #ffb800;
}

/* 消息项 */
.message-item {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar .user-avatar {
  background-color: #ffb800;
  color: white;
}

.message-avatar .ai-avatar {
  background-color: #1890ff;
  color: white;
}

.message-content {
  max-width: 70%;
}

.message-item.user .message-content {
  text-align: right;
}

.message-text {
  background: #f5f5f5;
  padding: 12px 16px;
  border-radius: 12px;
  border-top-left-radius: 4px;
  line-height: 1.6;
  font-size: 14px;
  color: #333;
}

.message-item.user .message-text {
  background: #ffb800;
  color: white;
  border-radius: 12px;
  border-top-right-radius: 4px;
}

.cursor-blink {
  display: inline-block;
  width: 2px;
  height: 16px;
  background: #333;
  margin-left: 2px;
  vertical-align: middle;
  animation: blink 1s steps(1) infinite;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

.streaming-dots {
  display: inline-flex;
  gap: 2px;
  color: #999;
}

.dot {
  animation: dotPulse 1.4s infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dotPulse {
  0%, 80%, 100% {
    opacity: 0.2;
  }
  40% {
    opacity: 1;
  }
}

.message-sources {
  margin-top: 12px;
  padding: 12px;
  background: #fff8e6;
  border-radius: 8px;
  text-align: left;
}

.sources-title {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #e6a600;
  margin-bottom: 8px;
}

.source-item {
  font-size: 12px;
  color: #666;
  padding: 4px 0;
  border-bottom: 1px dashed #e6d9b8;
}

.source-item:last-child {
  border-bottom: none;
}

.source-similarity {
  color: #999;
  font-size: 11px;
  margin-left: 8px;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
}

/* 输入区域 */
.chat-input-area {
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-wrapper .el-textarea {
  flex: 1;
}

.send-button {
  height: 60px;
  padding: 0 24px;
}

.input-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

/* 侧边栏 */
.chat-sidebar {
  width: 260px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sidebar-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.sidebar-card h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.sidebar-card h3 .el-icon {
  color: #ffb800;
}

.status-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.status-item:last-child {
  border-bottom: none;
}

.status-label {
  color: #666;
  font-size: 14px;
}

.status-value {
  font-weight: 600;
  color: #333;
}

.status-value.success {
  color: #52c41a;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-buttons .el-button {
  width: 100%;
}
</style>
