<template>
  <div class="login-container">
    <!-- 左侧装饰区域 -->
    <div class="login-left">
      <div class="left-content">
        <h1 class="logo">企业知识库</h1>
        <h2 class="subtitle">智能问答系统</h2>
        <p class="description">基于RAG技术的企业内部知识库智能问答平台，助您快速获取所需信息</p>
        <div class="features">
          <div class="feature-item">
            <el-icon><ChatDotRound /></el-icon>
            <span>智能问答</span>
          </div>
          <div class="feature-item">
            <el-icon><Document /></el-icon>
            <span>文档管理</span>
          </div>
          <div class="feature-item">
            <el-icon><DataLine /></el-icon>
            <span>数据统计</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录表单区域 -->
    <div class="login-right">
      <div class="login-box">
        <h2 class="login-title">用户登录</h2>
        <el-form
          ref="formRef"
          :model="loginForm"
          :rules="rules"
          class="login-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              size="large"
              prefix-icon="User"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="login-button"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-footer">
          <span>还没有账号？</span>
          <router-link to="/register" class="register-link">立即注册</router-link>
        </div>

        <!-- 演示账号提示 -->
        <div class="demo-hint">
          <el-alert type="info" :closable="false">
            <template #title>
              <span>演示账号：admin / 123456</span>
            </template>
          </el-alert>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 登录页面组件
 * 提供用户登录功能，支持表单验证和错误提示
 */
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

// 表单引用
const formRef = ref(null)
// 加载状态
const loading = ref(false)

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 个字符', trigger: 'blur' }
  ]
}

/**
 * 处理登录提交
 */
const handleLogin = async () => {
  // 表单验证
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const success = await userStore.login(loginForm)
    if (success) {
      // 根据用户角色跳转
      const redirectPath = userStore.isAdmin ? '/admin/home' : '/home'
      router.push(redirectPath)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  width: 100%;
  height: 100vh;
}

/* 左侧装饰区域 */
.login-left {
  flex: 1;
  background: linear-gradient(135deg, #FFB800 0%, #FF9500 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.login-left::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
  animation: pulse 8s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.3; }
}

.left-content {
  text-align: center;
  color: white;
  z-index: 1;
  padding: 40px;
}

.logo {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 16px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.subtitle {
  font-size: 28px;
  font-weight: 400;
  margin-bottom: 24px;
  opacity: 0.95;
}

.description {
  font-size: 16px;
  line-height: 1.8;
  max-width: 400px;
  margin: 0 auto 40px;
  opacity: 0.9;
}

.features {
  display: flex;
  gap: 32px;
  justify-content: center;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
}

.feature-item .el-icon {
  font-size: 24px;
}

/* 右侧登录表单区域 */
.login-right {
  width: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
}

.login-box {
  width: 320px;
  padding: 40px;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  text-align: center;
  margin-bottom: 32px;
}

.login-form {
  margin-bottom: 24px;
}

.login-button {
  width: 100%;
  font-size: 16px;
  height: 44px;
}

.login-footer {
  text-align: center;
  color: #666;
}

.register-link {
  color: #FFB800;
  text-decoration: none;
  margin-left: 8px;
  font-weight: 500;
}

.register-link:hover {
  color: #E6A600;
  text-decoration: underline;
}

.demo-hint {
  margin-top: 24px;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .login-left {
    display: none;
  }
  .login-right {
    width: 100%;
  }
}
</style>
