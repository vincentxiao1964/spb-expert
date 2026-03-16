const app = getApp()

Page({
  data: {
    crew: null,
    id: null,
    t: {}
  },

  onLoad: function (options) {
    this.updateLocales();
    if (options.id) {
      this.setData({ id: options.id });
      this.loadData(options.id);
    }
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

  loadData: function (id) {
    const token = wx.getStorageSync('access_token');
    const header = {};
    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }

    const i18n = require('../../../utils/i18n.js');
    const lang = i18n.getLocale();
    header['Accept-Language'] = lang === 'zh' ? 'zh-hans' : 'en';

    wx.request({
      url: `${app.globalData.baseUrl}/crew/${id}/`,
      method: 'GET',
      header: header,
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ crew: res.data });
        } else if (res.statusCode === 401 && token) {
           wx.removeStorageSync('access_token');
           this.loadData(id);
        } else {
          wx.showToast({ title: '加载失败', icon: 'none' });
        }
      }
    });
  },

  toggleFollow: function () {
    if (!wx.getStorageSync('access_token')) {
      wx.navigateTo({ url: '/pages/login/login' });
      return;
    }
    
    // Implement follow logic
    wx.request({
      url: `${app.globalData.baseUrl}/following/toggle/`,
      method: 'POST',
      data: { followed_id: this.data.crew.user },
      header: { 'Authorization': `Bearer ${wx.getStorageSync('access_token')}` },
      success: (res) => {
         if (res.statusCode === 200 || res.statusCode === 201) {
             const newStatus = !this.data.crew.is_following;
             this.setData({ 'crew.is_following': newStatus });
             const i18n = require('../../../utils/i18n.js');
             const msg = newStatus ? i18n.t('following') : i18n.t('follow');
             wx.showToast({ title: msg, icon: 'none' });
         }
      }
    });
  },

  toggleFavorite: function () {
    if (!wx.getStorageSync('access_token')) {
      this.goToLogin();
      return;
    }

    const action = this.data.crew.is_favorited ? 'remove' : 'add';
    // Logic for favorite might be different depending on API structure
    // Assuming generic favorite API
    wx.request({
      url: `${app.globalData.baseUrl}/favorites/toggle/`,
      method: 'POST',
      data: { 
          content_type: 'crewlisting', // Backend needs to map this
          object_id: this.data.id 
      },
      header: { 'Authorization': `Bearer ${wx.getStorageSync('access_token')}` },
      success: (res) => {
          if (res.statusCode === 200) {
             const newStatus = res.data.is_favorited; // Assuming backend returns new status
             this.setData({ 'crew.is_favorited': newStatus });
             const i18n = require('../../../utils/i18n.js');
             const msg = newStatus ? i18n.t('favorited') : i18n.t('favorite');
             wx.showToast({ title: msg, icon: 'none' });
          }
      }
    });
  },

  contactCrew: function () {
    if (!wx.getStorageSync('access_token')) {
        const i18n = require('../../../utils/i18n.js');
        wx.showModal({
            title: i18n.t('prompt') || '提示',
            content: i18n.t('login_required') || '登录后查看联系方式',
            confirmText: i18n.t('login') || '去登录',
            success: (res) => {
                if (res.confirm) wx.navigateTo({ url: '/pages/login/login' });
            }
        });
        return;
    }
    // If logged in but no contact info (shouldn't happen if UI logic is correct, but safe to handle)
    if (!this.data.crew.phone && !this.data.crew.email) {
         wx.showToast({ title: '暂无联系方式', icon: 'none' });
    }
  },

  makePhoneCall: function (e) {
    const phone = e.currentTarget.dataset.phone;
    if (phone) {
      wx.makePhoneCall({ phoneNumber: phone });
    }
  },

  copyEmail: function (e) {
    const email = e.currentTarget.dataset.email;
    if (email) {
      wx.setClipboardData({
        data: email,
        success: () => {
          wx.showToast({ title: '邮箱已复制', icon: 'none' });
        }
      });
    }
  },

})
