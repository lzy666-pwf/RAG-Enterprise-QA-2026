/**
 * 问答聊天相关API接口封装
 * 包括智能问答、会话管理、历史记录查询等功能
 */
import request from './request'

/**
 * 提交问答（非流式，兼容旧版）
 */
export function askQuestion(data) {
  return request.post('/chat', data)
}

/**
 * 创建会话
 */
export function createSession(data = {}) {
  return request.post('/sessions', data)
}

/**
 * 更新会话（如自动回填标题）
 */
export function updateSession(sessionId, data) {
  return request.patch(`/sessions/${sessionId}`, data)
}

/**
 * 获取会话列表
 */
export function getSessions() {
  return request.get('/sessions')
}

/**
 * 获取会话详情
 */
export function getSessionDetail(sessionId) {
  return request.get(`/sessions/${sessionId}`)
}

/**
 * 删除会话
 */
export function deleteSession(sessionId) {
  return request.delete(`/sessions/${sessionId}`)
}

/**
 * 获取会话消息
 */
export function getSessionMessages(sessionId) {
  return request.get(`/sessions/${sessionId}/messages`)
}

/**
 * 追加会话消息（用于继续旧对话）
 */
export function addSessionMessage(sessionId, data) {
  return request.post(`/sessions/${sessionId}/messages`, data)
}

/**
 * 获取问答历史记录
 */
export function getChatHistory(params) {
  return request.get('/chat/history', { params })
}

/**
 * 获取单条问答详情
 */
export function getChatDetail(chatId) {
  return request.get(`/chat/${chatId}`)
}

/**
 * 删除问答记录
 */
export function deleteChat(chatId) {
  return request.delete(`/chat/${chatId}`)
}
