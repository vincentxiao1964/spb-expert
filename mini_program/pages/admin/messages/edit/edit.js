const app = getApp();

Page({
  data: {
    id: null,
    content: '',
    replies: [],
    message: null,
    isSubmitting: false
  },

  onLoad(options) {
    const userInfo = wx.getStorageSync('user_info');
    if (!userInfo || !(userInfo.is_staff || userInfo.is_superuser)) {
      wx.showToast({ title: '无权限', icon: 'none' });
      wx.navigateBack();
      return;
    }
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
            message: res.data,
            content: res.data.content,
            replies: res.data.replies || []
          });
        }
      }
    });
  },

  deleteTopic() {
    const token = wx.getStorageSync('access_token');
    const id = this.data.id;
    wx.showModal({
      title: '确认删除',
      content: '确定要删除该帖子及其回复吗？',
      confirmColor: '#ff4d4f',
      success: (res) => {
        if (!res.confirm) return;
        wx.request({
          url: `${app.globalData.baseUrl}/messages/${id}/`,
          method: 'DELETE',
          header: { 'Authorization': `Bearer ${token}` },
          success: (delRes) => {
            if (delRes.statusCode === 204) {
              wx.showToast({ title: '已删除', icon: 'success' });
              setTimeout(() => wx.navigateBack(), 800);
            } else {
              wx.showToast({ title: '删除失败', icon: 'none' });
            }
          },
          fail: () => wx.showToast({ title: '网络错误', icon: 'none' })
        });
      }
    });
  },

  deleteReply(e) {
    const replyId = e.currentTarget.dataset.id;
    const token = wx.getStorageSync('access_token');
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这条回复吗？',
      confirmColor: '#ff4d4f',
      success: (res) => {
        if (!res.confirm) return;
        wx.request({
          url: `${app.globalData.baseUrl}/message-replies/${replyId}/`,
          method: 'DELETE',
          header: { 'Authorization': `Bearer ${token}` },
          success: (delRes) => {
            if (delRes.statusCode === 204) {
              const replies = (this.data.replies || []).filter(r => String(r.id) !== String(replyId));
              this.setData({ replies });
              wx.showToast({ title: '已删除', icon: 'success' });
            } else {
              wx.showToast({ title: '删除失败', icon: 'none' });
            }
          },
          fail: () => wx.showToast({ title: '网络错误', icon: 'none' })
        });
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
          if (res.statusCode === 400) {
            wx.showToast({ title: '内容可能含违规信息', icon: 'none' });
            return;
          }
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
