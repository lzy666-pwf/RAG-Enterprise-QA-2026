<template>
  <div class="users-container">
    <div class="page-header">
      <h2>
        <el-icon><User /></el-icon>
        用户管理
      </h2>
      <p class="page-desc">管理系统用户，查看用户信息和修改用户角色</p>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-bar">
      <el-input
        v-model="keyword"
        placeholder="搜索用户名..."
        style="width: 300px;"
        clearable
        @clear="loadUsers"
        @keyup.enter="loadUsers"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" @click="loadUsers">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>
    </div>

    <!-- 用户列表 -->
    <el-card v-loading="loading">
      <el-table :data="users" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" min-width="120">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="36">{{ row.username?.charAt(0)?.toUpperCase() }}</el-avatar>
              <span>{{ row.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'warning' : 'info'" size="small">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" min-width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.role !== 'admin'"
              text
              type="primary"
              @click="handleSetAdmin(row)"
            >
              设为管理员
            </el-button>
            <el-button
              v-else-if="row.username !== currentUsername"
              text
              type="warning"
              @click="handleSetUser(row)"
            >
              设为用户
            </el-button>
            <el-button
              v-if="row.username !== currentUsername"
              text
              type="danger"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 管理员用户管理页面组件
 * 展示所有用户列表，支持修改角色和删除用户
 */
import { ref, computed, onMounted } from 'vue'
import { getUsers, updateUser, deleteUser } from '../../api/admin'
import { useUserStore } from '../../stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()

const loading = ref(false)
const users = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const keyword = ref('')

// 当前用户名（用于判断是否可以删除或修改自己的角色）
const currentUsername = computed(() => userStore.username)

/**
 * 加载用户列表
 */
const loadUsers = async () => {
  loading.value = true
  try {
    const res = await getUsers({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value
    })
    if (res.data) {
      users.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 设为管理员
 */
const handleSetAdmin = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要将用户 "${user.username}" 设为管理员吗？`,
      '提示',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await updateUser(user.id, { role: 'admin' })
    ElMessage.success('操作成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

/**
 * 设为普通用户
 */
const handleSetUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要将用户 "${user.username}" 设为普通用户吗？`,
      '提示',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await updateUser(user.id, { role: 'user' })
    ElMessage.success('操作成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

/**
 * 删除用户
 */
const handleDelete = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复！`,
      '警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'error' }
    )
    await deleteUser(user.id)
    ElMessage.success('删除成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

/**
 * 分页大小改变
 */
const handleSizeChange = () => {
  page.value = 1
  loadUsers()
}

/**
 * 页码改变
 */
const handlePageChange = () => {
  loadUsers()
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users-container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
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
  margin-bottom: 20px;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-cell .el-avatar {
  background-color: #FFB800;
  color: white;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
