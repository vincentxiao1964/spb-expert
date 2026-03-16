const app = getApp()

Page({
  data: {
    userFollowers: [],
    listingFavorites: [],
    activeTab: 0,
    loading: true
  },

  onLoad() {
    this.fetchFollowers();
  },
  
  switchTab(e) {
      this.setData({
          activeTab: parseInt(e.currentTarget.dataset.index)
      });
  },

  fetchFollowers() {
    const token = wx.getStorageSync('access_token');
    if (!token) {
        wx.redirectTo({ url: '/pages/login/login' });
        return;
    }

    // 1. Fetch User Followers (Sync with website)
    const p1 = new Promise((resolve) => {
        wx.request({
            url: `${app.globalData.baseUrl}/following/followers/`,
            method: 'GET',
            header: { 'Authorization': `Bearer ${token}` },
            success: (res) => resolve(res.statusCode === 200 ? res.data : [])
        });
    });

    // 2. Fetch Listing Favorites (Legacy/Enhanced feature)
    const p2 = new Promise((resolve) => {
        wx.request({
            url: `${app.globalData.baseUrl}/favorites/who_favorited_me/`,
            method: 'GET',
            header: { 'Authorization': `Bearer ${token}` },
            success: (res) => resolve(res.statusCode === 200 ? res.data : [])
        });
    });

    Promise.all([p1, p2]).then(([userFollowers, listingFavorites]) => {
        this.setData({
            userFollowers: userFollowers,
            listingFavorites: listingFavorites,
            loading: false
        });
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
