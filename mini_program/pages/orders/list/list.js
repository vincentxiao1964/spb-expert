const app = getApp();

Page({
  data: {
    orders: [],
    loading: true,
    activeTab: 'all',
    tabs: [
      { key: 'all', label: '全部' },
      { key: 'PENDING', label: '待付款' },
      { key: 'PAID', label: '待发货' },
      { key: 'SHIPPED', label: '待收货' },
      { key: 'COMPLETED', label: '已完成' }
    ]
  },

  onLoad: function (options) {
    this.fetchOrders();
  },

  onShow: function () {
    this.fetchOrders();
  },

  onTabClick(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({ activeTab: tab });
    this.fetchOrders();
  },

  fetchOrders: function () {
    const token = wx.getStorageSync('access_token');
    if (!token) return;

    this.setData({ loading: true });
    
    let url = `${app.globalData.baseUrl}/orders/`;
    if (this.data.activeTab !== 'all') {
        url += `?status=${this.data.activeTab}`;
    }
    
    wx.request({
      url: url,
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        if (res.statusCode === 200) {
          const list = res.data.results || res.data;
          this.setData({ 
            orders: list,
            loading: false 
          });
        }
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },

  goToDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/orders/detail/detail?id=${id}`,
    });
  }
});
