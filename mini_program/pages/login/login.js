const app = getApp();
const i18n = require('../../utils/i18n.js');

Page({
  data: {
    t: {}, // Translation object
    isAdmin: false,
    phone: '',
    code: '',
    password: '',
    companyName: '',
    jobTitle: '',
    businessContent: '',
    counting: false,
    count: 60,
    nextUrl: '',
    isBinding: false,
    isPhoneLogin: false,
    wechatLoading: false,
    loginType: 'sms', // 'sms' or 'password'
    isAgreed: false
  },

  onLoad(options) {
    // Set language
    const lang = wx.getStorageSync('language') || 'zh';
    this.setData({ t: i18n.locales[lang] });

    if (options.next) {
        this.setData({ nextUrl: decodeURIComponent(options.next) });
    }

    if (options.role === 'admin') {
      this.setData({ isAdmin: true, loginType: 'password' });
    }
  },
  
  switchLoginType(e) {
      const type = e.currentTarget.dataset.type;
      this.setData({ loginType: type });
  },

  handleInput(e) {
    const field = e.currentTarget.dataset.field;
    this.setData({
      [field]: e.detail.value
    });
  },

  switchMode(e) {
      const mode = e.currentTarget.dataset.mode;
      this.setData({
          isPhoneLogin: mode === 'phone'
      });
  },

  goToRegister() {
    wx.navigateTo({
      url: '/pages/register/register'
    });
  },

  sendCode() {
    let { phone } = this.data;
    // Remove all spaces
    phone = phone ? String(phone).replace(/\s+/g, '') : '';
    
    if (!/^1\d{10}$/.test(phone)) {
      wx.showToast({
        title: '请输入有效的手机号',
        icon: 'none'
      });
      return;
    }
    
    // Update the phone input to the cleaned version
    this.setData({ phone });

    this.setData({ counting: true });
    
    // Call SMS API
    wx.request({
        url: `${app.globalData.baseUrl}/auth/sms/send/`,
        method: 'POST',
        data: { phone_number: phone },
        success: (res) => {
            if (res.statusCode === 200) {
                 wx.showToast({
                    title: '验证码已发送',
                    icon: 'success'
                 });
                 
                 // Dev Helper
                 if (res.data.code) {
                    wx.showModal({
                        title: '测试验证码',
                        content: '验证码是: ' + res.data.code,
                        showCancel: false,
                        confirmText: '自动填写',
                        success: (modalRes) => {
                            if (modalRes.confirm) {
                               this.setData({ code: res.data.code });
                            }
                        }
                    });
                 }

                 let timer = setInterval(() => {
                    if (this.data.count <= 0) {
                        clearInterval(timer);
                        this.setData({
                            counting: false,
                            count: 60
                        });
                    } else {
                        this.setData({
                            count: this.data.count - 1
                        });
                    }
                 }, 1000);
            } else {
                wx.showToast({
                    title: '发送失败',
                    icon: 'none'
                });
                this.setData({ counting: false });
            }
        },
        fail: () => {
             wx.showToast({
                title: '网络错误',
                icon: 'none'
             });
             this.setData({ counting: false });
        }
    });
  },

  handleAgreementChange(e) {
      this.setData({
          isAgreed: e.detail.value.length > 0
      });
  },

  openUserAgreement() {
      wx.navigateTo({
          url: '/pages/legal/agreement/agreement'
      });
  },

  openPrivacyPolicy() {
      wx.navigateTo({
          url: '/pages/legal/privacy/privacy'
      });
  },

  checkAgreement() {
      if (!this.data.isAgreed) {
          wx.showToast({
              title: this.data.t.agree_hint || '请阅读并同意协议',
              icon: 'none'
          });
          return false;
      }
      return true;
  },

  handlePhoneLogin() {
      if (!this.checkAgreement()) return;
      
      const { loginType } = this.data;
      if (loginType === 'sms') {
          this.handleSMSLogin();
      } else {
          this.handlePasswordLogin();
      }
  },

  handlePasswordLogin() {
      let { phone, password } = this.data;
      phone = phone ? String(phone).replace(/\s+/g, '') : '';
      
      if (!phone || !password) {
          wx.showToast({ title: '请输入账号和密码', icon: 'none' });
          return;
      }
      
      wx.request({
          url: `${app.globalData.baseUrl}/auth/token/`, // Use SimpleJWT default token view
          method: 'POST',
          data: {
              username: phone, // Assuming phone or username
              password: password
          },
          success: (res) => {
              if (res.statusCode === 200) {
                  const { access, refresh, user_id, username, is_staff, membership_level } = res.data;
                  app.globalData.token = access;
                  const userInfo = {
                      id: user_id,
                      username,
                      is_staff,
                      membership_level,
                      phone_number: res.data.phone_number
                  };
                  app.globalData.userInfo = userInfo;
                  
                  wx.setStorageSync('access_token', access);
                  wx.setStorageSync('refresh_token', refresh);
                  wx.setStorageSync('user_info', userInfo);
                  wx.setStorageSync('userInfo', userInfo);
                  
                  wx.showToast({ title: '登录成功', icon: 'success' });
                  
                  setTimeout(() => {
                      if (this.data.nextUrl) {
                          wx.reLaunch({ url: this.data.nextUrl });
                      } else {
                          wx.switchTab({ url: '/pages/index/index' });
                      }
                  }, 1000);
              } else {
                  wx.showToast({ title: '登录失败: ' + (res.data.detail || '账号或密码错误'), icon: 'none' });
              }
          },
          fail: () => {
              wx.showToast({ title: '网络请求失败', icon: 'none' });
          }
      });
  },

  handleSMSLogin() {
    let { phone, code } = this.data;
    // Clean phone
    phone = phone ? String(phone).replace(/\s+/g, '') : '';

    if (!phone || !code) {
        wx.showToast({
            title: '请填写手机号和验证码',
            icon: 'none'
        });
        return;
    }

      wx.showLoading({ title: '登录中...', mask: true });

      wx.request({
          url: `${app.globalData.baseUrl}/auth/sms/login/`,
          method: 'POST',
          data: { phone_number: phone, code: code },
          success: (res) => {
              wx.hideLoading();
              if (res.statusCode === 200) {
                  wx.showToast({ title: '登录成功', icon: 'success' });
                  
                  // Save tokens
                  wx.setStorageSync('access_token', res.data.access);
                  wx.setStorageSync('refresh_token', res.data.refresh);
                  
                  // Save user info
                  const userInfo = {
                      id: res.data.user_id,
                      username: res.data.username,
                      is_staff: res.data.is_staff,
                      phone_number: phone // SMS login implies phone is known
                  };
                  wx.setStorageSync('user_info', userInfo);
                  
                  // Redirect
                  setTimeout(() => {
                      if (this.data.nextUrl) {
                          wx.reLaunch({ url: this.data.nextUrl });
                      } else {
                          wx.switchTab({ url: '/pages/mine/mine' });
                      }
                  }, 1500);
              } else {
                  wx.showToast({ title: res.data.error || '登录失败', icon: 'none' });
              }
          },
          fail: () => {
              wx.hideLoading();
              wx.showToast({ title: '网络错误', icon: 'none' });
          }
      });
  },

  handleWeChatLogin() {
    if (!this.checkAgreement()) return;
    if (this.data.wechatLoading) return;
    this.setData({ wechatLoading: true });
    
    wx.showLoading({ title: '微信登录中...', mask: true });
    wx.login({
      success: (res) => {
        console.log('wx.login res =', res);
        if (res.code) {
          wx.request({
            url: `${app.globalData.baseUrl}/auth/wechat/`,
            method: 'POST',
            header: { 'content-type': 'application/json' },
            timeout: 15000,
            data: {
              code: res.code
            },
            success: (apiRes) => {
              console.log('wechat login apiRes =', apiRes);
              if (apiRes.statusCode === 200) {
                 wx.setStorageSync('access_token', apiRes.data.access);
                 wx.setStorageSync('refresh_token', apiRes.data.refresh);
                 this.setData({ wechatLoading: false });
                 this.checkPhoneAndRedirect(apiRes.data.access, apiRes.data);

              } else {
                 wx.hideLoading();
                 const serverMsg = (apiRes.data && (apiRes.data.error || apiRes.data.detail)) || (apiRes.data ? JSON.stringify(apiRes.data) : '') || '未知错误';
                 wx.showToast({ title: '登录失败: ' + serverMsg, icon: 'none', duration: 3000 });
                 this.setData({ wechatLoading: false });
              }
            },
            fail: (err) => {
                wx.hideLoading();
                console.error('WeChat login request failed', err);
                const errMsg = err.errMsg || JSON.stringify(err);
                wx.showToast({ title: '请求失败: ' + errMsg, icon: 'none', duration: 3000 });
                this.setData({ wechatLoading: false });
            }
          });
        } else {
          wx.hideLoading();
          wx.showToast({ title: '微信登录失败', icon: 'none' });
          this.setData({ wechatLoading: false });
        }
      },
      fail: (err) => {
         wx.hideLoading();
         console.error('wx.login failed', err);
         wx.showToast({ title: '无法获取登录凭证', icon: 'none' });
         this.setData({ wechatLoading: false });
      }
    });
  },

  clearCache() {
      wx.clearStorageSync();
      wx.showToast({
          title: '缓存已清除',
          icon: 'success'
      });
  },

  checkPhoneAndRedirect(token, userData) {
      this.setData({ wechatLoading: false });
      if (!userData.phone_number) {
          // No phone number, switch to binding mode
          wx.hideLoading(); // Hide global loading
          wx.showToast({
              title: '请绑定手机号',
              icon: 'none',
              duration: 2000
          });
          this.setData({ 
              isBinding: true, 
              loading: false,
              wechatLoading: false
          });
          return;
      }
      
      // Has phone number, proceed as normal
      wx.setStorageSync('user_info', userData);
      
      // Hide loading is optional if we are redirecting immediately, 
      // but showing success toast is good. 
      // wx.showToast implicitly hides loading on some platforms, but explicit is better.
      wx.hideLoading();

      wx.showToast({
          title: '登录成功',
          icon: 'success'
      });
      
      setTimeout(() => {
          if (this.data.nextUrl) {
              wx.reLaunch({ url: this.data.nextUrl });
          } else {
              wx.switchTab({ url: '/pages/mine/mine' });
          }
      }, 1500);
  },

  handleBindPhone() {
      if (!this.checkAgreement()) return;

      const { phone, code, companyName, jobTitle, businessContent } = this.data;
      if (!phone || !code) {
          wx.showToast({ title: '请输入手机号和验证码', icon: 'none' });
          return;
      }
      
      wx.showLoading({ title: '绑定中...', mask: true });
      const token = wx.getStorageSync('access_token');
      
      wx.request({
          url: `${app.globalData.baseUrl}/auth/bind-phone/`,
          method: 'POST',
          header: { 'Authorization': `Bearer ${token}` },
          data: { 
              phone_number: phone, 
              code: code,
              company_name: companyName,
              job_title: jobTitle,
              business_content: businessContent
          },
          success: (res) => {
              if (res.statusCode === 200) {
                  // Update tokens if merged
                  if (res.data.status === 'merged') {
                      wx.setStorageSync('access_token', res.data.access);
                      wx.setStorageSync('refresh_token', res.data.refresh);
                  }
                  
                  wx.hideLoading();
                  wx.showToast({ title: '绑定成功', icon: 'success' });
                  
                  // Update user info
                  const userInfo = wx.getStorageSync('user_info') || {};
                  userInfo.phone_number = res.data.phone_number || res.data.username; 
                  userInfo.username = res.data.username;
                  if (res.data.user_id) userInfo.id = res.data.user_id;
                  
                  wx.setStorageSync('user_info', userInfo);
                  
                  // Redirect
                  setTimeout(() => {
                      wx.switchTab({ url: '/pages/mine/mine' });
                  }, 1500);
                  
              } else {
                  wx.hideLoading();
                  wx.showToast({ title: res.data.error || '绑定失败', icon: 'none' });
              }
          },
          fail: () => {
              wx.hideLoading();
              wx.showToast({ title: '网络错误', icon: 'none' });
          }
      });
  },
  
  cancelBind() {
      this.setData({ isBinding: false });
      wx.removeStorageSync('access_token');
      wx.removeStorageSync('refresh_token');
      wx.removeStorageSync('user_info');
  }
});
