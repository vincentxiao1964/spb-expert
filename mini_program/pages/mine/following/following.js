const app = getApp()

Page({
  data: {
    following: [],
    loading: true,
    username: ''
  },

  onLoad() {
    this.fetchUserInfo();
    this.fetchFollowing();
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

  fetchFollowing() {
    const token = wx.getStorageSync('access_token');
    if (!token) {
        wx.redirectTo({ url: '/pages/login/login' });
        return;
    }

    wx.request({
      url: `${app.globalData.baseUrl}/following/following/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            following: res.data,
            loading: false
          });
        }
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },

  goChat(e) {
      const userId = e.currentTarget.dataset.userid;
      const username = e.currentTarget.dataset.username;
      wx.navigateTo({
          url: `/pages/messages/chat/chat?userId=${userId}&userName=${username}`
      });
  },

  unfollow(e) {
      const userId = e.currentTarget.dataset.userid;
      const that = this;
      
      wx.showModal({
          title: '提示',
          content: '确定要取消关注吗？',
          success(res) {
              if (res.confirm) {
                  that.doUnfollow(userId);
              }
          }
      });
  },

  doUnfollow(userId) {
      const token = wx.getStorageSync('access_token');
      wx.request({
          url: `${app.globalData.baseUrl}/following/toggle/`,
          method: 'POST',
          header: { 'Authorization': `Bearer ${token}` },
          data: { user_id: userId },
          success: (res) => {
              if (res.statusCode === 200 && res.data.is_following === false) {
                  wx.showToast({ title: '已取消关注' });
                  this.fetchFollowing(); // Refresh list
              }
          }
      });
  }
})
