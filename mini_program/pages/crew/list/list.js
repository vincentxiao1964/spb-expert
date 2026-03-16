const app = getApp()

Page({
  data: {
    crewList: [],
    currentTab: 'DOMESTIC',
    searchQuery: '',
    page: 1,
    hasMore: true,
    loading: false,
    t: {}
  },

  onLoad: function (options) {
    this.updateLocales();
    this.loadData(true);
  },

  onShow: function() {
    this.updateLocales();
  },

  updateLocales: function() {
    const i18n = require('../../../utils/i18n.js');
    const lang = i18n.getLocale();
    this.setData({
      t: i18n.locales[lang]
    });
    wx.setNavigationBarTitle({
      title: i18n.t('crew_services')
    });
  },

  onPullDownRefresh: function () {
    this.loadData(true);
  },

  onReachBottom: function () {
    if (this.data.hasMore && !this.data.loading) {
      this.loadData(false);
    }
  },

  switchTab: function (e) {
    const tab = e.currentTarget.dataset.tab;
    if (tab !== this.data.currentTab) {
      this.setData({
        currentTab: tab,
        page: 1,
        hasMore: true,
        crewList: []
      }, () => {
        this.loadData(true);
      });
    }
  },

  onSearch: function (e) {
    this.setData({
      searchQuery: e.detail.value,
      page: 1,
      hasMore: true,
      crewList: []
    }, () => {
      this.loadData(true);
    });
  },

  loadData: function (refresh = false) {
    if (this.data.loading) return;
    this.setData({ loading: true });

    const i18n = require('../../../utils/i18n.js');
    const lang = i18n.getLocale();
    const url = `${app.globalData.baseUrl}/crew/`;
    
    const token = wx.getStorageSync('access_token');
    const header = {
      // 'Accept-Language': lang === 'zh' ? 'zh-hans' : 'en'
    };
    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }

    wx.request({
      url: url,
      method: 'GET',
      data: {
        page: this.data.page,
        nationality_type: this.data.currentTab,
        q: this.data.searchQuery
      },
      header: header,
      success: (res) => {
        if (res.statusCode === 200) {
          const results = res.data.results || res.data;
          const next = res.data.next;
          
          if (refresh) {
            this.setData({
              crewList: results,
              hasMore: !!next,
              loading: false
            });
            wx.stopPullDownRefresh();
          } else {
            this.setData({
              crewList: this.data.crewList.concat(results),
              hasMore: !!next,
              loading: false
            });
          }
        } else if (res.statusCode === 401 && token) {
           // Token expired or invalid, retry as anonymous
           wx.removeStorageSync('access_token');
           this.setData({ loading: false });
           this.loadData(refresh);
        } else {
          this.setData({ loading: false });
          wx.showToast({ title: '加载失败', icon: 'none' });
        }
      },
      fail: (err) => {
        this.setData({ loading: false });
        wx.showToast({ title: '加载失败', icon: 'none' });
      }
    });
  },

  goDetail: function (e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/crew/detail/detail?id=${id}`,
    });
  },

  goCreate: function () {
    // Check login
    if (!wx.getStorageSync('token')) {
      wx.navigateTo({ url: '/pages/login/login' });
      return;
    }
    wx.navigateTo({
      url: '/pages/crew/edit/edit',
    });
  }
})
