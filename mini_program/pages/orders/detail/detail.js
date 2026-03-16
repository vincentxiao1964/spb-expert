const app = getApp();

Page({
  data: {
    order: null,
    loading: true,
    isBuyer: false,
    isSeller: false
  },

  onLoad: function (options) {
    if (options.id) {
      this.fetchOrder(options.id);
    }
  },
  
  onShow: function() {
      if (this.data.order) {
          this.fetchOrder(this.data.order.id);
      }
  },

  fetchOrder: function (id) {
    const token = wx.getStorageSync('access_token');
    const userInfo = wx.getStorageSync('user_info');

    wx.request({
      url: `${app.globalData.baseUrl}/orders/${id}/`,
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        if (res.statusCode === 200) {
          const order = res.data;
          this.setData({ 
            order: order,
            loading: false,
            isBuyer: userInfo && order.buyer === userInfo.id,
            isSeller: userInfo && order.seller === userInfo.id
          });
        }
      }
    });
  },

  onPay() {
      const token = wx.getStorageSync('access_token');
      wx.showLoading({ title: '正在创建支付...' });
      
      wx.request({
          url: `${app.globalData.baseUrl}/payments/create_order/`,
          method: 'POST',
          header: { 'Authorization': `Bearer ${token}` },
          data: { order_id: this.data.order.id },
          success: (res) => {
              wx.hideLoading();
              if (res.statusCode === 200) {
                  const params = res.data;
                  // Call WeChat Pay
                  wx.requestPayment({
                      timeStamp: params.timeStamp,
                      nonceStr: params.nonceStr,
                      package: params.package,
                      signType: params.signType,
                      paySign: params.paySign,
                      success: () => {
                          wx.showToast({ title: '支付成功' });
                          // Poll or wait for callback processing, but for UX just refresh
                          setTimeout(() => {
                              this.fetchOrder(this.data.order.id);
                          }, 2000);
                      },
                      fail: (err) => {
                          console.error('Payment failed', err);
                          wx.showToast({ title: '支付取消或失败', icon: 'none' });
                      }
                  });
              } else {
                  wx.showToast({ title: res.data.error || '创建支付失败', icon: 'none' });
              }
          },
          fail: () => {
              wx.hideLoading();
              wx.showToast({ title: '网络错误', icon: 'none' });
          }
      });
  },

  onShip() {
      this.callAction('ship', '已发货');
  },

  onComplete() {
      this.callAction('complete', '订单已完成');
  },
  
  onReview(e) {
      const itemId = e.currentTarget.dataset.itemId;
      if (!itemId) return;
      
      wx.navigateTo({
          url: `/pages/reviews/add/add?order_id=${this.data.order.id}&item_id=${itemId}`
      });
  },

  callAction(action, successMsg) {
    const token = wx.getStorageSync('access_token');
    wx.showLoading({ title: '处理中' });
    
    wx.request({
        url: `${app.globalData.baseUrl}/orders/${this.data.order.id}/${action}/`,
        method: 'POST',
        header: { 'Authorization': `Bearer ${token}` },
        success: (res) => {
            wx.hideLoading();
            if (res.statusCode === 200) {
                wx.showToast({ title: successMsg });
                this.fetchOrder(this.data.order.id);
            } else {
                wx.showToast({ title: res.data.error || '失败', icon: 'none' });
            }
        },
        fail: () => {
             wx.hideLoading();
             wx.showToast({ title: '网络错误', icon: 'none' });
        }
    });
  }
});
