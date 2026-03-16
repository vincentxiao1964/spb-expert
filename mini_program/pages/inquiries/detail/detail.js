const app = getApp();

Page({
  data: {
    inquiry: null,
    loading: true,
    canAccept: false
  },

  onLoad: function (options) {
    if (options.id) {
      this.fetchInquiry(options.id);
    }
  },

  fetchInquiry: function (id) {
    const token = wx.getStorageSync('access_token');
    wx.request({
      url: `${app.globalData.baseUrl}/inquiries/${id}/`,
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        if (res.statusCode === 200) {
          const inquiry = res.data;
          this.setData({ 
            inquiry: inquiry,
            loading: false,
            canAccept: inquiry.status === 'QUOTED' // Assuming QUOTED status allows acceptance
          });
        }
      }
    });
  },

  onAcceptQuote() {
    const token = wx.getStorageSync('access_token');
    wx.showLoading({ title: '处理中' });
    
    wx.request({
      url: `${app.globalData.baseUrl}/inquiries/${this.data.inquiry.id}/accept_quote/`,
      method: 'POST',
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        wx.hideLoading();
        if (res.statusCode === 200 || res.statusCode === 201) {
           const orderId = res.data.order_id || res.data.id; // API returns order object usually, check view
           wx.showToast({ title: '已生成订单' });
           setTimeout(() => {
               // Navigate to order detail
               wx.redirectTo({
                   url: `/pages/orders/detail/detail?id=${orderId}`
               });
           }, 1500);
        } else {
           wx.showToast({ title: res.data.detail || '操作失败', icon: 'none' });
        }
      },
      fail: () => {
          wx.hideLoading();
          wx.showToast({ title: '网络错误', icon: 'none' });
      }
    });
  }
});
