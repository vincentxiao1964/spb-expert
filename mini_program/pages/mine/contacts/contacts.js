const app = getApp()

Page({
  data: {
    conversations: [],
    loading: true
  },

  onLoad() {
    this.fetchConversations();
  },

  onShow() {
      // Refresh when coming back
      this.fetchConversations();
  },

  fetchConversations() {
    const token = wx.getStorageSync('access_token');
    if (!token) {
        wx.redirectTo({ url: '/pages/login/login' });
        return;
    }

    wx.request({
      url: `${app.globalData.baseUrl}/private-messages/conversations/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            conversations: res.data,
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
  }
})
