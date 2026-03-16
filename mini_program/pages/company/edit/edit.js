const app = getApp();

Page({
  data: {
    userInfo: {},
    loading: true,
    saving: false
  },

  onLoad() {
    this.fetchProfile();
  },

  fetchProfile() {
    const token = wx.getStorageSync('access_token');
    if (!token) {
        this.redirectToLogin();
        return;
    }

    wx.request({
      url: `${app.globalData.baseUrl}/user/info/`,
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        if (res.statusCode === 200) {
          const info = res.data;
          // Merge company_profile if exists
          const companyProfile = info.company_profile || {};
          const formData = {
              ...info,
              ...companyProfile
          };
          this.setData({ userInfo: formData, loading: false });
        } else if (res.statusCode === 401) {
            this.handle401();
        }
      },
      fail: () => {
          wx.showToast({ title: '加载失败', icon: 'none' });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },

  chooseImage() {
      wx.chooseImage({
          count: 1,
          success: (res) => {
              const filePath = res.tempFilePaths[0];
              this.uploadImage(filePath);
          }
      });
  },

  uploadImage(filePath) {
      const token = wx.getStorageSync('access_token');
      wx.showLoading({ title: '上传中...' });
      
      // Upload to dedicated endpoint
      wx.uploadFile({
          url: `${app.globalData.baseUrl}/user/upload/`,
          filePath: filePath,
          name: 'file',
          formData: {
              'field': 'business_license'
          },
          header: { 'Authorization': `Bearer ${token}` },
          success: (res) => {
              if (res.statusCode === 200) {
                  const data = JSON.parse(res.data);
                  this.setData({
                      'userInfo.business_license_img': data.url
                  });
                  wx.showToast({ title: '上传成功' });
              } else {
                  wx.showToast({ title: '上传失败', icon: 'none' });
              }
          },
          fail: () => {
              wx.showToast({ title: '网络错误', icon: 'none' });
          },
          complete: () => {
              wx.hideLoading();
          }
      });
  },

  onSubmit(e) {
      const data = e.detail.value;
      this.setData({ saving: true });
      const token = wx.getStorageSync('access_token');
      
      // Ensure role is set to COMPANY
      data.role = 'COMPANY';

      wx.request({
          url: `${app.globalData.baseUrl}/user/profile/update/`,
          method: 'PUT',
          header: { 
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
          },
          data: data,
          success: (res) => {
              if (res.statusCode === 200) {
                  wx.showToast({ title: '保存成功' });
                  setTimeout(() => wx.navigateBack(), 1500);
              } else if (res.statusCode === 401) {
                  this.handle401();
              } else {
                  wx.showToast({ title: '保存失败', icon: 'none' });
              }
          },
          complete: () => {
              this.setData({ saving: false });
          }
      });
  },

  handle401() {
      wx.removeStorageSync('access_token');
      wx.showModal({
          title: '提示',
          content: '登录已过期，请重新登录',
          showCancel: false,
          success: (res) => {
              if (res.confirm) {
                  wx.navigateTo({ url: '/pages/login/login' });
              }
          }
      });
  },

  redirectToLogin() {
      wx.navigateTo({ url: '/pages/login/login' });
  }
});
