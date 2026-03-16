const app = getApp();
const i18n = require('../../../utils/i18n.js');

Page({
  data: {
    transactions: [],
    loading: true,
    t: {}
  },
  onLoad: function () {
    this.updateLocales();
    this.fetchTransactions();
  },
  onShow: function() {
    this.updateLocales();
  },
  updateLocales: function() {
    const lang = i18n.getLocale();
    this.setData({ t: i18n.locales[lang] });
  },
  fetchTransactions: function() {
    const token = wx.getStorageSync('access_token');
    wx.request({
      url: `${app.globalData.baseUrl}/transactions/`,
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        if (res.statusCode === 200) {
          const list = res.data.map(item => {
              item.status_display = this.data.t[`txn_status_${item.status}`] || item.status;
              item.created_at = item.created_at.split('T')[0];
              return item;
          });
          this.setData({ transactions: list, loading: false });
        } else if (res.statusCode === 401) {
            wx.removeStorageSync('access_token');
            wx.removeStorageSync('user_info');
            wx.showToast({
                title: this.data.t.login_required || '请先登录',
                icon: 'none'
            });
            setTimeout(() => {
                this.goToLogin();
            }, 1500);
        }
      },
      fail: () => {
          this.setData({ loading: false });
      }
    });
  }
});