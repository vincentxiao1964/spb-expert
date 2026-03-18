const app = getApp();

Page({
  data: {
    phoneNumber: '',
    code: '',
    email: '',
    emailCode: '',
    password: '',
    confirmPassword: '',
    username: '',
    companyName: '',
    jobTitle: '',
    businessContent: '',
    countdown: 0,
    loading: false,
    registerType: 'sms' // 'sms' or 'account' or 'email'
  },
  
  onLoad(options) {
    const mode = options && options.mode;
    const preEmail = options && options.email ? decodeURIComponent(options.email) : '';
    if (mode === 'email') {
      this.setData({ registerType: 'email', email: preEmail });
    }
  },

  switchRegisterType(e) {
      const type = e.currentTarget.dataset.type;
      this.setData({ registerType: type });
  },

  handleInput(e) {
    const field = e.currentTarget.dataset.field;
    this.setData({
      [field]: e.detail.value
    });
  },

  sendCode() {
    if (this.data.countdown > 0) return;
    
    let phone = this.data.phoneNumber;
    // Clean phone number
    phone = phone ? String(phone).replace(/\s+/g, '') : '';
    
    if (!/^1\d{10}$/.test(phone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' });
      return;
    }
    
    // Update data with clean phone
    this.setData({ phoneNumber: phone });

    wx.request({
      url: `${app.globalData.baseUrl}/auth/sms/send/`,
      method: 'POST',
      data: { phone_number: phone },
      success: (res) => {
        if (res.statusCode === 200) {
          wx.showToast({ title: '验证码已发送', icon: 'success' });
          this.startCountdown();

          // DEV: Show code in modal for easier testing
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
        } else {
          wx.showToast({ title: '发送失败: ' + (res.data.error || '未知错误'), icon: 'none' });
        }
      },
      fail: () => {
        wx.showToast({ title: '网络请求失败', icon: 'none' });
      }
    });
  },

  sendEmailCode() {
    if (this.data.countdown > 0) return;
    let email = this.data.email ? String(this.data.email).trim().toLowerCase() : '';
    if (!email || email.indexOf('@') <= 0 || email.lastIndexOf('.') <= email.indexOf('@') + 1) {
      wx.showToast({ title: '请输入有效邮箱', icon: 'none' });
      return;
    }
    this.setData({ email: email });
    wx.request({
      url: `${app.globalData.baseUrl}/auth/email/send/`,
      method: 'POST',
      data: { email },
      success: (res) => {
        if (res.statusCode === 200) {
          wx.showToast({ title: '验证码已发送', icon: 'success' });
          this.startCountdown();
          if (res.data.code) {
            wx.showModal({
              title: '测试验证码',
              content: '验证码是: ' + res.data.code,
              showCancel: false,
              confirmText: '自动填写',
              success: (modalRes) => {
                if (modalRes.confirm) {
                  this.setData({ emailCode: res.data.code });
                }
              }
            });
          }
        } else {
          wx.showToast({ title: res.data.error || '发送失败', icon: 'none' });
        }
      },
      fail: () => wx.showToast({ title: '网络错误', icon: 'none' })
    });
  },

  startCountdown() {
    this.setData({ countdown: 60 });
    const timer = setInterval(() => {
      if (this.data.countdown <= 1) {
        clearInterval(timer);
        this.setData({ countdown: 0 });
      } else {
        this.setData({ countdown: this.data.countdown - 1 });
      }
    }, 1000);
  },

  handleRegister() {
    let { registerType, phoneNumber, code, email, emailCode, password, confirmPassword, username, companyName, jobTitle, businessContent } = this.data;
    
    // Clean phone just in case
    phoneNumber = phoneNumber ? String(phoneNumber).replace(/\s+/g, '') : '';

    if (registerType === 'sms') {
        if (!phoneNumber || !code) {
          wx.showToast({ title: '请填写手机号和验证码', icon: 'none' });
          return;
        }
    } else if (registerType === 'email') {
        email = email ? String(email).trim().toLowerCase() : '';
        emailCode = emailCode ? String(emailCode).trim() : '';
        if (!email || !emailCode) {
          wx.showToast({ title: '请填写邮箱与验证码', icon: 'none' });
          return;
        }
    } else {
        // Account Mode
        if (!username || !password) {
            wx.showToast({ title: '请填写用户名和密码', icon: 'none' });
            return;
        }
    }
    
    if (password && password !== confirmPassword) {
        wx.showToast({ title: '两次输入的密码不一致', icon: 'none' });
        return;
    }

    this.setData({ loading: true });

    const doSuccess = (res) => {
      this.setData({ loading: false });
      if (res.statusCode === 201 || res.statusCode === 200) {
        wx.setStorageSync('access_token', res.data.access);
        wx.setStorageSync('refresh_token', res.data.refresh);
        wx.setStorageSync('user_id', res.data.user_id);
        wx.showToast({ title: '注册成功', icon: 'success' });
        setTimeout(() => { wx.switchTab({ url: '/pages/index/index' }); }, 1500);
      } else {
        wx.showToast({ title: res.data.error || '注册失败', icon: 'none' });
      }
    };

    if (registerType === 'email') {
      wx.request({
        url: `${app.globalData.baseUrl}/auth/email/register/`,
        method: 'POST',
        data: { email, code: emailCode },
        success: doSuccess,
        fail: () => { this.setData({ loading: false }); wx.showToast({ title: '网络错误', icon: 'none' }); }
      });
    } else {
      wx.request({
        url: `${app.globalData.baseUrl}/auth/register/`,
        method: 'POST',
        data: {
          phone_number: phoneNumber,
          code: code,
          password: password,
          username: username,
          company_name: companyName,
          job_title: jobTitle,
          business_content: businessContent
        },
        success: doSuccess,
        fail: () => { this.setData({ loading: false }); wx.showToast({ title: '网络错误', icon: 'none' }); }
      });
    }
  },

  goLogin() {
      wx.navigateBack();
  }
});
