const app = getApp()
const i18n = require('../../../utils/i18n.js');

Page({
  data: {
    listing: null,
    listingId: null,
    loading: true,
    isFavorite: false,
    isFollowing: false,
    isLoggedIn: false,
    t: {}
  },
  onLoad: function (options) {
    this.checkLoginStatus();
    this.updateLocales();
    const id = options.id
    if (id) {
      this.setData({ listingId: id });
      this.fetchListingDetail(id)
    }
  },
  onShow: function() {
    this.checkLoginStatus();
    this.updateLocales();
    i18n.updateTabBar(this);
    if (this.data.listingId) {
        this.fetchListingDetail(this.data.listingId);
    }
  },
  checkLoginStatus: function() {
      const token = wx.getStorageSync('access_token');
      this.setData({ isLoggedIn: !!token });
  },
  updateLocales: function() {
      const lang = i18n.getLocale();
      this.setData({
          t: i18n.locales[lang]
      });
  },
  fetchListingDetail: function (id, isRetry = false) {
    const token = wx.getStorageSync('access_token');
    const header = {};
    if (token) {
        header['Authorization'] = `Bearer ${token}`;
    }
    
    // Set Accept-Language header based on current locale
    const lang = i18n.getLocale();
    // header['Accept-Language'] = lang === 'zh' ? 'zh-hans' : 'en';

    wx.request({
      url: `${app.globalData.baseUrl}/listings/${id}/`,
      method: 'GET',
      header: header,
      success: (res) => {
        if (res.statusCode === 200) {
          const listing = this.processListing(res.data);
          // Manually ensure unique_id is preserved if processListing doesn't (though it should)
          if (!listing.unique_id && res.data.unique_id) {
              listing.unique_id = res.data.unique_id;
          }
          this.setData({
            listing: listing,
            loading: false
          });
          this.checkFavorite(listing.id);
          if (listing.user) {
              this.checkFollow(listing.user);
          }
        } else if (res.statusCode === 401 && !isRetry) {
            // Token invalid or expired, retry without token
            wx.removeStorageSync('access_token');
            this.fetchListingDetail(id, true);
        } else {
            this.setData({ loading: false });
            console.error('Fetch detail failed:', res);
            wx.showToast({
                title: `获取失败: ${res.statusCode}`,
                icon: 'none',
                duration: 3000
            });
        }
      },
      fail: (err) => {
        this.setData({ loading: false })
        console.error('Fetch detail error:', err);
        wx.showToast({
          title: `网络错误: ${err.errMsg || 'Unknown'}`,
          icon: 'none',
          duration: 3000
        })
      }
    })
  },

  processListing(item) {
      if (!item) return null;
      const API_BASE = app.globalData.baseUrl;
      const siteRoot = API_BASE.split('/api')[0];
      const lang = i18n.getLocale();

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
      
      // Process images
      if (item.images && item.images.length > 0) {
          item.images = item.images.map(img => {
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
      
      return item;
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

  initiateTransaction() {
      const that = this;
      const listing = this.data.listing;
      if (!listing) return;

      const title = `${listing.ship_category_display} - ${listing.dwt}t`;

      wx.showModal({
          title: that.data.t.initiate_transaction,
          content: `${that.data.t.confirm_transaction}: ${title}?`,
          confirmText: that.data.t.confirm_transaction,
          cancelText: that.data.t.cancel || 'Cancel',
          success(res) {
              if (res.confirm) {
                  that.createTransaction(listing.id);
              }
          }
      });
  },

  createTransaction(listingId) {
      const token = wx.getStorageSync('access_token');
      if (!token) {
          wx.navigateTo({
              url: `/pages/login/login?next=${encodeURIComponent('/pages/detail/detail?id=' + listingId)}`
          });
          return;
      }

      wx.showLoading({ title: 'Processing...' });
      
      wx.request({
          url: `${app.globalData.baseUrl}/transactions/`,
          method: 'POST',
          header: { 'Authorization': `Bearer ${token}` },
          data: { listing: listingId },
          success: (res) => {
              wx.hideLoading();
              if (res.statusCode === 201) {
                  wx.showToast({ title: 'Success', icon: 'success' });
                  // Navigate to transaction detail
                  wx.navigateTo({
                      url: `/pages/transactions/detail/detail?id=${res.data.id}`
                  });
              } else {
                  wx.showToast({ 
                      title: res.data.error || 'Failed', 
                      icon: 'none' 
                  });
              }
          },
          fail: (err) => {
              wx.hideLoading();
              wx.showToast({ title: 'Network Error', icon: 'none' });
          }
      });
  },

  onPublish() {
    const token = wx.getStorageSync('access_token');
    if (!token) {
        this.goToLogin();
        return;
    }
    wx.navigateTo({
        url: '/pages/admin/ships/edit/edit'
    });
  },

  generatePoster() {
      const that = this;
      const listing = this.data.listing;
      if (!listing) return;

      wx.showLoading({ title: that.data.t.poster_saving || 'Generating...' });

      // 1. Get Main Image URL
      let imageUrl = '';
      if (listing.images && listing.images.length > 0) {
          imageUrl = listing.images[0].image;
      }

      // 2. Download Image (if exists)
      const downloadImage = new Promise((resolve, reject) => {
          if (!imageUrl) {
              resolve(null);
              return;
          }
          
          // Handle localhost for dev environment if needed, but usually we need accessible URL
          // If it is 127.0.0.1, it might fail on real device, but works in simulator
          
          wx.downloadFile({
              url: imageUrl,
              success: (res) => {
                  if (res.statusCode === 200) {
                      resolve(res.tempFilePath);
                  } else {
                      resolve(null);
                  }
              },
              fail: (err) => {
                  console.error('Download failed', err);
                  resolve(null);
              }
          });
      });

      downloadImage.then(localImagePath => {
          that.drawPoster(listing, localImagePath);
      });
  },

  drawPoster(listing, localImagePath) {
      const that = this;
      const ctx = wx.createCanvasContext('posterCanvas');
      const width = 375; // Fixed canvas width
      const height = 550; // Fixed canvas height
      const padding = 20;

      // Background
      ctx.setFillStyle('#ffffff');
      ctx.fillRect(0, 0, width, height);

      // Header (Title)
      ctx.setFontSize(22);
      ctx.setFillStyle('#333333');
      ctx.setTextAlign('left');
      
      let title = '';
      if (listing.listing_type_display) title += listing.listing_type_display + ' ';
      if (listing.ship_category_display) title += listing.ship_category_display;
      if (listing.dwt) title += ' ' + listing.dwt + 't';
      
      this.wrapText(ctx, title, padding, 50, width - 40, 30);

      // Info
      ctx.setFontSize(16);
      ctx.setFillStyle('#666666');
      let y = 100; // Start Y position
      
      const drawLine = (label, value) => {
          if (value) {
              ctx.fillText(`${label}: ${value}`, padding, y);
              y += 26;
          }
      };

      drawLine(that.data.t.length || 'Length', listing.length ? listing.length + 'm' : '');
      drawLine(that.data.t.width || 'Width', listing.width ? listing.width + 'm' : '');
      drawLine(that.data.t.build_year || 'Built', listing.build_year);
      drawLine(that.data.t.status || 'Status', listing.status_display);
      
      if (listing.price) {
          ctx.setFillStyle('#ff5722');
          ctx.setFontSize(18);
          ctx.fillText(`${that.data.t.price || 'Price'}: ${listing.price}`, padding, y + 10);
          y += 35;
      }

      // Image
      if (localImagePath) {
          y += 10;
          // Draw image (cover aspect)
          // For simplicity, just stretch or fit. 
          // Ideally we calculate aspect ratio.
          ctx.drawImage(localImagePath, padding, y, width - 40, 220);
          y += 240;
      } else {
          y += 100;
      }

      // Footer
      ctx.setFontSize(14);
      ctx.setFillStyle('#999999');
      const footerText = 'Shared from Barge Expert Mini Program';
      const footerX = (width - ctx.measureText(footerText).width) / 2;
      ctx.fillText(footerText, footerX, height - 30);

      // Draw
      ctx.draw(false, () => {
          setTimeout(() => {
              wx.canvasToTempFilePath({
                  canvasId: 'posterCanvas',
                  success: (res) => {
                      that.savePoster(res.tempFilePath);
                  },
                  fail: (err) => {
                      wx.hideLoading();
                      wx.showToast({ title: 'Canvas Error', icon: 'none' });
                  }
              }, that);
          }, 200);
      });
  },

  savePoster(tempFilePath) {
      const that = this;
      wx.saveImageToPhotosAlbum({
          filePath: tempFilePath,
          success: () => {
              wx.hideLoading();
              wx.showToast({
                  title: that.data.t.poster_success || 'Saved',
                  icon: 'success'
              });
          },
          fail: (err) => {
              wx.hideLoading();
              if (err.errMsg.includes('auth')) {
                  wx.showModal({
                      title: 'Permission Required',
                      content: 'Please allow access to save photos',
                      success: (res) => {
                          if (res.confirm) wx.openSetting();
                      }
                  });
              } else {
                  // Often fails in simulator if not handled right, but okay on device
                  wx.showToast({ title: 'Save Failed', icon: 'none' });
              }
          }
      });
  },

  wrapText(ctx, text, x, y, maxWidth, lineHeight) {
      if (!text) return;
      let arr = text.split('');
      let line = '';
      
      for (let n = 0; n < arr.length; n++) {
        let testLine = line + arr[n];
        let metrics = ctx.measureText(testLine);
        let testWidth = metrics.width;
        if (testWidth > maxWidth && n > 0) {
          ctx.fillText(line, x, y);
          line = arr[n];
          y += lineHeight;
        } else {
          line = testLine;
        }
      }
      ctx.fillText(line, x, y);
  },
  
  onEdit() {
      const id = this.data.listing.id;
      wx.navigateTo({
          url: `/pages/admin/ships/edit/edit?id=${id}`
      });
  },

  onDelete() {
      const that = this;
      wx.showModal({
          title: '确认删除',
          content: '确定要删除这条船源信息吗？此操作不可恢复。',
          success(res) {
              if (res.confirm) {
                  that.deleteListing();
              }
          }
      });
  },

  checkFavorite(id) {
      const token = wx.getStorageSync('access_token');
      if (!token) return;
      
      wx.request({
          url: `${app.globalData.baseUrl}/favorites/check/?object_id=${id}&content_type=shiplisting`,
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
          this.goToLogin();
          return;
      }
      
      const id = this.data.listing.id;
      wx.request({
          url: `${app.globalData.baseUrl}/favorites/toggle/`,
          method: 'POST',
          header: { 'Authorization': `Bearer ${token}` },
          data: { object_id: id, content_type: 'shiplisting' },
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
      
      const userId = this.data.listing.user;
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
      
      // Track contact view
      const id = this.data.listing.id;
      wx.request({
          url: `${app.globalData.baseUrl}/listings/${id}/track_contact/`,
          method: 'POST',
          header: { 'Authorization': `Bearer ${token}` }
      });

      const userId = this.data.listing.user;
      const username = this.data.listing.user_name;
      
      // Navigate to chat page
      wx.navigateTo({
          url: `/pages/messages/chat/chat?targetUserId=${userId}&targetUsername=${username}`
      });
  },

  deleteListing() {
      const id = this.data.listing.id;
      const token = wx.getStorageSync('access_token');
      const app = getApp();
      
      wx.showLoading({ title: '删除中...' });
      
      wx.request({
          url: `${app.globalData.baseUrl}/listings/${id}/`,
          method: 'DELETE',
          header: {
              'Authorization': `Bearer ${token}`
          },
          success: (res) => {
              wx.hideLoading();
              if (res.statusCode === 204) {
                  wx.showToast({
                      title: '删除成功',
                      icon: 'success'
                  });
                  // Refresh list page if possible, or just go back
                  setTimeout(() => {
                      const pages = getCurrentPages();
                      const prevPage = pages[pages.length - 2];
                      if (prevPage && prevPage.fetchListings) {
                          prevPage.setData({ page: 1, listings: [] }, () => {
                            prevPage.fetchListings(true);
                          });
                      }
                      wx.navigateBack();
                  }, 1500);
              } else {
                  wx.showToast({
                      title: '删除失败',
                      icon: 'none'
                  });
                  console.error('Delete failed:', res);
              }
          },
          fail: (err) => {
              wx.hideLoading();
              wx.showToast({
                  title: '网络错误',
                  icon: 'none'
              });
              console.error('Delete error:', err);
          }
      });
  }
})
