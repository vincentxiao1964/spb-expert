Page({
  data: {
    ad: null,
    loading: true,
    isFavorite: false,
    isFollowing: false
  },
  onLoad: function (options) {
    const id = options.id;
    if (id) {
        this.fetchAdDetail(id);
    } else {
        this.setData({ loading: false });
        wx.showToast({ title: '缺少广告ID', icon: 'none' });
    }
  },
  fetchAdDetail: function(id) {
    const app = getApp();
    const that = this;
    const token = wx.getStorageSync('access_token');
    const header = {};
    if (token) {
        header['Authorization'] = `Bearer ${token}`;
    }
    
    wx.request({
      url: `${app.globalData.baseUrl}/ads/${id}/`,
      method: 'GET',
      header: header,
      success(res) {
        if(res.statusCode === 200) {
          const ad = that.processAd(res.data);
          that.setData({ ad: ad, loading: false });
          that.checkFavorite(ad.id);
          if (ad.user) {
              that.checkFollow(ad.user);
          }
        } else {
            that.setData({ loading: false });
            console.error('Fetch ad failed:', res);
            wx.showToast({ title: `加载失败: ${res.statusCode}`, icon: 'none' });
        }
      },
      fail(err) {
          that.setData({ loading: false });
          console.error('Fetch ad error:', err);
          wx.showToast({ title: `网络错误: ${err.errMsg || 'Unknown'}`, icon: 'none' });
      }
    });
  },

  checkFavorite(id) {
      const app = getApp();
      const token = wx.getStorageSync('access_token');
      if (!token) return;
      
      wx.request({
          url: `${app.globalData.baseUrl}/favorites/check/?object_id=${id}&content_type=advertisement`,
          header: { 'Authorization': `Bearer ${token}` },
          success: (res) => {
              if (res.statusCode === 200) {
                  this.setData({ isFavorite: res.data.is_favorite });
              }
          }
      });
  },

  toggleFavorite() {
      const app = getApp();
      const token = wx.getStorageSync('access_token');
      if (!token) {
          wx.navigateTo({ url: '/pages/login/login' });
          return;
      }
      
      const id = this.data.ad.id;
      wx.request({
          url: `${app.globalData.baseUrl}/favorites/toggle/`,
          method: 'POST',
          header: { 'Authorization': `Bearer ${token}` },
          data: { object_id: id, content_type: 'advertisement' },
          success: (res) => {
              if (res.statusCode === 200) {
                  this.setData({ isFavorite: res.data.is_favorite });
                  wx.showToast({
                      title: res.data.is_favorite ? '已收藏' : '已取消收藏',
                      icon: 'none'
                  });
              }
          }
      });
  },

  checkFollow(userId) {
      const app = getApp();
      const token = wx.getStorageSync('access_token');
      if (!token) return;
      
      wx.request({
          url: `${app.globalData.baseUrl}/following/check/?followed_id=${userId}`,
          header: { 'Authorization': `Bearer ${token}` },
          success: (res) => {
              if (res.statusCode === 200) {
                  this.setData({ isFollowing: res.data.is_following });
              }
          }
      });
  },

  toggleFollow() {
      const app = getApp();
      const token = wx.getStorageSync('access_token');
      if (!token) {
          wx.navigateTo({ url: '/pages/login/login' });
          return;
      }
      
      const userId = this.data.ad.user;
      wx.request({
          url: `${app.globalData.baseUrl}/following/toggle/`,
          method: 'POST',
          header: { 'Authorization': `Bearer ${token}` },
          data: { followed_id: userId },
          success: (res) => {
              if (res.statusCode === 200) {
                  this.setData({ isFollowing: res.data.is_following });
                  wx.showToast({
                      title: res.data.is_following ? '已关注' : '已取消关注',
                      icon: 'none'
                  });
              }
          }
      });
  },

  contactUser() {
      const token = wx.getStorageSync('access_token');
      if (!token) {
          this.goToLogin();
          return;
      }
      
      const userId = this.data.ad.user;
      const username = this.data.ad.user_name;
      
      wx.navigateTo({
          url: `/pages/messages/chat/chat?targetUserId=${userId}&targetUsername=${username}`
      });
  },

  processAd(item) {
      if (!item) return null;
      const app = getApp();
      const API_BASE = app.globalData.baseUrl;
      const siteRoot = API_BASE.split('/api')[0];
      
      if (item.image) {
        if (!item.image.startsWith('http')) {
            item.image = siteRoot + item.image;
        } else if (item.image.includes('127.0.0.1')) {
            const currentHost = siteRoot.split('://')[1].split(':')[0];
            item.image = item.image.replace('127.0.0.1', currentHost);
        }
      }
      return item;
  }
})
