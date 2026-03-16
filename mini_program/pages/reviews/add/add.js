const app = getApp();

Page({
  data: {
    order_id: null,
    rating: 5,
    comment: '',
    files: [],
    loading: false
  },

  onLoad: function (options) {
    if (options.order_id) {
      this.setData({ order_id: options.order_id });
    }
    if (options.item_id) {
        this.setData({ item_id: options.item_id });
    }
  },

  onRate(e) {
      this.setData({ rating: parseInt(e.currentTarget.dataset.score) });
  },

  onInput(e) {
      this.setData({ comment: e.detail.value });
  },

  submit() {
      if (!this.data.comment) {
          wx.showToast({ title: '请输入评价内容', icon: 'none' });
          return;
      }
      
      this.setData({ loading: true });
      const token = wx.getStorageSync('access_token');
      
      if (this.data.item_id) {
          this.createReview(this.data.item_id, token);
      } else {
        // Fallback: Fetch order to get item ID (assuming first item for MVP)
        wx.request({
            url: `${app.globalData.baseUrl}/orders/${this.data.order_id}/`,
            header: { 'Authorization': `Bearer ${token}` },
            success: (res) => {
                const order = res.data;
                if (order.items && order.items.length > 0) {
                    const itemId = order.items[0].id;
                    this.createReview(itemId, token);
                } else {
                    wx.showToast({ title: '订单无商品', icon: 'none' });
                    this.setData({ loading: false });
                }
            },
            fail: () => {
                this.setData({ loading: false });
            }
        });
      }
  },

  createReview(itemId, token) {
      wx.request({
          url: `${app.globalData.baseUrl}/reviews/`,
          method: 'POST',
          header: { 'Authorization': `Bearer ${token}` },
          data: {
              order_item_id: itemId,
              rating: this.data.rating,
              comment: this.data.comment
          },
          success: (res) => {
              if (res.statusCode === 201) {
                  wx.showToast({ title: '评价成功' });
                  setTimeout(() => {
                      wx.navigateBack();
                  }, 1500);
              } else {
                  wx.showToast({ title: res.data.detail || '评价失败', icon: 'none' });
              }
          },
          complete: () => {
              this.setData({ loading: false });
          }
      });
  }
});
