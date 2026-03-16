const app = getApp()

Page({
  data: {
    userInfo: {},
    saving: false
  },

  onLoad() {
    this.fetchProfile();
  },

  fetchProfile() {
    const token = wx.getStorageSync('access_token');
    if (!token) {
      wx.showModal({
        title: '提示',
        content: '请先登录',
        showCancel: false,
        success: (res) => {
          if (res.confirm) {
            wx.reLaunch({
              url: '/pages/login/login'
            });
          }
        }
      });
      return;
    }

    wx.request({
      url: `${app.globalData.baseUrl}/user/info/`,
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            userInfo: res.data
          });
        } else if (res.statusCode === 401) {
          wx.showToast({
            title: '登录已过期，请重新登录',
            icon: 'none'
          });
          wx.removeStorageSync('access_token');
          wx.removeStorageSync('user_info');
          setTimeout(() => {
            wx.reLaunch({
              url: '/pages/login/login'
            });
          }, 1500);
        } else {
          wx.showToast({
            title: '获取资料失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    });
  },

  chooseAvatar() {
      wx.chooseMedia({
          count: 1,
          mediaType: ['image'],
          sourceType: ['album', 'camera'],
          success: (res) => {
              const tempFilePath = res.tempFiles[0].tempFilePath;
              this.uploadAvatar(tempFilePath);
          }
      })
  },
  
  uploadAvatar(filePath) {
      const token = wx.getStorageSync('access_token');
      wx.showLoading({ title: 'Uploading...' });
      
      wx.uploadFile({
          url: `${app.globalData.baseUrl}/user/profile/update/`,
          filePath: filePath,
          name: 'avatar',
        header: {
            'Authorization': `Bearer ${token}`
        },
        success: (res) => {
              wx.hideLoading();
              if (res.statusCode === 200) {
                  const data = JSON.parse(res.data);
                  // Update local user info
                  const userInfo = this.data.userInfo;
                  userInfo.avatar = data.avatar;
                  userInfo.avatarUrl = data.avatar; // Keep consistent for mine page
                  this.setData({ userInfo });
                  wx.setStorageSync('user_info', userInfo); // Update global storage
                  wx.showToast({ title: 'Avatar Updated' });
              } else {
                  wx.showToast({ title: 'Upload failed', icon: 'none' });
              }
          },
          fail: (err) => {
              wx.hideLoading();
              wx.showToast({ title: 'Network error', icon: 'none' });
          }
      })
  },

  saveProfile(e) {
      const data = e.detail.value;
      this.setData({ saving: true });
      const token = wx.getStorageSync('access_token');

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
                  // Update local storage
                  const oldInfo = wx.getStorageSync('user_info') || {};
                  const newInfo = { ...oldInfo, ...data };
                  wx.setStorageSync('user_info', newInfo);
                  
                  setTimeout(() => wx.navigateBack(), 1500);
              } else {
                  wx.showToast({ title: '保存失败', icon: 'none' });
              }
          },
          complete: () => {
              this.setData({ saving: false });
          }
      });
  },

  logout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('access_token');
          wx.removeStorageSync('refresh_token');
          wx.removeStorageSync('user_info');
          
          wx.reLaunch({
            url: '/pages/login/login'
          });
        }
      }
    });
  }
})