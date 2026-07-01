<template>
  <div class="admin-home">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>
        <el-icon><DataLine /></el-icon>
        管理后台
      </h2>
      <p class="page-desc">系统数据统计与分析</p>
    </div>

    <!-- 概览统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #FFF8E6;">
            <el-icon style="color: #FFB800;"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.overview.total_users }}</div>
            <div class="stat-label">用户总数</div>
            <div class="stat-today">今日新增: {{ stats.today.users }}</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #E8F4FF;">
            <el-icon style="color: #1890FF;"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.overview.total_docs }}</div>
            <div class="stat-label">文档总数</div>
            <div class="stat-today">今日新增: {{ stats.today.docs }}</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #F0FFF4;">
            <el-icon style="color: #52C41A;"><ChatDotRound /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.overview.total_chats }}</div>
            <div class="stat-label">问答总数</div>
            <div class="stat-today">今日新增: {{ stats.today.chats }}</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #FFF0F0;">
            <el-icon style="color: #FF4D4F;"><Collection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.overview.indexed_docs }}</div>
            <div class="stat-label">已入库文档</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <!-- 问答趋势图 -->
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><TrendCharts /></el-icon>
                问答趋势（近7天）
              </span>
            </div>
          </template>
          <div v-if="stats.chat_trend && stats.chat_trend.length > 0" ref="chatTrendChartRef" class="chart-container"></div>
          <el-empty v-else description="暂无问答数据" />
        </el-card>
      </el-col>

      <!-- 用户分布图 -->
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><PieChart /></el-icon>
                用户角色分布
              </span>
            </div>
          </template>
          <div v-if="stats.role_distribution && stats.role_distribution.length > 0" ref="roleDistChartRef" class="chart-container"></div>
          <el-empty v-else description="暂无用户数据" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 问题关键词 + 文档使用频率 -->
    <el-row :gutter="20" class="charts-row">
      <!-- 问题关键词柱状图 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Histogram /></el-icon>
                高频问题关键词 Top15
              </span>
            </div>
          </template>
          <div v-if="stats.question_stats && stats.question_stats.length > 0" ref="keywordChartRef" class="chart-container-sm"></div>
          <el-empty v-else description="暂无问题数据，请先进行问答" />
        </el-card>
      </el-col>

      <!-- 文档使用频率柱状图 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Document /></el-icon>
                文档被查询次数 Top10
              </span>
            </div>
          </template>
          <div v-if="stats.doc_usage && stats.doc_usage.length > 0" ref="docUsageChartRef" class="chart-container-sm"></div>
          <el-empty v-else description="暂无文档使用记录" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 文档状态分布 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><DataAnalysis /></el-icon>
                文档状态分布
              </span>
            </div>
          </template>
          <div v-if="stats.doc_status && stats.doc_status.length > 0" ref="docStatusChartRef" class="chart-container-sm"></div>
          <el-empty v-else description="暂无文档数据" />
        </el-card>
      </el-col>

      <!-- 快捷入口 -->
      <el-col :span="12">
        <el-card class="quick-entry-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Menu /></el-icon>
                快捷入口
              </span>
            </div>
          </template>
          <div class="quick-entry-grid">
            <div class="entry-item" @click="goTo('/admin/users')">
              <div class="entry-icon">
                <el-icon><User /></el-icon>
              </div>
              <span>用户管理</span>
            </div>
            <div class="entry-item" @click="goTo('/admin/documents')">
              <div class="entry-icon">
                <el-icon><Document /></el-icon>
              </div>
              <span>文档管理</span>
            </div>
            <div class="entry-item" @click="goTo('/admin/chats')">
              <div class="entry-icon">
                <el-icon><ChatLineSquare /></el-icon>
              </div>
              <span>问答记录</span>
            </div>
            <div class="entry-item" @click="goTo('/chat')">
              <div class="entry-icon">
                <el-icon><ChatDotRound /></el-icon>
              </div>
              <span>智能问答</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
/**
 * 管理员首页组件
 * 展示系统整体数据统计、数据可视化图表和快捷入口
 */
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { getStats } from '../../api/admin'
import * as echarts from 'echarts'

const router = useRouter()

// 统计数据
const stats = reactive({
  overview: {
    total_users: 0,
    total_docs: 0,
    total_chats: 0,
    indexed_docs: 0
  },
  today: {
    users: 0,
    docs: 0,
    chats: 0
  },
  chat_trend: [],
  role_distribution: [],
  doc_status: [],
  question_stats: [],
  doc_usage: []
})

// 图表DOM引用
const chatTrendChartRef = ref(null)
const roleDistChartRef = ref(null)
const docStatusChartRef = ref(null)
const keywordChartRef = ref(null)
const docUsageChartRef = ref(null)

/**
 * 加载统计数据
 */
const loadStats = async () => {
  try {
    const res = await getStats()
    if (res.data) {
      Object.assign(stats.overview, res.data.overview || {})
      Object.assign(stats.today, res.data.today || {})
      stats.chat_trend = res.data.chat_trend || []
      stats.role_distribution = res.data.role_distribution || []
      stats.doc_status = res.data.doc_status || []
      stats.question_stats = res.data.question_stats || []
      stats.doc_usage = res.data.doc_usage || []

      // 更新图表
      nextTick(() => {
        initCharts()
      })
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

/**
 * 初始化图表
 */
const initCharts = () => {
  initChatTrendChart()
  initRoleDistChart()
  initDocStatusChart()
  initKeywordChart()
  initDocUsageChart()
}

/**
 * 问答趋势图
 */
const initChatTrendChart = () => {
  if (!chatTrendChartRef.value) return

  const chart = echarts.init(chatTrendChartRef.value)

  // 处理数据
  const dates = stats.chat_trend.map(item => item.date)
  const counts = stats.chat_trend.map(item => item.count)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'line'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [
      {
        name: '问答数量',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: {
          color: '#FFB800'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 184, 0, 0.4)' },
            { offset: 1, color: 'rgba(255, 184, 0, 0.05)' }
          ])
        },
        data: counts
      }
    ]
  }

  chart.setOption(option)
}

/**
 * 用户角色分布图
 */
const initRoleDistChart = () => {
  if (!roleDistChartRef.value) return

  const chart = echarts.init(roleDistChartRef.value)

  const roleMap = {
    'admin': '管理员',
    'user': '普通用户'
  }

  const data = stats.role_distribution.map(item => ({
    name: roleMap[item.role] || item.role,
    value: item.count
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '用户角色',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data,
        color: ['#FFB800', '#1890FF']
      }
    ]
  }

  chart.setOption(option)
}

/**
 * 文档状态分布图
 */
const initDocStatusChart = () => {
  if (!docStatusChartRef.value) return

  const chart = echarts.init(docStatusChartRef.value)

  const data = stats.doc_status.map(item => ({
    name: item.status,
    value: item.count
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}'
    },
    legend: {
      bottom: '5%',
      left: 'center'
    },
    series: [
      {
        name: '文档状态',
        type: 'pie',
        radius: '60%',
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        color: ['#FAAD14', '#52C41A']
      }
    ]
  }

  chart.setOption(option)
}

/**
 * 问题关键词柱状图
 */
const initKeywordChart = () => {
  if (!keywordChartRef.value) return

  const chart = echarts.init(keywordChartRef.value)

  const data = stats.question_stats.slice().reverse()
  const keywords = data.map(item => item.keyword)
  const counts = data.map(item => item.count)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      minInterval: 1
    },
    yAxis: {
      type: 'category',
      data: keywords,
      axisLabel: { fontSize: 11 }
    },
    series: [
      {
        name: '出现次数',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#FFB800' },
            { offset: 1, color: '#FF9500' }
          ]),
          borderRadius: [0, 4, 4, 0]
        },
        label: {
          show: true,
          position: 'right',
          fontSize: 11,
          color: '#999'
        }
      }
    ]
  }

  chart.setOption(option)
}

/**
 * 文档使用频率柱状图
 */
const initDocUsageChart = () => {
  if (!docUsageChartRef.value) return

  const chart = echarts.init(docUsageChartRef.value)

  const data = stats.doc_usage.slice().reverse()
  const titles = data.map(item => item.title.length > 10 ? item.title.substring(0, 10) + '...' : item.title)
  const counts = data.map(item => item.count)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const d = data[params[0].dataIndex]
        return `${d.title}<br/>被查询次数: ${d.count} 次`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      minInterval: 1
    },
    yAxis: {
      type: 'category',
      data: titles,
      axisLabel: { fontSize: 10 }
    },
    series: [
      {
        name: '查询次数',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#1890FF' },
            { offset: 1, color: '#0050B3' }
          ]),
          borderRadius: [0, 4, 4, 0]
        },
        label: {
          show: true,
          position: 'right',
          fontSize: 11,
          color: '#999'
        }
      }
    ]
  }

  chart.setOption(option)
}

/**
 * 跳转到指定页面
 */
const goTo = (path) => {
  router.push(path)
}

onMounted(() => {
  loadStats()

  // 监听窗口大小变化，自适应图表
  window.addEventListener('resize', () => {
    if (chatTrendChartRef.value) echarts.getInstanceByDom(chatTrendChartRef.value)?.resize()
    if (roleDistChartRef.value) echarts.getInstanceByDom(roleDistChartRef.value)?.resize()
    if (docStatusChartRef.value) echarts.getInstanceByDom(docStatusChartRef.value)?.resize()
    if (keywordChartRef.value) echarts.getInstanceByDom(keywordChartRef.value)?.resize()
    if (docUsageChartRef.value) echarts.getInstanceByDom(docUsageChartRef.value)?.resize()
  })
})
</script>

<style scoped>
.admin-home {
  max-width: 1400px;
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

/* 统计卡片 */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon .el-icon {
  font-size: 32px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin: 4px 0;
}

.stat-today {
  font-size: 12px;
  color: #999;
}

/* 图表卡片 */
.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.card-header .el-icon {
  color: #FFB800;
}

.chart-container {
  height: 280px;
}

.chart-container-sm {
  height: 200px;
}

/* 快捷入口 */
.quick-entry-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.entry-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px 16px;
  background: #FAFAFA;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.entry-item:hover {
  background: #FFF8E6;
  transform: translateY(-2px);
}

.entry-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #FFB800 0%, #FF9500 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.entry-icon .el-icon {
  font-size: 24px;
  color: white;
}

.entry-item span {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.entry-item:hover span {
  color: #E6A600;
}
</style>
