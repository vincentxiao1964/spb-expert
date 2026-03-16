const app = getApp()
const i18n = require('../../utils/i18n.js');

Page({
  data: {
    userInfo: null,
    hasUserInfo: false,
    canIUseGetUserProfile: false,
    stats: {
        match_count: 0,
        unread_message_count: 0,
        favorite_me_count: 0
    },
    t: {}
  },
  onLoad() {
    this.updateLocales();

    if (wx.getUserProfile) {
      this.setData({
        canIUseGetUserProfile: true
      })
    }
    // Check if token exists
    this.checkLoginStatus();
  },
  onShow() {
      this.updateLocales();
      i18n.updateTabBar(this);
      
      this.checkLoginStatus();
      if (this.data.hasUserInfo) {
          this.fetchStats();
      }
  },
  
  updateLocales() {
      const lang = i18n.getLocale();
      this.setData({
          t: i18n.locales[lang]
      });
      // Dynamically set title
      wx.setNavigationBarTitle({ title: i18n.locales[lang]['tabbar_mine'] });
  },

  switchLanguage() {
      const current = i18n.getLocale();
      const next = current === 'zh' ? 'en' : 'zh';
      
      // 1. Set storage synchronously
      i18n.setLocale(next);
      
      // 2. Update current page immediately
      this.setData({
          t: i18n.locales[next]
      });
      i18n.updateTabBar(this);
      
      // 3. Show toast
      wx.showToast({
          title: i18n.t('switched_lang_success'),
          icon: 'none'
      });
      
      // 4. Reload page data to reflect language change (e.g. status text)
      if (this.data.hasUserInfo) {
          this.fetchStats();
      }
      this.checkLoginStatus(); // Re-evaluate text like "Logged In" vs "已登录"
  },
  fetchStats() {
      const token = wx.getStorageSync('access_token');
      if (!token) return;
      
      wx.request({
          url: `${app.globalData.baseUrl}/mine/stats/`,
          header: { 'Authorization': `Bearer ${token}` },
          success: (res) => {
              if (res.statusCode === 200) {
                  this.setData({ stats: res.data });
              }
          }
      });
  },
  checkLoginStatus() {
      const token = wx.getStorageSync('access_token');
      // We might store user info in storage or fetch it
      const userInfo = wx.getStorageSync('user_info');
      
      if (token && userInfo) {
          this.setData({
              hasUserInfo: true,
              userInfo: userInfo
          });
          
          // Verify admin status if we have user info, or fetch it
          if (userInfo.is_staff || userInfo.is_superuser) {
              this.setData({ isAdmin: true });
          }
          // Always fetch latest to verify token validity
          this.fetchUserInfo();
      } else {
          // Explicitly clear state if token or userInfo is missing
          this.setData({
              hasUserInfo: false,
              userInfo: null,
              isAdmin: false
          });
          // Also ensure storage is clean if partial state exists
          if (!token) wx.removeStorageSync('user_info');
          if (!userInfo) wx.removeStorageSync('access_token');
      }
  },

  fetchUserInfo() {
    const token = wx.getStorageSync('access_token');
    if (!token) return;

    wx.request({
        url: `${app.globalData.baseUrl}/user/info/`,
        header: { 'Authorization': `Bearer ${token}` },
        success: (res) => {
            if (res.statusCode === 200) {
                const user = res.data;
                // Add avatarUrl/nickName mapping if backend uses different fields
                user.avatarUrl = user.avatar || '/assets/default-avatar.png';
                user.nickName = user.username;
                
                wx.setStorageSync('user_info', user);
                this.setData({
                    userInfo: user,
                    hasUserInfo: true,
                    isAdmin: user.is_staff || user.is_superuser
                });
            } else if (res.statusCode === 401) {
                // Token expired or invalid
                this.handleLogout();
            }
        },
        fail: () => {
            // Network error - do not logout immediately, user might be offline
            // But if we want to be strict about 'sync', we might need to handle this.
            // For now, assume network failure doesn't mean logout.
        }
    });
  },

  handleLogout() {
      wx.removeStorageSync('access_token');
      wx.removeStorageSync('refresh_token');
      wx.removeStorageSync('user_info');
      this.setData({
          hasUserInfo: false,
          userInfo: null,
          isAdmin: false,
          stats: {
            match_count: 0,
            unread_message_count: 0,
            favorite_me_count: 0
        }
      });
  },
  
  goLogin() {
    if (this.data.hasUserInfo) {
      wx.navigateTo({
        url: '/pages/mine/profile/profile'
      });
    } else {
      wx.navigateTo({
        url: '/pages/login/login'
      });
    }
  },

  goToAdminDashboard() {
      wx.navigateTo({
          url: '/pages/admin/dashboard/dashboard'
      });
  },

  preventTouchMove() {},
  
  // Menu handlers
  goToOrders() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({ url: '/pages/orders/list/list' });
  },
  goToInquiries() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({ url: '/pages/inquiries/list/list' });
  },
  goToProfile() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({ 
          url: '/pages/mine/profile/profile'
      });
  },
  goToContact() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({ 
          url: '/pages/mine/profile/profile'
      });
  },
  bindWeChat() {
      if (!this.data.hasUserInfo) return this.goLogin();
      
      const that = this;
      
      // Check if already bound
      if (this.data.userInfo.is_wechat_bound) {
          wx.showModal({
              title: i18n.t('action_unbind'),
              content: i18n.t('confirm_unbind'),
              confirmColor: '#ff4d4f',
              success(res) {
                  if (res.confirm) {
                      that.doUnbindWeChat();
                  }
              }
          });
          return;
      }

      wx.showLoading({ title: i18n.t('binding') });
      
      wx.login({
          success: (res) => {
              if (res.code) {
                  const token = wx.getStorageSync('access_token');
                  wx.request({
                      url: `${app.globalData.baseUrl}/auth/bind-wechat/`,
                      method: 'POST',
                      header: { 
                          'Authorization': `Bearer ${token}`,
                          'Content-Type': 'application/json' 
                      },
                      data: { code: res.code },
                      success: (response) => {
                          wx.hideLoading();
                          if (response.statusCode === 200) {
                              wx.showToast({ title: i18n.t('bind_success'), icon: 'success' });
                              // Update local user info
                              that.fetchUserInfo();
                          } else if (response.statusCode === 401) {
                              wx.showModal({
                                  title: i18n.t('login_expired'),
                                  content: i18n.t('please_relogin'),
                                  showCancel: false,
                                  success: () => {
                                      that.handleLogout();
                                      that.goLogin();
                                  }
                              });
                          } else {
                              console.error('Bind WeChat Error:', response);
                              const errorMsg = response.data.error || response.data.detail || i18n.t('unknown_error');
                              wx.showModal({
                                  title: i18n.t('bind_fail'),
                                  content: errorMsg,
                                  showCancel: false
                              });
                          }
                      },
                      fail: (err) => {
                          wx.hideLoading();
                          wx.showToast({ title: i18n.t('error_network'), icon: 'none' });
                      }
                  });
              } else {
                  wx.hideLoading();
                  wx.showToast({ title: i18n.t('get_code_fail'), icon: 'none' });
              }
          },
          fail: () => {
              wx.hideLoading();
              wx.showToast({ title: i18n.t('wechat_login_fail'), icon: 'none' });
          }
      });
  },
  doUnbindWeChat() {
      const that = this;
      const token = wx.getStorageSync('access_token');
      wx.showLoading({ title: 'Processing...' });
      
      wx.request({
          url: `${app.globalData.baseUrl}/auth/unbind-wechat/`,
          method: 'POST',
          header: { 
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json' 
          },
          success: (response) => {
              wx.hideLoading();
              if (response.statusCode === 200) {
                  wx.showToast({ title: i18n.t('unbind_success'), icon: 'success' });
                  setTimeout(() => { that.fetchUserInfo(); }, 500);
              } else {
                  const errorMsg = response.data.error || i18n.t('unbind_fail');
                  wx.showModal({
                      title: i18n.t('unbind_fail'),
                      content: errorMsg,
                      showCancel: false
                  });
              }
          },
          fail: () => {
              wx.hideLoading();
              wx.showToast({ title: i18n.t('error_network'), icon: 'none' });
          }
      });
  },

  goToMyShips() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({
          url: '/pages/admin/ships/list/list?mode=my'
      });
  },
  goToMyNews() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({
          url: '/pages/admin/news/list/list?mode=my'
      });
  },
  goToMyAds() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({
          url: '/pages/admin/ads/list/list?mode=my'
      });
  },
  goToMyForum() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({
          url: '/pages/mine/forum/forum'
      });
  },
  goToMyCrewProfile() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({
          url: '/pages/crew/edit/edit'
      });
  },

  // Admin handlers
  goToShipApproval() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({
          url: '/pages/admin/ships/list/list?mode=admin'
      });
  },
  goToNewsApproval() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({
          url: '/pages/admin/news/list/list?mode=admin'
      });
  },
  goToTransactionManager() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({
          url: '/pages/admin/transactions/manager/manager'
      });
  },
  goToAdApproval() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({
          url: '/pages/admin/ads/list/list?mode=admin'
      });
  },
  goToForumManagement() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({
          url: '/pages/admin/messages/list/list'
      });
  },
  goToUserStats() {
    wx.navigateTo({
      url: '/pages/admin/user_stats/user_stats'
    })
  },
  goToCrewManagement() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({
          url: '/pages/crew/list/list'
      });
  },

  goToTransactions() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({
          url: '/pages/transactions/list/list'
      });
  },

  goToFavorites() {
      if (!this.data.hasUserInfo) return this.goLogin();
      // Use a dedicated page for favorites since we can't navigate to TabBar page with params
      wx.navigateTo({
          url: '/pages/mine/favorites/favorites'
      });
  },
  goToDrafts() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({
        url: '/pages/admin/ships/list/list?status=PENDING'
    });
  },

  goToMatches() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.navigateTo({
          url: '/pages/mine/matches/matches'
      });
  },
  goToInbox() {
    if (!this.data.hasUserInfo) return this.goLogin();
    wx.navigateTo({
        url: '/pages/mine/contacts/contacts'
    });
  },
  goToFollowing() {
    if (!this.data.hasUserInfo) return this.goLogin();
    wx.navigateTo({
        url: '/pages/mine/following/following'
    });
  },
  goToFollowers() {
    if (!this.data.hasUserInfo) return this.goLogin();
    wx.navigateTo({
        url: '/pages/mine/followers/followers'
    });
  },
  
  showAdminContact() {
    wx.showActionSheet({
      itemList: [
        i18n.t('action_call') + ': +86 180 1911 9595',
        i18n.t('action_copy_email') + ': admin@barge-expert.com'
      ],
      success(res) {
        if (res.tapIndex === 0) {
          wx.makePhoneCall({
            phoneNumber: '+8618019119595'
          });
        } else if (res.tapIndex === 1) {
          wx.setClipboardData({
            data: 'admin@barge-expert.com',
            success() {
              wx.showToast({ title: i18n.t('email_copied') });
            }
          });
        }
      }
    });
  },

  logout() {
      wx.removeStorageSync('access_token');
      wx.removeStorageSync('user_info');
      this.setData({
          hasUserInfo: false,
          userInfo: null
      });
      wx.showToast({ title: i18n.t('logout_success'), icon: 'none' });
  },

  deleteAccount() {
      if (!this.data.hasUserInfo) return this.goLogin();
      wx.showModal({
          title: i18n.t('delete_account'),
          content: i18n.t('delete_account_confirm'),
          confirmColor: '#e64340',
          success: (res) => {
              if (res.confirm) {
                  const token = wx.getStorageSync('access_token');
                  wx.showLoading({ title: i18n.t('loading') });
                  wx.request({
                      url: `${app.globalData.baseUrl}/user/delete/`,
                      method: 'DELETE',
                      header: { 'Authorization': `Bearer ${token}` },
                      success: (response) => {
                          wx.hideLoading();
                          if (response.statusCode === 200) {
                              wx.showToast({ title: i18n.t('delete_account_success'), icon: 'none' });
                              wx.removeStorageSync('access_token');
                              wx.removeStorageSync('refresh_token');
                              wx.removeStorageSync('user_info');
                              wx.reLaunch({ url: '/pages/index/index' });
                          } else if (response.statusCode === 401) {
                              wx.showToast({ title: i18n.t('login_expired'), icon: 'none' });
                              wx.removeStorageSync('access_token');
                              wx.redirectTo({ url: '/pages/login/login' });
                          } else {
                              const msg = (response.data && (response.data.error || response.data.detail)) || '删除失败';
                              wx.showToast({ title: msg, icon: 'none' });
                          }
                      },
                      fail: () => {
                          wx.hideLoading();
                          wx.showToast({ title: i18n.t('error_network'), icon: 'none' });
                      }
                  });
              }
          }
      });
  }
})
