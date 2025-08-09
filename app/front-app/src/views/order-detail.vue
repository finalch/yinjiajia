<template>
  <div class="detail-container">
    <div class="header">
      <div class="back-btn" @click="goBack">←</div>
      <div class="title">订单详情</div>
    </div>

    <!-- 订单信息 -->
    <div class="card">
      <div class="row"><span class="label">订单号</span><span class="value">{{ order.order_number }}</span></div>
      <div class="row"><span class="label">下单时间</span><span class="value">{{ formatDate(order.created_at) }}</span></div>
      <div class="row"><span class="label">订单状态</span><span class="value status" :class="statusClass">{{ order.status_text }}</span></div>
      <div class="row total"><span class="label">合计</span><span class="value price">¥{{ formatPrice(order.total_amount) }}</span></div>
    </div>

    <!-- 物流信息 -->
    <div class="card" v-if="order.logistics">
      <div class="card-title">物流信息</div>
      <div class="row"><span class="label">物流公司</span><span class="value">{{ order.logistics.carrier }}</span></div>
      <div class="row"><span class="label">运单号</span><span class="value">{{ order.logistics.tracking_number }}</span></div>
      <div class="row"><span class="label">状态</span><span class="value">{{ order.logistics.status_text || order.logistics.status }}</span></div>
      <div class="row"><span class="label">更新时间</span><span class="value">{{ formatDate(order.logistics.updated_at) }}</span></div>
    </div>

    <!-- 商品列表 -->
    <div class="card">
      <div class="card-title">商品列表</div>
      <div class="item" v-for="it in order.items" :key="it.id">
        <div class="thumb"><img :src="it.product_image || '/static/default-product.png'" /></div>
        <div class="info">
          <div class="name" :title="it.product_name">{{ it.product_name }}</div>
          <div class="spec" v-if="it.spec_combination_id">规格：{{ it.spec_combination_id }}</div>
          <div class="meta">
            <span class="price">¥{{ formatPrice(it.price) }}</span>
            <span class="qty">×{{ it.quantity }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import request from '@/utils/request.js'
import { getUserId } from '@/utils/auth.js'

export default {
  name: 'OrderDetail',
  data() {
    return {
      order: { items: [] }
    }
  },
  computed: {
    statusClass() {
      const m = {
        pending: 'status-pending',
        paid: 'status-paid',
        shipped: 'status-shipped',
        delivered: 'status-delivered',
        completed: 'status-completed',
        cancelled: 'status-cancelled',
        refunded: 'status-refunded'
      }
      return m[this.order.status] || 'status-default'
    }
  },
  mounted() {
    this.loadDetail()
  },
  methods: {
    formatDate(v) {
      if (!v) return ''
      const d = new Date(v)
      const p = n => String(n).padStart(2, '0')
      return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
    },
    formatPrice(n) { return Number(n || 0).toFixed(2) },
    goBack() { this.$router.go(-1) },
    async loadDetail() {
      const id = this.$route.params.id
      const res = await request.get(`/api/app/order/${id}`, { params: { user_id: getUserId() } })
      if (res.data && res.data.code === 200) {
        this.order = res.data.data
      } else {
        alert(res.data?.message || '加载失败')
      }
    }
  }
}
</script>

<style scoped>
.detail-container { min-height: 100vh; background:#f5f5f5; padding-bottom: 80px; }
.header { background:#fff; padding:15px 20px; display:flex; align-items:center; border-bottom:1px solid #eee; position:sticky; top:0; z-index:10; }
.back-btn { font-size:20px; cursor:pointer; margin-right:10px; }
.title { font-size:18px; font-weight:700; }

.card { background:#fff; margin:12px; border-radius:12px; padding:12px 14px; box-shadow:0 2px 8px rgba(0,0,0,0.04); }
.card-title { font-weight:600; margin-bottom:8px; color:#333; }
.row { display:flex; justify-content:space-between; align-items:center; padding:6px 0; font-size:14px; }
.row .label { color:#666; }
.row .value { color:#111; }
.row.total .value.price { color:#ff4757; font-weight:700; }

.item { display:flex; gap:10px; padding:10px 0; border-bottom:1px dashed #eee; }
.item:last-child { border-bottom:none; }
.thumb { width:64px; height:64px; border-radius:6px; overflow:hidden; flex-shrink:0; }
.thumb img { width:100%; height:100%; object-fit:cover; }
.info { flex:1; display:flex; flex-direction:column; justify-content:space-between; }
.name { font-size:14px; color:#333; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.spec { font-size:12px; color:#999; margin:4px 0; }
.meta { display:flex; justify-content:space-between; align-items:center; }
.meta .price { color:#ff4757; font-weight:600; }
.meta .qty { color:#666; font-size:12px; }

.status-pending { background:#fff3cd; color:#856404; padding:2px 6px; border-radius:4px; }
.status-paid { background:#d1ecf1; color:#0c5460; padding:2px 6px; border-radius:4px; }
.status-shipped { background:#d4edda; color:#155724; padding:2px 6px; border-radius:4px; }
.status-delivered { background:#e2e3e5; color:#6c757d; padding:2px 6px; border-radius:4px; }
.status-completed { background:#d1ecf1; color:#0c5460; padding:2px 6px; border-radius:4px; }
.status-cancelled { background:#f8d7da; color:#721c24; padding:2px 6px; border-radius:4px; }
.status-refunded { background:#e2e3e5; color:#6c757d; padding:2px 6px; border-radius:4px; }
</style>


