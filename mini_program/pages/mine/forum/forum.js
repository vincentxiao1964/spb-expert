const app = getApp()

Page({
  data: {
    messages: [],
    loading: true,
    username: ''
  },

  onLoad() {
    this.fetchUserInfo();
    this.fetchMessages();
  },

  fetchUserInfo() {
      const token = wx.getStorageSync('access_token');
      if (!token) return;
      
      wx.request({
          url: `${app.globalData.baseUrl}/user/info/`,
          method: 'GET',
          header: { 'Authorization': `Bearer ${token}` },
          success: (res) => {
              if (res.statusCode === 200) {
                  this.setData({ username: res.data.username });
              }
          }
      });
  },

  fetchMessages() {
    const token = wx.getStorageSync('access_token');
    if (!token) {
        wx.redirectTo({ url: '/pages/login/login' });
        return;
    }

    wx.request({
      url: `${app.globalData.baseUrl}/messages/?mode=my`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            messages: res.data,
            loading: false
          });
        }
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },

  goToDetail(e) {
      const id = e.currentTarget.dataset.id;
      wx.navigateTo({
          url: `/pages/messages/detail/detail?id=${id}`
      });
  }
})
