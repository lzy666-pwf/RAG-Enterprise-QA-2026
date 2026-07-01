/**
 * 认证相关API接口封装
 * 包括登录、注册、获取用户信息等功能
 */
import request from './request'

/**
 * 用户登录接口
 * @param {Object} data - 登录数据 {username, password}
 * @returns {Promise} 返回Token和用户信息
 */
export function login(data) {
  return request.post('/auth/login', data)
}

/**
 * 用户注册接口
 * @param {Object} data - 注册数据 {username, password, email}
 * @returns {Promise} 返回新用户信息
 */
export function register(data) {
  return request.post('/auth/register', data)
}

/**
 * 获取当前登录用户信息
 * @returns {Promise} 返回用户详细信息
 */
export function getCurrentUser() {
  return request.get('/auth/me')
}

/**
 * 修改密码接口
 * @param {Object} data - 密码数据 {old_password, new_password}
 * @returns {Promise} 返回操作结果
 */
export function changePassword(data) {
  return request.put('/auth/password', data)
}
