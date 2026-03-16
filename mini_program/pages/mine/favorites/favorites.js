const app = getApp();

Page({
  data: {
    listings: [],
    page: 1,
    hasMore: true,
    isLoadingMore: false,
    isRefreshing: false
  },

  onShow() {
    this.fetchListings(true);
  },

  fetchListings(reset = false) {
    if (!this.data.hasMore && !reset) return;
    if (this.data.isLoadingMore) return;

    this.setData({ isLoadingMore: true });

    const API_BASE = app.globalData.baseUrl;
    const token = wx.getStorageSync('access_token');
    
    if (!token) {
        wx.redirectTo({ url: '/pages/login/login' });
        return;
    }

    let url = `${API_BASE}/favorites/?page=${this.data.page}`;
    
    wx.request({
      url: url,
      header: {
          'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const newItems = this.processListings(res.data.results || res.data);
          const hasMore = !!res.data.next;
          
          this.setData({
            listings: reset ? newItems : [...this.data.listings, ...newItems],
            page: this.data.page + 1,
            hasMore: hasMore,
            isLoadingMore: false,
            isRefreshing: false
          });
        } else if (res.statusCode === 401) {
            wx.removeStorageSync('access_token');
            wx.redirectTo({ url: '/pages/login/login' });
        } else {
            this.setData({ isLoadingMore: false, isRefreshing: false });
        }
      },
      fail: (err) => {
        console.error('Fetch favorites failed', err);
        this.setData({ isLoadingMore: false, isRefreshing: false });
        wx.showToast({ title: '加载失败', icon: 'none' });
      }
    });
  },

  processListings(items) {
      if (!items) return [];
      const API_BASE = app.globalData.baseUrl;
      const siteRoot = API_BASE.split('/api')[0];
      
      return items.map(item => {
          // Flatten structure for easier binding
          if (item.content_object) {
              const detail = item.content_object;
              item.type = item.content_type_model; // shiplisting, marketnews, advertisement, membermessage
              item.detail = detail;
              
              // Process images for different types
              if (item.type === 'shiplisting') {
                  if (detail.images && detail.images.length > 0) {
                      detail.images = detail.images.map(img => {
                          if (img.image) {
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
                  // Date formatting
                  if (detail.created_at) {
                      item.created_at_formatted = detail.created_at.split('T')[0];
                  }
              } else if (item.type === 'marketnews' || item.type === 'advertisement') {
                  if (detail.image) {
                      if (!detail.image.startsWith('http')) {
                          detail.image = siteRoot + detail.image;
                      } else if (detail.image.includes('127.0.0.1')) {
                          const currentHost = siteRoot.split('://')[1].split(':')[0];
                          detail.image = detail.image.replace('127.0.0.1', currentHost);
                      }
                  }
                  if (detail.created_at) {
                      item.created_at_formatted = detail.created_at.split('T')[0];
                  }
              } else if (item.type === 'membermessage') {
                  if (detail.created_at) {
                      item.created_at_formatted = detail.created_at.split('T')[0] + ' ' + detail.created_at.split('T')[1].substring(0, 5);
                  }
              }
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
    const item = e.currentTarget.dataset.item;
    const type = item.type;
    const id = item.detail.id;
    
    let url = '';
    if (type === 'shiplisting') {
        url = `/pages/detail/detail?id=${id}`;
    } else if (type === 'marketnews') {
        url = `/pages/news/detail/detail?id=${id}`;
    } else if (type === 'advertisement') {
        url = `/pages/ads/detail/detail?id=${id}`;
    } else if (type === 'membermessage') {
        url = `/pages/messages/detail/detail?id=${id}`;
    }
    
    if (url) {
        wx.navigateTo({ url });
    }
  }
});
