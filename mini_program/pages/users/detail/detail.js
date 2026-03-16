const app = getApp()
const i18n = require('../../../utils/i18n.js');

Page({
  data: {
    userId: null,
    user: null,
    loading: true,
    isFollowing: false,
    followId: null,
    t: {},
    currentLang: 'zh'
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ userId: options.id });
    }
    this.updateLocales();
  },

  onShow() {
    this.updateLocales();
    if (this.data.userId) {
      this.fetchProfile();
    }
  },

  updateLocales() {
    const lang = i18n.getLocale();
    this.setData({
      currentLang: lang,
      t: i18n.locales[lang]
    });
    wx.setNavigationBarTitle({ title: i18n.locales[lang]['user_profile'] || 'User Profile' });
  },

  fetchProfile() {
    const token = wx.getStorageSync('access_token');
    if (!token) return;

    wx.request({
      url: `${app.globalData.baseUrl}/users/${this.data.userId}/profile/`,
      method: 'GET',
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        if (res.statusCode === 200) {
          const data = res.data;
          this.setData({
            user: data,
            isFollowing: data.is_following,
            followId: data.follow_id,
            loading: false
          });
        }
      },
      fail: () => {
        this.setData({ loading: false });
        wx.showToast({ title: 'Load failed', icon: 'none' });
      }
    });
  },

  toggleFollow() {
    const token = wx.getStorageSync('access_token');
    if (!token) return;

    if (this.data.isFollowing) {
      // Unfollow
      if (!this.data.followId) return;
      
      wx.showModal({
        title: this.data.t['confirm'] || 'Confirm',
        content: this.data.t['confirm_unfollow'] || 'Unfollow this user?',
        success: (res) => {
          if (res.confirm) {
            wx.request({
              url: `${app.globalData.baseUrl}/following/${this.data.followId}/`,
              method: 'DELETE',
              header: { 'Authorization': `Bearer ${token}` },
              success: (res) => {
                if (res.statusCode === 204) {
                  this.setData({
                    isFollowing: false,
                    followId: null,
                    'user.followers_count': this.data.user.followers_count - 1
                  });
                  wx.showToast({ title: 'Unfollowed', icon: 'success' });
                }
              }
            });
          }
        }
      });
    } else {
      // Follow
      wx.request({
        url: `${app.globalData.baseUrl}/following/`,
        method: 'POST',
        header: { 'Authorization': `Bearer ${token}` },
        data: { followed: this.data.userId },
        success: (res) => {
          if (res.statusCode === 201) {
            this.setData({
              isFollowing: true,
              followId: res.data.id,
              'user.followers_count': this.data.user.followers_count + 1
            });
            wx.showToast({ title: 'Followed', icon: 'success' });
          }
        }
      });
    }
  },

  navigateToChat() {
    const user = this.data.user;
    if (!user) return;
    
    wx.navigateTo({
      url: `/pages/messages/chat/chat?targetUserId=${user.id}&targetUsername=${user.username}`
    });
  }
});
