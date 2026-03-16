const i18n = require('../../../utils/i18n.js');

Page({
  data: {
    t: {}
  },
  onShow() {
    const lang = i18n.getLocale();
    this.setData({ t: i18n.locales[lang] });
    wx.setNavigationBarTitle({ title: this.data.t.privacy_policy || '隐私政策' });
  }
});
