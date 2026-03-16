const app = getApp();
const i18n = require('../../utils/i18n.js');

Component({
  properties: {
    hasTabbar: {
      type: Boolean,
      value: false
    },
    hasCustomTabbar: {
      type: Boolean,
      value: false
    }
  },

  data: {
    crewText: '船员服务',
    langText: 'English',
    homeText: '回首页'
  },

  lifetimes: {
    attached: function() {
      this.updateLocales();
    }
  },

  pageLifetimes: {
    show: function() {
      this.updateLocales();
    }
  },

  methods: {
    updateLocales: function() {
      const lang = i18n.getLocale();
      this.setData({
        crewText: lang === 'zh' ? '船员服务' : 'Crew Services',
        langText: lang === 'zh' ? 'Switch to English' : '切换到中文',
        homeText: lang === 'zh' ? '回首页' : 'Home'
      });
    },

    preventTouchMove: function() {
      // Prevent touch move propagation
    },


    goCrew: function() {
      wx.navigateTo({
        url: '/pages/crew/list/list'
      });
    },

    goHome: function() {
      wx.switchTab({
        url: '/pages/index/index'
      });
    },

    switchLang: function() {
      const current = i18n.getLocale();
      const next = current === 'zh' ? 'en' : 'zh';
      i18n.setLocale(next);
      
      // Update this component
      this.updateLocales();
      
      // Update current page (parent)
      const pages = getCurrentPages();
      const currentPage = pages[pages.length - 1];
      if (currentPage && currentPage.updateLocales) {
        currentPage.updateLocales();
        i18n.updateTabBar(currentPage);
      }
      
      // Force refresh of the current page if it has an onShow that updates data
      if (currentPage && currentPage.onShow) {
          currentPage.onShow();
      }
      
      wx.showToast({
        title: next === 'zh' ? '已切换中文' : 'Switched to English',
        icon: 'none'
      });
    }
  }
});