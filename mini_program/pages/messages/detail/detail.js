const app = getApp();

Page({
  data: {
    id: null,
    message: null,
    replyContent: '',
    submitting: false,
    focusReply: false,
    isFavorite: false,
    isFollowing: false,
    isLoggedIn: false
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ 
          id: options.id,
          focusReply: options.focus === 'true'
      });
      this.fetchDetail(options.id);
    }
  },

  onShow() {
      this.checkLoginStatus();
  },

  checkLoginStatus() {
      const token = wx.getStorageSync('access_token');
      this.setData({ isLoggedIn: !!token });
  },

  goToLogin() {
      wx.navigateTo({ url: '/pages/login/login' });
  },

  onPullDownRefresh() {
      if (this.data.id) {
          this.fetchDetail(this.data.id);
      }
      wx.stopPullDownRefresh();
  },

  fetchDetail(id, showLoading = true) {
    const token = wx.getStorageSync('access_token');
    const header = {};
    if (token) {
        header['Authorization'] = `Bearer ${token}`;
    }

    if (showLoading) {
        wx.showLoading({ title: '加载中' });
    }
    
    wx.request({
      url: `${app.globalData.baseUrl}/messages/${id}/`,
      method: 'GET',
      header: header,
      success: (res) => {
        if (showLoading) wx.hideLoading();
        if (res.statusCode === 200) {
          // Format times if needed, or rely on backend
          this.setData({ message: res.data });
          this.checkFavorite(id);
          if (res.data.user) {
              this.checkFollow(res.data.user);
          }
        } else {
            wx.showToast({ title: '加载失败', icon: 'none' });
        }
      },
      fail: () => {
        if (showLoading) wx.hideLoading();
        wx.showToast({ title: '网络错误', icon: 'none' });
      }
    });
  },

  checkFavorite(id) {
      const token = wx.getStorageSync('access_token');
      if (!token) return;
      
      wx.request({
          url: `${app.globalData.baseUrl}/favorites/check/?object_id=${id}&content_type=membermessage`,
          header: { 'Authorization': `Bearer ${token}` },
          success: (res) => {
              if (res.statusCode === 200) {
                  this.setData({ isFavorite: res.data.is_favorite });
              }
          }
      });
  },

  toggleFavorite() {
      const token = wx.getStorageSync('access_token');
      if (!token) {
          wx.navigateTo({ url: '/pages/login/login' });
          return;
      }
      
      const id = this.data.id;
      wx.request({
          url: `${app.globalData.baseUrl}/favorites/toggle/`,
          method: 'POST',
          header: { 'Authorization': `Bearer ${token}` },
          data: { object_id: id, content_type: 'membermessage' },
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
      const token = wx.getStorageSync('access_token');
      if (!token) {
          wx.navigateTo({ url: '/pages/login/login' });
          return;
      }
      
      const userId = this.data.message.user;
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
          wx.navigateTo({ url: '/pages/login/login' });
          return;
      }
      
      const userId = this.data.message.user;
      const username = this.data.message.user_name;
      
      wx.navigateTo({
          url: `/pages/messages/chat/chat?targetUserId=${userId}&targetUsername=${username}`
      });
  },

  onInputReply(e) {
    this.setData({ replyContent: e.detail.value });
  },

  submitReply() {
    if (!this.data.replyContent.trim()) return;
    
    const token = wx.getStorageSync('access_token');
    if (!token) {
        this.goToLogin();
        return;
    }

    this.setData({ submitting: true });

    wx.request({
      url: `${app.globalData.baseUrl}/message-replies/`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${token}` // Assuming JWT auth
      },
      data: {
        message: this.data.id,
        content: this.data.replyContent
      },
      success: (res) => {
        if (res.statusCode === 201) {
          wx.showToast({ title: '回复成功' });
          this.setData({ replyContent: '', submitting: false });
          this.fetchDetail(this.data.id, false); // Refresh without loading spinner
        } else if (res.statusCode === 401) {
            wx.showToast({ title: '登录过期，请重新登录', icon: 'none' });
            this.setData({ submitting: false });
            setTimeout(() => {
                wx.navigateTo({ url: '/pages/login/login' });
            }, 1500);
        } else {
          console.error(res);
          if (res.statusCode === 400) {
            wx.showToast({ title: '内容可能含违规信息', icon: 'none' });
            this.setData({ submitting: false });
            return;
          }
          wx.showToast({ title: '回复失败: ' + (res.data.detail || '未知错误'), icon: 'none' });
          this.setData({ submitting: false });
        }
      },
      fail: (err) => {
        console.error(err);
        wx.showToast({ title: '网络错误', icon: 'none' });
        this.setData({ submitting: false });
      }
    });
  }
});
