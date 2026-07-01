/**
 * 用户状态管理模块
 * 使用Pinia管理用户登录状态、Token等信息
 */
import { defineStore } from 'pinia'
import { login as apiLogin, register as apiRegister, getCurrentUser, changePassword as apiChangePassword } from '../api/auth'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', {
  state: () => ({
    // 用户信息
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    // 登录令牌
    token: localStorage.getItem('token') || '',
    // 是否已登录
    isLoggedIn: !!localStorage.getItem('token')
  }),

  getters: {
    // 获取用户角色
    userRole: (state) => state.user?.role || 'user',
    // 判断是否为管理员
    isAdmin: (state) => state.user?.role === 'admin',
    // 获取用户名
    username: (state) => state.user?.username || ''
  },

  actions: {
    /**
     * 用户登录
     * @param {Object} credentials - 登录凭证 {username, password}
     */
    async login(credentials) {
      try {
        const res = await apiLogin(credentials)
        // 保存Token和用户信息到本地存储
        this.token = res.data.token
        this.user = res.data.user
        this.isLoggedIn = true
        localStorage.setItem('token', res.data.token)
        localStorage.setItem('user', JSON.stringify(res.data.user))
        ElMessage.success('登录成功')
        return true
      } catch (error) {
        return false
      }
    },

    /**
     * 用户注册
     * @param {Object} data - 注册数据 {username, password, email}
     */
    async register(data) {
      try {
        await apiRegister(data)
        ElMessage.success('注册成功，请登录')
        return true
      } catch (error) {
        return false
      }
    },

    /**
     * 刷新当前用户信息
     */
    async fetchCurrentUser() {
      try {
        const res = await getCurrentUser()
        this.user = res.data
        localStorage.setItem('user', JSON.stringify(res.data))
      } catch (error) {
        this.logout()
      }
    },

    /**
     * 修改密码
     * @param {Object} data - 密码数据 {old_password, new_password}
     */
    async changePassword(data) {
      try {
        await apiChangePassword(data)
        ElMessage.success('密码修改成功')
        return true
      } catch (error) {
        return false
      }
    },

    /**
     * 用户登出
     */
    logout() {
      this.user = null
      this.token = ''
      this.isLoggedIn = false
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      ElMessage.info('已退出登录')
    }
  }
})
