const app = getApp();

Page({
  data: {
    id: null,
    content: '',
    isSubmitting: false
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ id: options.id });
      this.fetchMessage(options.id);
    }
  },

  fetchMessage(id) {
    const token = wx.getStorageSync('access_token');
    wx.request({
      url: `${app.globalData.baseUrl}/messages/${id}/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            content: res.data.content
          });
        }
      }
    });
  },

  submitForm(e) {
    const content = e.detail.value.content;
    if (!content) {
      wx.showToast({
        title: '请输入内容',
        icon: 'none'
      });
      return;
    }

    this.setData({ isSubmitting: true });
    const token = wx.getStorageSync('access_token');
    const url = `${app.globalData.baseUrl}/messages/${this.data.id}/`;
    const method = 'PATCH'; // or PUT

    wx.request({
      url: url,
      method: method,
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: {
        content: content
      },
      success: (res) => {
        if (res.statusCode === 200) {
          wx.showToast({
            title: '修改成功',
            icon: 'success'
          });
          setTimeout(() => {
            wx.navigateBack();
          }, 1500);
        } else {
          wx.showToast({
            title: '修改失败',
            icon: 'none'
          });
        }
      },
      complete: () => {
        this.setData({ isSubmitting: false });
      }
    });
  }
});