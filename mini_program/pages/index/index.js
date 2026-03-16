const app = getApp()
const i18n = require('../../utils/i18n.js');

Page({
  data: {
    listings: [],
    ads: [],
    news: [],
    isLoggedIn: false,
    t: {},
    currentLang: 'zh'
  },
  onLoad: function () {
    this.setData({ currentLang: i18n.getLocale() });
    this.updateLocales();
    this.fetchData();
  },
  onShow: function() {
    this.checkLoginStatus();
    
    // Always get the latest language from storage
    const lang = i18n.getLocale();
    console.log('Index onShow, lang:', lang, 'currentLang:', this.data.currentLang);

    // Update t data and TabBar
    this.setData({
        t: i18n.locales[lang]
    }, () => {
        i18n.updateTabBar(this);
    });

    // Check if we need to refresh data
    if (lang !== this.data.currentLang) {
        console.log('Language changed, refreshing data...');
        
        // Immediately update existing listings with new language
        if (this.data.listings && this.data.listings.length > 0) {
            const updatedListings = this.processListings(this.data.listings);
            this.setData({ listings: updatedListings });
        }

        this.setData({ currentLang: lang });
        this.fetchData();
    }
  },
  
  processListings(listings) {
      if (!listings) return [];
      return listings.map(item => {
          if (item.listing_type) item.listing_type_display = i18n.t(`type_${item.listing_type}`);
          if (item.ship_category) item.ship_category_display = i18n.t(`cat_${item.ship_category}`);
          if (item.status) item.status_display = i18n.t(`status_${item.status}`);
          return item;
      });
  },
  
  updateLocales: function() {
      const lang = i18n.getLocale();
      this.setData({
          t: i18n.locales[lang]
      });
      const title = lang === 'zh' ? '甲板船家 | SPB EXPERT' : 'SPB EXPERT';
      wx.setNavigationBarTitle({ title: title });
  },

  goCrew() {
    wx.navigateTo({
      url: '/pages/crew/list/list'
    });
  },

  goHymartMatch() {
    wx.navigateTo({
      url: '/pages/hymart/match/match'
    });
  },

  preventTouchMove() {},

  switchLanguage() {
      const current = i18n.getLocale();
      const next = current === 'zh' ? 'en' : 'zh';
      i18n.setLocale(next);
      this.updateLocales();
      i18n.updateTabBar(this);
      
      // Refresh data to show correct language content
      this.fetchData();
      
      wx.showToast({
          title: next === 'zh' ? '已切换中文' : 'Switched to English',
          icon: 'none'
      });
  },
  
  checkLoginStatus: function() {
    const token = wx.getStorageSync('access_token');
    this.setData({
      isLoggedIn: !!token
    });
  },

  onAdImageError: function(e) {
    console.error('Ad Image Load Error:', e);
    const index = e.currentTarget.dataset.index;
    const ads = this.data.ads;
    if (ads[index]) {
      // Set image to null to show placeholder
      const key = `ads[${index}].image`;
      this.setData({
        [key]: null
      });
    }
  },

  // 下拉刷新
  onPullDownRefresh: function() {
    this.fetchData();
  },

  fetchListings: function(callback) {
    const that = this;
    const API_BASE = app.globalData.baseUrl;
    let url = `${API_BASE}/listings/?page=1&page_size=5`; // Limit to 5 for homepage

    wx.request({
      url: url,
      success(res) {
        if(res.statusCode === 200) {
          const results = res.data.results || res.data;
          const processed = that.processListings(results);
          that.setData({ listings: processed });
        }
      },
      fail(err) {
        console.error('Fetch listings failed', err);
      },
      complete() {
        if (callback) callback();
      }
    });
  },

  fetchAds: function(callback) {
      const that = this;
      const API_BASE = app.globalData.baseUrl;
      const lang = i18n.getLocale();
      const header = {
          'Accept-Language': lang === 'zh' ? 'zh-hans' : 'en'
      };

      wx.request({
          url: `${API_BASE}/ads/`,
          method: 'GET',
          header: header,
          success(res) {
              if (res.statusCode === 200) {
                const results = res.data.results || res.data;
                const ads = that.processAds(results);
                that.setData({ ads: ads });
              }
          },
          fail(err) {
              console.error('Fetch ads failed', err);
              wx.showToast({
                  title: '加载广告失败',
                  icon: 'none'
              });
          },
          complete() {
              if(callback) callback();
          }
      });
  },

  processAds(ads) {
    if (!ads) return [];
    const API_BASE = app.globalData.baseUrl;
    const siteRoot = API_BASE.split('/api')[0];
    
    return ads.map(ad => {
        if (ad.image) {
            if (!ad.image.startsWith('http')) {
                ad.image = siteRoot + ad.image;
            } else if (ad.image.includes('127.0.0.1')) {
                const currentHost = siteRoot.split('://')[1].split(':')[0];
                ad.image = ad.image.replace('127.0.0.1', currentHost);
            }
        }
        return ad;
    });
  },

  fetchNews: function(callback) {
      const that = this;
      const API_BASE = app.globalData.baseUrl;
      wx.request({
          url: `${API_BASE}/news/?page=1&page_size=3`,
          success(res) {
              if (res.statusCode === 200) {
                const results = res.data.results || res.data;
                that.setData({ news: results });
              }
          },
          fail(err) {
              console.error('Fetch news failed', err);
              wx.showToast({
                  title: '加载资讯失败',
                  icon: 'none'
              });
          },
          complete() {
              if(callback) callback();
          }
      });
  },

  fetchData: function() {
      wx.showLoading({ title: '加载中' });
      
      const that = this;
      let completed = 0;
      const total = 3; // ads, listings, news
      
      const checkComplete = () => {
          completed++;
          if (completed >= total) {
              wx.hideLoading();
              wx.stopPullDownRefresh();
          }
      };

            // Force mock data if network fails (for debugging)
            const useMock = false; 

            if (useMock) {
          this.setData({
              ads: [{id: 1, title: 'Test Ad', image: null}],
              listings: [{id: 1, listing_type: 'SELL', ship_category: 'SELF_PROPELLED', dwt: 5000, build_year: 2020, status: 'APPROVED'}],
              news: [{id: 1, title: 'Test News', created_at: '2023-01-01'}]
          });
          wx.hideLoading();
          return;
      }

      this.fetchAds(checkComplete);
      this.fetchListings(checkComplete);
      this.fetchNews(checkComplete);
  },

  navigateToListing: function(e) {
      const type = e.currentTarget.dataset.type;
      app.globalData.listingType = type;
      wx.switchTab({
          url: '/pages/listings/list/list'
      });
  },

  goCrew: function() {
      wx.navigateTo({
          url: '/pages/crew/list/list'
      });
  },

  goAdDetail: function(e) {
      const id = e.currentTarget.dataset.id;
      wx.navigateTo({
          url: `/pages/ads/detail/detail?id=${id}`
      });
  },

  goListingDetail: function(e) {
      const id = e.currentTarget.dataset.id;
      wx.navigateTo({
          url: `/pages/listings/detail/detail?id=${id}`
      });
  },

  viewNews: function(e) {
      const id = e.currentTarget.dataset.id;
      wx.navigateTo({
          url: `/pages/news/detail/detail?id=${id}`
      });
  }
})
