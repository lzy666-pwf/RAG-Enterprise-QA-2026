/**
 * Vue Router路由配置
 * 定义应用的路由结构和权限控制
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

// 路由懒加载
const Login = () => import('../views/Login.vue')
const Register = () => import('../views/Register.vue')
const Layout = () => import('../views/Layout.vue')
const Home = () => import('../views/Home.vue')
const Chat = () => import('../views/Chat.vue')
const History = () => import('../views/History.vue')
const Documents = () => import('../views/Documents.vue')
const AdminHome = () => import('../views/admin/Home.vue')
const AdminUsers = () => import('../views/admin/Users.vue')
const AdminDocuments = () => import('../views/admin/Documents.vue')
const AdminChats = () => import('../views/admin/Chats.vue')

// 定义路由规则
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { title: '注册', requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: Home,
        meta: { title: '首页' }
      },
      {
        path: 'chat',
        name: 'Chat',
        component: Chat,
        meta: { title: '智能问答' }
      },
      {
        path: 'history',
        name: 'History',
        component: History,
        meta: { title: '问答历史' }
      },
      {
        path: 'documents',
        name: 'Documents',
        component: Documents,
        meta: { title: '我的文档' }
      }
    ]
  },
  {
    path: '/admin',
    component: Layout,
    redirect: '/admin/home',
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: 'home',
        name: 'AdminHome',
        component: AdminHome,
        meta: { title: '管理后台', requiresAdmin: true }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: AdminUsers,
        meta: { title: '用户管理', requiresAdmin: true }
      },
      {
        path: 'documents',
        name: 'AdminDocuments',
        component: AdminDocuments,
        meta: { title: '文档管理', requiresAdmin: true }
      },
      {
        path: 'chats',
        name: 'AdminChats',
        component: AdminChats,
        meta: { title: '问答记录', requiresAdmin: true }
      }
    ]
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由前置守卫：验证登录状态和权限
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || '知识库'} - 企业知识库问答系统`

  const userStore = useUserStore()

  // 需要登录的页面
  if (to.meta.requiresAuth !== false && !userStore.isLoggedIn) {
    next('/login')
    return
  }

  // 需要管理员权限的页面
  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    ElMessage.error('需要管理员权限')
    next('/home')
    return
  }

  // 已登录用户访问登录/注册页，跳转首页
  if (userStore.isLoggedIn && ['/login', '/register'].includes(to.path)) {
    next('/home')
    return
  }

  next()
})

export default router
