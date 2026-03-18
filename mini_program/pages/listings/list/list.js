const app = getApp();
const i18n = require('../../../utils/i18n.js');

Page({
  data: {
    activeTab: 'all',
    listings: [],
    page: 1,
    hasMore: true,
    isLoadingMore: false,
    isRefreshing: false,
    t: {},
    currentLang: 'zh'
  },

  onLoad(options) {
    this.setData({ currentLang: i18n.getLocale() });
    this.updateLocales();
    if (options.type) {
      this.setData({ activeTab: options.type });
    }
    this.fetchListings(true);
  },

  onShow() {
    this.updateLocales();
    i18n.updateTabBar(this);

    // Check for global listingType intent (from homepage buttons)
    if (app.globalData.listingType) {
        const type = app.globalData.listingType;
        app.globalData.listingType = null; // Clear it
        this.setData({ 
            activeTab: type,
            listings: [],
            page: 1,
            hasMore: true
        }, () => {
            this.fetchListings(true);
        });
        return; // Skip default loading logic below
    }
    
    const lang = i18n.getLocale();
    if (lang !== this.data.currentLang) {
        this.setData({ 
          currentLang: lang,
          listings: [], 
          page: 1, 
          hasMore: true 
        }, () => {
          this.fetchListings(true);
        });
    } else if (this.data.listings.length === 0) {
        this.fetchListings(true);
    }
  },

  updateLocales() {
      const lang = i18n.getLocale();
      this.setData({
          t: i18n.locales[lang]
      });
      wx.setNavigationBarTitle({ title: i18n.locales[lang]['tabbar_ships'] });
  },

  onTabChange(e) {
    const type = e.currentTarget.dataset.type;
    if (this.data.activeTab === type) return;
    
    this.setData({ 
      activeTab: type,
      listings: [],
      page: 1,
      hasMore: true
    }, () => {
      this.fetchListings(true);
    });
  },

  onRefresherRefresh() {
    this.setData({ isRefreshing: true });
    this.fetchListings(true);
  },

  preventTouchMove() {},


  fetchListings(reset = false) {
    if (!this.data.hasMore && !reset) return;
    if (this.data.isLoadingMore) return;

    this.setData({ isLoadingMore: true });

    const API_BASE = app.globalData.baseUrl;
    let url = `${API_BASE}/listings/?page=${this.data.page}`;
    
    // Add filters
    const token = wx.getStorageSync('access_token');
    let header = {};
    
    if (token) {
        header['Authorization'] = `Bearer ${token}`;
    }

    if (this.data.activeTab === 'my_listings') {
       url += `&manage=true`;
    } else if (this.data.activeTab === 'drafts') {
       url += `&manage=true&status=PENDING`;
    } else if (this.data.activeTab === 'favorites') {
       url = `${API_BASE}/favorites/`;
    } else if (this.data.activeTab !== 'all') {
       url += `&listing_type=${this.data.activeTab}`;
    }

    // Set Accept-Language header based on current locale
    const lang = i18n.getLocale();
    // header['Accept-Language'] = lang === 'zh' ? 'zh-hans' : 'en';

    console.log('Fetching listings:', { url, hasToken: !!token, activeTab: this.data.activeTab });
    
    wx.showNavigationBarLoading();

    wx.request({
      url: url,
      method: 'GET',
      header: header,
      timeout: 15000,
      success: (res) => {
        console.log('Fetch response:', res.statusCode, res.data);
        wx.hideNavigationBarLoading();
        
        if (res.statusCode === 200) {
          // Support both paginated and flat array responses
          const rawItems = Array.isArray(res.data) ? res.data : (res.data.results || []);
          const newItems = this.processListings(rawItems); 
          const hasMore = !!res.data.next; 
          
          this.setData({
            listings: reset ? newItems : [...this.data.listings, ...newItems],
            page: this.data.page + 1,
            hasMore: hasMore,
            isLoadingMore: false,
            isRefreshing: false
          });
          wx.stopPullDownRefresh();
        } else if (res.statusCode === 401) {
            // Token expired or invalid
            console.log('Token invalid (401), retrying without token...');
            wx.removeStorageSync('access_token');
            
            // Retry only if we had a token to begin with (to avoid infinite loop)
            if (token) {
                // Reset page to 1 for retry to ensure fresh start
                this.setData({ page: 1 });
                this.fetchListings(true);
            } else {
                this.setData({ isLoadingMore: false, isRefreshing: false });
                wx.stopPullDownRefresh();
            }
        } else {
            console.error('Fetch failed with status:', res.statusCode);
            wx.hideNavigationBarLoading();
            this.setData({ isLoadingMore: false, isRefreshing: false });
            wx.stopPullDownRefresh();
            wx.showToast({ title: '加载失败: ' + res.statusCode, icon: 'none' });
        }
      },
      fail: (err) => {
        console.error('Fetch listings request failed', err);
        wx.hideNavigationBarLoading();
        this.setData({ isLoadingMore: false, isRefreshing: false });
        wx.stopPullDownRefresh();
        const msg = err && err.errMsg && err.errMsg.indexOf('timeout') !== -1 ? '请求超时，请稍后重试' : '网络请求失败';
        wx.showToast({ title: msg, icon: 'none' });
      }
    });
  },

  processListings(items) {
      if (!items) return [];
      const API_BASE = app.globalData.baseUrl;
      const siteRoot = API_BASE.split('/api')[0];
      const lang = i18n.getLocale();
      
      return items.map(item => {
          // If it's a favorite object, extract the listing detail
          if (item.listing_detail) {
              item = { ...item.listing_detail, fav_created_at: item.created_at };
          }

          // Translate Enums
          if (item.listing_type) {
              item.listing_type_display = i18n.t(`type_${item.listing_type}`);
          }
          if (item.ship_category) {
              item.ship_category_display = i18n.t(`cat_${item.ship_category}`);
          }
          if (item.status) {
              item.status_display = i18n.t(`status_${item.status}`);
          }

          // Handle i18n for description
          if (lang === 'en' && item.description_en) {
              item.display_description = item.description_en;
          } else {
              item.display_description = item.description;
          }

          // Process images
          if (item.images && item.images.length > 0) {
              item.images = item.images.map(img => {
                  if (img.image) {
                    // Force HTTPS only for production
                    if (app.globalData.env === 'prod' && img.image.startsWith('http:')) {
                        img.image = img.image.replace('http:', 'https:');
                    }
                    
                    if (!img.image.startsWith('http')) {
                        img.image = siteRoot + img.image;
                    } else if (img.image.includes('127.0.0.1')) {
                        const currentHost = siteRoot.split('://')[1].split(':')[0];
                        img.image = img.image.replace('127.0.0.1', currentHost);
                    }
                  }
                  return img;
              });
          }
          
          // Format date (simple version)
          if (item.created_at) {
              item.created_at_formatted = item.created_at.split('T')[0];
          }
          
          return item;
      });
  },

  onPullDownRefresh() {
    this.setData({
      isRefreshing: true,
      page: 1,
      hasMore: true
    }, () => {
      this.fetchListings(true);
    });
  },

  onReachBottom() {
    this.fetchListings();
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/listings/detail/detail?id=${id}`
    });
  },

  goPost() {
    const token = wx.getStorageSync('access_token');
    if (!token) {
        wx.navigateTo({
            url: '/pages/login/login'
        });
        return;
    }
    wx.navigateTo({
        url: '/pages/admin/ships/edit/edit'
    });
  }
});
