const app = getApp()

Page({
  data: {
    matches: [],
    loading: false
  },
  onLoad: function () {
    this.fetchMatches();
  },
  onPullDownRefresh: function() {
      this.fetchMatches();
  },
  fetchMatches: function () {
    this.setData({ loading: true });
    const token = wx.getStorageSync('access_token');
    if (!token) {
        wx.showToast({ title: '请先登录', icon: 'none' });
        this.setData({ loading: false });
        return;
    }

    wx.request({
      url: `${app.globalData.baseUrl}/matches/`,
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        if (res.statusCode === 200) {
           const matches = (res.data.results || res.data).map(item => {
               // Format date
               const date = new Date(item.created_at);
               const year = date.getFullYear();
               const month = (date.getMonth() + 1).toString().padStart(2, '0');
               const day = date.getDate().toString().padStart(2, '0');
               item.created_at_formatted = `${year}-${month}-${day}`;
               return item;
           });
           this.setData({ matches: matches });
        } else {
            wx.showToast({ title: '获取匹配失败', icon: 'none' });
        }
      },
      fail: () => {
          wx.showToast({ title: '网络错误', icon: 'none' });
      },
      complete: () => {
        this.setData({ loading: false });
        wx.stopPullDownRefresh();
      }
    });
  },
  goDetail: function (e) {
      const id = e.currentTarget.dataset.id;
      wx.navigateTo({
          url: `/pages/detail/detail?id=${id}`
      });
  },
  goChat: function(e) {
      const targetUserId = e.currentTarget.dataset.userid;
      const targetUserName = e.currentTarget.dataset.username;
      wx.navigateTo({
          url: `/pages/messages/chat/chat?userId=${targetUserId}&userName=${encodeURIComponent(targetUserName)}`
      });
  }
})
