const app = getApp();

Page({
  data: {
    content: '',
    submitting: false
  },

  submit() {
    if (!this.data.content.trim()) {
      wx.showToast({
        title: '请输入内容',
        icon: 'none'
      });
      return;
    }

    this.setData({ submitting: true });
    
    const token = wx.getStorageSync('access_token');
    
    wx.request({
      url: `${app.globalData.baseUrl}/messages/`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${token}`
      },
      data: {
        content: this.data.content
      },
      success: (res) => {
        if (res.statusCode === 201) {
          wx.showToast({
            title: '发帖成功',
            icon: 'success'
          });
          setTimeout(() => {
            // Refresh previous page
            const pages = getCurrentPages();
            const prevPage = pages[pages.length - 2];
            if (prevPage && prevPage.fetchMessages) {
                prevPage.setData({ page: 1, messages: [] }, () => {
                    prevPage.fetchMessages(true);
                });
            }
            wx.navigateBack();
          }, 1500);
        } else {
          this.setData({ submitting: false });
          if (res.statusCode === 400) {
            wx.showToast({ title: '内容可能含违规信息', icon: 'none' });
            return;
          }
          wx.showToast({
            title: '发帖失败',
            icon: 'none'
          });
          console.error(res);
        }
      },
      fail: (err) => {
        this.setData({ submitting: false });
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
        console.error(err);
      }
    });
  }
})
