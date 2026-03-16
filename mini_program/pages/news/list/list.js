const app = getApp()
const i18n = require('../../../utils/i18n.js');

Page({
  data: {
    newsList: [],
    page: 1,
    hasMore: true,
    loading: false,
    t: {},
    currentLang: 'zh'
  },
  
  onLoad() {
    this.setData({ currentLang: i18n.getLocale() });
    this.updateLocales();
    this.fetchNews(true);
  },

  onShow() {
    this.updateLocales();
    i18n.updateTabBar(this);
    
    const lang = i18n.getLocale();
    if (lang !== this.data.currentLang) {
        this.setData({ 
          currentLang: lang,
          newsList: [], 
          page: 1, 
          hasMore: true 
        }, () => {
          this.fetchNews(true);
        });
    }
  },

  updateLocales() {
      const lang = i18n.getLocale();
      this.setData({
          t: i18n.locales[lang]
      });
      wx.setNavigationBarTitle({ title: i18n.locales[lang]['tabbar_news'] });
  },
  
  onRefresherRefresh() {
    this.setData({ isRefreshing: true });
    this.fetchNews(true);
  },

  preventTouchMove() {},
  
  onReachBottom() {
    this.fetchNews(false);
  },
  
  fetchNews(refresh) {
    if (this.data.loading || (!refresh && !this.data.hasMore)) return;
    
    this.setData({ loading: true });
    
    if (refresh) {
      this.setData({ page: 1, hasMore: true });
    }
    
    // Set Accept-Language header based on current locale
    const i18n = require('../../../utils/i18n.js');
    const lang = i18n.getLocale();
    const header = {
        // 'Accept-Language': lang === 'zh' ? 'zh-hans' : 'en'
    };

    wx.request({
      url: `${app.globalData.baseUrl}/news/`,
      method: 'GET',
      header: header,
      data: {
        page: this.data.page
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const results = res.data.results || res.data;
          const processedResults = results.map(this.processNews);
          
          this.setData({
            newsList: refresh ? processedResults : [...this.data.newsList, ...processedResults],
            page: this.data.page + 1,
            hasMore: !!res.data.next,
            loading: false
          });
        } else {
          this.setData({ loading: false });
          wx.showToast({ title: '加载失败', icon: 'none' });
          wx.showModal({
            title: '加载失败',
            content: '状态码: ' + res.statusCode,
            showCancel: false
          });
        }
      },
      fail: (err) => {
        this.setData({ loading: false, isRefreshing: false });
        wx.showToast({ title: '网络错误', icon: 'none' });
        wx.showModal({
            title: '网络错误',
            content: '错误信息: ' + JSON.stringify(err),
            showCancel: false
        });
      },
      complete: () => {
        if (refresh) wx.stopPullDownRefresh();
      }
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

  viewNews(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/news/detail/detail?id=${id}`
    });
  },

  onPublish() {
    // Check if user is logged in
    const token = wx.getStorageSync('access_token');
    if (!token) {
        wx.navigateTo({ url: '/pages/login/login' });
        return;
    }
    // Navigate to admin edit page (which handles both create and edit)
    wx.navigateTo({
        url: '/pages/admin/news/edit/edit'
    });
  }
})
