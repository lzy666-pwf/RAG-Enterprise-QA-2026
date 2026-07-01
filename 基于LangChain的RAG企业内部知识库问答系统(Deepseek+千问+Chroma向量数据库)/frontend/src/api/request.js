/**
 * Axios HTTP请求封装模块
 * 统一处理请求拦截、响应拦截和错误处理
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

// 创建axios实例，配置基础URL和超时时间
const service = axios.create({
  baseURL: '/api',
  timeout: 60000  // 1分钟超时
})

// 请求拦截器：自动添加Token到请求头
service.interceptors.request.use(
  config => {
    // 从localStorage获取Token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器：统一处理错误和Token失效
service.interceptors.response.use(
  response => {
    const res = response.data

    // 根据业务码判断请求是否成功
    if (res.code !== 200) {
      ElMessage.error(res.msg || '请求失败')
      return Promise.reject(new Error(res.msg || '请求失败'))
    }

    return res
  },
  error => {
    // 处理HTTP错误状态码
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Token过期或无效，跳转登录页
          ElMessage.error('登录已过期，请重新登录')
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          router.push('/login')
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          // 业务层错误码(400等)不自动登出，只显示错误消息
          const msg = error.response.data?.msg
          if (msg) {
            ElMessage.error(msg)
          }
      }
    } else if (error.message.includes('timeout')) {
      ElMessage.error('请求超时，请稍后重试')
    } else {
      ElMessage.error('网络连接失败')
    }
    return Promise.reject(error)
  }
)

export default service
