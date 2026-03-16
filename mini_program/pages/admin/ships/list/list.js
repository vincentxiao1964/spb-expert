const app = getApp();

Page({
  data: {
    shipList: [],
    loading: false,
    options: {},
    isAdmin: false
  },

  onLoad(options) {
    this.setData({ options: options || {} });
  },

  onShow() {
    this.fetchUserInfo();
    this.fetchShips();
  },

  fetchUserInfo() {
    const token = wx.getStorageSync('access_token');
    if (!token) return;
    
    wx.request({
      url: `${app.globalData.baseUrl}/user/info/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
              isAdmin: res.data.is_staff || res.data.is_superuser
          });
        }
      }
    });
  },

  fetchShips() {
    const token = wx.getStorageSync('access_token');
    if (!token) {
      wx.redirectTo({ url: '/pages/login/login' });
      return;
    }

    this.setData({ loading: true });
    
    let url = `${app.globalData.baseUrl}/listings/?manage=true`;
    if (this.data.options && this.data.options.status) {
        url += `&status=${this.data.options.status}`;
    }

    wx.request({
      url: url,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          // Handle pagination (results array or direct array)
          const list = res.data.results || res.data;
          this.setData({ shipList: list });
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
      url: '/pages/admin/ships/edit/edit'
    });
  },

  navigateToEdit(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/admin/ships/edit/edit?id=${id}`
    });
  },

  handleAudit(e) {
    const { id, status } = e.currentTarget.dataset;
    const token = wx.getStorageSync('access_token');
    
    wx.showLoading({ title: '处理中...' });

    wx.request({
        url: `${app.globalData.baseUrl}/listings/${id}/?manage=true`,
        method: 'PATCH',
        header: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        data: { status: status },
        success: (res) => {
            if (res.statusCode >= 200 && res.statusCode < 300) {
                wx.showToast({ title: '操作成功' });
                this.fetchShips();
            } else {
                wx.showToast({ title: '操作失败', icon: 'none' });
            }
        },
        fail: () => {
            wx.showToast({ title: '网络错误', icon: 'none' });
        },
        complete: () => {
            wx.hideLoading();
        }
    });
  },

  handleDelete(e) {
    const id = e.currentTarget.dataset.id;
    const token = wx.getStorageSync('access_token');

    wx.showModal({
      title: '确认删除',
      content: '确定要删除这条船源吗？',
      success: (res) => {
        if (res.confirm) {
          wx.request({
            url: `${app.globalData.baseUrl}/listings/${id}/?manage=true`,
            method: 'DELETE',
            header: {
              'Authorization': `Bearer ${token}`
            },
            success: (delRes) => {
              if (delRes.statusCode === 204) {
                wx.showToast({ title: '删除成功' });
                this.fetchShips();
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