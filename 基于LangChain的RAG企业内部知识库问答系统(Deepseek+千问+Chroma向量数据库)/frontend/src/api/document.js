/**
 * 文档管理相关API接口封装
 * 包括文档上传、列表查询、删除等功能
 */
import request from './request'

/**
 * 获取文档列表
 * @param {Object} params - 查询参数 {page, page_size, status, keyword}
 * @returns {Promise} 返回文档列表和分页信息
 */
export function getDocuments(params) {
  return request.get('/documents', { params })
}

/**
 * 上传文档
 * @param {FormData} formData - 表单数据，包含文件和标题
 * @returns {Promise} 返回上传结果
 */
export function uploadDocument(formData) {
  return request.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取文档详情
 * @param {Number} docId - 文档ID
 * @returns {Promise} 返回文档详细信息
 */
export function getDocument(docId) {
  return request.get(`/documents/${docId}`)
}

/**
 * 删除文档
 * @param {Number} docId - 文档ID
 * @returns {Promise} 返回删除结果
 */
export function deleteDocument(docId) {
  return request.delete(`/documents/${docId}`)
}
