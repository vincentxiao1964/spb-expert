const app = getApp();

Page({
  data: {
    messages: [],
    page: 1,
    hasMore: true,
    isLoading: false
  },

  onShow() {
    const userInfo = wx.getStorageSync('user_info');
    if (!userInfo || !(userInfo.is_staff || userInfo.is_superuser)) {
      wx.showToast({ title: '无权限', icon: 'none' });
      wx.navigateBack();
      return;
    }
    this.setData({ page: 1, messages: [], hasMore: true });
    this.fetchMessages();
  },

  onPullDownRefresh() {
    this.setData({ page: 1, messages: [], hasMore: true });
    this.fetchMessages(() => {
      wx.stopPullDownRefresh();
    });
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.isLoading) {
      this.fetchMessages();
    }
  },

  fetchMessages(callback) {
    if (this.data.isLoading) return;

    this.setData({ isLoading: true });
    const token = wx.getStorageSync('access_token');

    wx.request({
      url: `${app.globalData.baseUrl}/messages/?page=${this.data.page}`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const newMessages = res.data.results || res.data || [];
          this.setData({
            messages: [...this.data.messages, ...newMessages],
            page: this.data.page + 1,
            hasMore: !!res.data.next
          });
          if (!res.data.next && !res.data.results) {
            this.setData({ hasMore: false });
          }
        }
      },
      complete: () => {
        this.setData({ isLoading: false });
        if (callback) callback();
      }
    });
  },

  navigateToEdit(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/admin/messages/edit/edit?id=${id}`
    });
  },

  handleDelete(e) {
    const id = e.currentTarget.dataset.id;
    const token = wx.getStorageSync('access_token');

    wx.showModal({
      title: '确认删除',
      content: '确定要删除这条留言吗？',
      success: (res) => {
        if (res.confirm) {
          wx.request({
            url: `${app.globalData.baseUrl}/messages/${id}/`,
            method: 'DELETE',
            header: {
              'Authorization': `Bearer ${token}`
            },
            success: (delRes) => {
              if (delRes.statusCode === 204) {
                wx.showToast({
                  title: '删除成功',
                  icon: 'success'
                });
                // Refresh list
                this.setData({ page: 1, messages: [], hasMore: true });
                this.fetchMessages();
              } else {
                wx.showToast({
                  title: '删除失败',
                  icon: 'none'
                });
              }
            }
          });
        }
      }
    });
  }
});
