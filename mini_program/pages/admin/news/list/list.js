const app = getApp();

Page({
  data: {
    newsList: [],
    loading: false,
    isAdmin: false
  },

  onShow() {
    this.fetchUserInfo();
    this.fetchNews();
  },

  fetchUserInfo() {
    const token = wx.getStorageSync('access_token');
    const userInfo = wx.getStorageSync('user_info');
    if (userInfo && (userInfo.is_staff || userInfo.is_superuser)) {
        this.setData({ isAdmin: true });
    } else {
        // Fallback or fetch if needed
        this.setData({ isAdmin: false });
    }
  },

  fetchNews() {
    const token = wx.getStorageSync('access_token');
    if (!token) {
      wx.redirectTo({ url: '/pages/login/login' });
      return;
    }

    this.setData({ loading: true });
    wx.request({
      url: `${app.globalData.baseUrl}/news/?manage=true&page=1&page_size=100`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const results = res.data.results || res.data;
          this.setData({ newsList: results });
        } else if (res.statusCode === 401) {
          wx.removeStorageSync('access_token');
          wx.redirectTo({ url: '/pages/login/login' });
        }
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },

  navigateToAdd() {
    wx.navigateTo({
      url: '/pages/admin/news/edit/edit'
    });
  },

  navigateToEdit(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/admin/news/edit/edit?id=${id}`
    });
  },

  handleAudit(e) {
    const { id, status } = e.currentTarget.dataset;
    const token = wx.getStorageSync('access_token');
    
    wx.showModal({
        title: status === 'APPROVED' ? '确认通过' : '确认拒绝',
        content: status === 'APPROVED' ? '确定批准这条资讯发布吗？' : '确定拒绝这条资讯发布吗？',
        success: (res) => {
            if (res.confirm) {
                wx.showLoading({ title: '处理中' });
                wx.request({
                    url: `${app.globalData.baseUrl}/news/${id}/?manage=true`,
                    method: 'PATCH',
                    header: {
                        'Authorization': `Bearer ${token}`
                    },
                    data: { status: status },
                    success: (res) => {
                        wx.hideLoading();
                        if (res.statusCode === 200) {
                            wx.showToast({ title: '操作成功' });
                            this.fetchNews();
                        } else {
                            wx.showToast({ title: '操作失败', icon: 'none' });
                        }
                    },
                    fail: () => {
                        wx.hideLoading();
                        wx.showToast({ title: '网络错误', icon: 'none' });
                    }
                });
            }
        }
    });
  },

  handleDelete(e) {
    const id = e.currentTarget.dataset.id;
    const token = wx.getStorageSync('access_token');

    wx.showModal({
      title: '确认删除',
      content: '确定要删除这条资讯吗？',
      success: (res) => {
        if (res.confirm) {
          wx.request({
            url: `${app.globalData.baseUrl}/news/${id}/`,
            method: 'DELETE',
            header: {
              'Authorization': `Bearer ${token}`
            },
            success: (delRes) => {
              if (delRes.statusCode === 204) {
                wx.showToast({ title: '删除成功' });
                this.fetchNews();
              } else if (delRes.statusCode === 401) {
                  wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
                  wx.removeStorageSync('access_token');
                  setTimeout(() => {
                      wx.redirectTo({ url: '/pages/login/login' });
                  }, 1500);
              } else if (delRes.statusCode === 403) {
                wx.showToast({ title: '无权删除他人发布的内容', icon: 'none' });
              } else {
                wx.showToast({ title: '删除失败', icon: 'none' });
              }
            }
          });
        }
      }
    });
  }
});
