const app = getApp();

Page({
  data: {
    stats: {
      user_count: 0,
      new_users_today: 0,
      listing_count: 0,
      listing_pending: 0
    }
  },

  onShow() {
    this.fetchStats();
  },

  fetchStats() {
    const token = wx.getStorageSync('access_token');
    wx.request({
      url: `${app.globalData.baseUrl}/admin/stats/`,
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ stats: res.data });
        }
      }
    });
  },

  goToUsers() {
    wx.navigateTo({
      url: '/pages/admin/users/list/list'
    });
  },

  goToShips() {
      wx.navigateTo({
          url: '/pages/admin/ships/list/list'
      });
  },

  goToPendingListings() {
    // Navigate to ship list with status=PENDING
    wx.navigateTo({
        url: '/pages/admin/ships/list/list?status=PENDING'
    });
  },

  goToForumModeration() {
    wx.navigateTo({
      url: '/pages/admin/messages/list/list'
    });
  }
});
