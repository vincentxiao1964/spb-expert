const app = getApp();

Page({
  data: {
    list: [],
    loading: false,
    isAdmin: false
  },

  onShow() {
    this.fetchUserInfo();
    this.fetchList();
  },

  fetchUserInfo() {
    const userInfo = wx.getStorageSync('user_info');
    if (userInfo && (userInfo.is_staff || userInfo.is_superuser)) {
        this.setData({ isAdmin: true });
    }
  },

  onPullDownRefresh() {
    this.fetchList(() => {
      wx.stopPullDownRefresh();
    });
  },

  fetchList(cb) {
    this.setData({ loading: true });
    const token = wx.getStorageSync('access_token');
    
    wx.request({
      url: `${app.globalData.baseUrl}/ads/?manage=true`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          // Extract site root from API_BASE
          const siteRoot = app.globalData.baseUrl.split('/api')[0];
          
          const list = res.data.map(item => {
            // Format date if needed, or backend handles it
            item.created_at_formatted = item.created_at.split('T')[0];
            
            // Fix image URL
            if (item.image) {
                if (!item.image.startsWith('http')) {
                   item.image = siteRoot + item.image;
                } else if (item.image.includes('127.0.0.1')) {
                   // Replace 127.0.0.1 with current API host
                   const currentHost = siteRoot.split('://')[1].split(':')[0];
                   item.image = item.image.replace('127.0.0.1', currentHost);
                }
            }
            
            return item;
          });
          this.setData({ list });
        }
      },
      fail: (err) => {
        console.error(err);
        wx.showToast({ title: '加载失败', icon: 'none' });
      },
      complete: () => {
        this.setData({ loading: false });
        if (cb) cb();
      }
    });
  },

  goAdd() {
    wx.navigateTo({
      url: '/pages/admin/ads/edit/edit'
    });
  },

  goEdit(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/admin/ads/edit/edit?id=${id}`
    });
  },

  handleAudit(e) {
    const { id, status } = e.currentTarget.dataset;
    const token = wx.getStorageSync('access_token');
    
    wx.showModal({
        title: status === 'APPROVED' ? '确认通过' : '确认拒绝',
        content: status === 'APPROVED' ? '确定批准这条广告吗？' : '确定拒绝这条广告吗？',
        success: (res) => {
            if (res.confirm) {
                wx.showLoading({ title: '处理中' });
                wx.request({
                    url: `${app.globalData.baseUrl}/ads/${id}/?manage=true`,
                    method: 'PATCH',
                    header: {
                        'Authorization': `Bearer ${token}`
                    },
                    data: { status: status },
                    success: (res) => {
                        wx.hideLoading();
                        if (res.statusCode === 200) {
                            wx.showToast({ title: '操作成功' });
                            this.fetchList();
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
    wx.showModal({
      title: '提示',
      content: '确定要删除这条广告吗？',
      success: (res) => {
        if (res.confirm) {
          this.deleteItem(id);
        }
      }
    });
  },

  deleteItem(id) {
    const token = wx.getStorageSync('access_token');
    wx.request({
      url: `${app.globalData.baseUrl}/ads/${id}/`,
      method: 'DELETE',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 204) {
          wx.showToast({ title: '删除成功' });
          this.fetchList();
        } else if (res.statusCode === 401) {
            wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
            wx.removeStorageSync('access_token');
            setTimeout(() => {
                wx.redirectTo({ url: '/pages/login/login' });
            }, 1500);
        } else {
          console.error('Delete failed:', res);
          let errorMsg = '删除失败';
           if (res.data && res.data.detail) {
               errorMsg += ': ' + res.data.detail;
           }
          wx.showToast({ title: errorMsg, icon: 'none', duration: 3000 });
        }
      },
      fail: (err) => {
        console.error(err);
        wx.showToast({ title: '网络错误', icon: 'none' });
      }
    });
  }
});