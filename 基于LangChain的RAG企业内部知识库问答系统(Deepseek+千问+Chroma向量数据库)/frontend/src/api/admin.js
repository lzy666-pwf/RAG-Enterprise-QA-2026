/**
 * 管理员相关API接口封装
 * 包括统计数据、用户管理、文档管理等管理员功能
 */
import request from './request'

/**
 * 获取管理后台统计数据
 * @returns {Promise} 返回统计数据概览
 */
export function getStats() {
  return request.get('/admin/stats')
}

/**
 * 获取用户列表（管理员）
 * @param {Object} params - 查询参数 {page, page_size, keyword}
 * @returns {Promise} 返回用户列表和分页信息
 */
export function getUsers(params) {
  return request.get('/admin/users', { params })
}

/**
 * 更新用户信息（管理员）
 * @param {Number} userId - 用户ID
 * @param {Object} data - 更新数据 {role}
 * @returns {Promise} 返回操作结果
 */
export function updateUser(userId, data) {
  return request.put(`/admin/users/${userId}`, data)
}

/**
 * 删除用户（管理员）
 * @param {Number} userId - 用户ID
 * @returns {Promise} 返回删除结果
 */
export function deleteUser(userId) {
  return request.delete(`/admin/users/${userId}`)
}

/**
 * 获取所有文档列表（管理员）
 * @param {Object} params - 查询参数 {page, page_size, status}
 * @returns {Promise} 返回文档列表和分页信息
 */
export function getAdminDocuments(params) {
  return request.get('/admin/documents', { params })
}

/**
 * 获取所有问答记录（管理员）
 * @param {Object} params - 查询参数 {page, page_size}
 * @returns {Promise} 返回问答记录列表和分页信息
 */
export function getAdminChats(params) {
  return request.get('/admin/chats', { params })
}

/**
 * 获取向量库状态（管理员）
 * @returns {Promise} 返回向量库状态
 */
export function getVectorStatus() {
  return request.get('/admin/vectors/status')
}

/**
 * 清空向量库（管理员）
 * @returns {Promise} 返回清空结果
 */
export function clearVectorStore() {
  return request.post('/admin/vectors/clear')
}

/**
 * 删除文档（管理员）
 * @param {Number} docId - 文档ID
 * @returns {Promise} 返回删除结果
 */
export function deleteDocument(docId) {
  return request.delete(`/admin/documents/${docId}`)
}
