const app = getApp()
const i18n = require('../../../utils/i18n.js');

Page({
  data: {
    news: null,
    loading: true,
    isFavorite: false,
    isFollowing: false,
    t: {}
  },
  onLoad(options) {
    this.updateLocales();
    const id = options.id
    if (id) {
      this.fetchNewsDetail(id)
    } else {
      this.setData({ loading: false })
      wx.showToast({ title: '缺少新闻ID', icon: 'none' })
    }
  },
  onShow() {
      this.updateLocales();
      i18n.updateTabBar(this);
      // Refresh data when page is shown (e.g. after login)
      if (this.data.news && this.data.news.id) {
          this.fetchNewsDetail(this.data.news.id);
      }
  },
  updateLocales() {
      const lang = i18n.getLocale();
      this.setData({
          t: i18n.locales[lang]
      });
  },
  fetchNewsDetail(id) {
    const token = wx.getStorageSync('access_token');
    const header = {};
    if (token) {
        header['Authorization'] = `Bearer ${token}`;
    }

    // Set Accept-Language header based on current locale
    const lang = i18n.getLocale();
    header['Accept-Language'] = lang === 'zh' ? 'zh-hans' : 'en';

    wx.request({
      url: `${app.globalData.baseUrl}/news/${id}/`,
      method: 'GET',
      header: header,
      success: (res) => {
        if (res.statusCode === 200) {
          const news = this.processNews(res.data);
          this.setData({ news: news, loading: false });
          this.checkFavorite(news.id);
          if (news.user) {
              this.checkFollow(news.user);
          }
        } else {
          this.setData({ loading: false })
          console.error('Fetch news failed:', res);
          wx.showToast({ title: `加载失败: ${res.statusCode}`, icon: 'none' })
        }
      },
      fail: (err) => {
        this.setData({ loading: false })
        console.error('Fetch news error:', err);
        wx.showToast({ title: `网络错误: ${err.errMsg || 'Unknown'}`, icon: 'none' })
      }
    })
  },

  checkFavorite(id) {
      const token = wx.getStorageSync('access_token');
      if (!token) return;
      
      wx.request({
          url: `${app.globalData.baseUrl}/favorites/check/?object_id=${id}&content_type=marketnews`,
          header: { 'Authorization': `Bearer ${token}` },
          success: (res) => {
              if (res.statusCode === 200) {
                  this.setData({ isFavorite: res.data.is_favorite });
              }
          }
      });
  },

  goToLogin() {
    const pages = getCurrentPages();
    const currentPage = pages[pages.length - 1];
    const url = currentPage.route;
    const options = currentPage.options;
    let path = '/' + url;
    const keys = Object.keys(options);
    if (keys.length > 0) {
        path += '?' + keys.map(key => `${key}=${options[key]}`).join('&');
    }
    wx.navigateTo({
      url: `/pages/login/login?next=${encodeURIComponent(path)}`
    });
  },

  toggleFavorite() {
      const token = wx.getStorageSync('access_token');
      if (!token) {
          this.goToLogin();
          return;
      }
      
      const id = this.data.news.id;
      wx.request({
          url: `${app.globalData.baseUrl}/favorites/toggle/`,
          method: 'POST',
          header: { 'Authorization': `Bearer ${token}` },
          data: { object_id: id, content_type: 'marketnews' },
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
          this.goToLogin();
          return;
      }
      
      const userId = this.data.news.user;
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
      
      const userId = this.data.news.user;
      const username = this.data.news.user_name;
      
      wx.navigateTo({
          url: `/pages/messages/chat/chat?targetUserId=${userId}&targetUsername=${username}`
      });
  },
  
  processNews(item) {
      if (!item) return null;
      const API_BASE = app.globalData.baseUrl;
      const siteRoot = API_BASE.split('/api')[0];
      
      // Process image
      if (item.image) {
        if (!item.image.startsWith('http')) {
            item.image = siteRoot + item.image;
        } else if (item.image.includes('127.0.0.1')) {
            const currentHost = siteRoot.split('://')[1].split(':')[0];
            item.image = item.image.replace('127.0.0.1', currentHost);
        }
      }
      
      return item;
  },

  handleEdit() {
      wx.navigateTo({
          url: `/pages/admin/news/edit/edit?id=${this.data.news.id}`
      });
  },

  handleDelete() {
      const that = this;
      wx.showModal({
          title: '提示',
          content: '确定要删除这条资讯吗？',
          success(res) {
              if (res.confirm) {
                  const token = wx.getStorageSync('access_token');
                  wx.request({
                      url: `${app.globalData.baseUrl}/news/${that.data.news.id}/`,
                      method: 'DELETE',
                      header: { 'Authorization': `Bearer ${token}` },
                      success: (res) => {
                          if (res.statusCode === 204) {
                              wx.showToast({ title: '删除成功' });
                              setTimeout(() => {
                                  wx.navigateBack();
                              }, 1500);
                          } else {
                              wx.showToast({ title: '删除失败', icon: 'none' });
                          }
                      }
                  });
              }
          }
      });
  }
})
