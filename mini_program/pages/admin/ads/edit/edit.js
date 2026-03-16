const app = getApp();

Page({
  data: {
    id: null,
    title: '',
    link: '',
    description: '',
    image: '',
    is_active: false,
    submitting: false,
    hasNewImage: false,
    originalImage: ''
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ id: options.id });
      wx.setNavigationBarTitle({ title: '编辑广告' });
      this.loadData(options.id);
    } else {
        wx.setNavigationBarTitle({ title: '发布广告' });
    }
  },

  loadData(id) {
    const token = wx.getStorageSync('access_token');
    wx.request({
      url: `${app.globalData.baseUrl}/ads/${id}/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const data = res.data;
          
          // Fix image URL if it's partial
          if (data.image) {
              const siteRoot = app.globalData.baseUrl.split('/api')[0];
              if (!data.image.startsWith('http')) {
                  data.image = siteRoot + data.image;
              } else if (data.image.includes('127.0.0.1')) {
                   // Replace 127.0.0.1 with current API host
                   const currentHost = siteRoot.split('://')[1].split(':')[0];
                   data.image = data.image.replace('127.0.0.1', currentHost);
              }
          }

          this.setData({
            title: data.title,
            link: data.link || '',
            description: data.description || '',
            image: data.image,
            is_active: data.is_active,
            hasNewImage: false,
            originalImage: data.image
          });
        }
      }
    });
  },

  handleInput(e) {
    const field = e.currentTarget.dataset.field;
    this.setData({
      [field]: e.detail.value
    });
  },

  handleSwitch(e) {
    this.setData({
      is_active: e.detail.value
    });
  },

  chooseImage() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePaths = res.tempFilePaths;
        this.setData({
          image: tempFilePaths[0],
          hasNewImage: true
        });
      }
    });
  },

  removeImage() {
    this.setData({ 
      image: '',
      hasNewImage: false
    });
  },

  handleSubmit() {
    if (!this.data.title) {
      wx.showToast({ title: '请输入标题', icon: 'none' });
      return;
    }

    this.setData({ submitting: true });
    
    // Determine if we need to upload image
    const isImageChanged = this.data.image !== this.data.originalImage;
    const isLocalPath = this.data.image && (
        this.data.image.startsWith('http://tmp/') || 
        this.data.image.startsWith('wxfile://') || 
        this.data.image.startsWith('blob:')
    );
    const shouldUpload = this.data.image && (this.data.hasNewImage || isImageChanged || isLocalPath);

    console.log('Submit Strategy:', {
        id: this.data.id,
        shouldUpload,
        isLocalPath
    });

    if (this.data.id) {
        // UPDATE MODE
        // 1. Update text fields first
        this.updateAdText().then(() => {
            if (shouldUpload) {
                // 2. If image changed, upload it separately
                this.uploadAdImage(this.data.id);
            } else {
                wx.showToast({ title: '修改成功' });
                setTimeout(() => wx.navigateBack(), 1500);
            }
        }).catch(err => {
            console.error('Update text failed:', err);
            this.setData({ submitting: false });
        });
    } else {
        // CREATE MODE
        // If has image, use wx.uploadFile to send everything
        if (shouldUpload) {
            this.createAdWithImage();
        } else {
            // Text only create
            this.createAdText();
        }
    }
  },

  updateAdText() {
    return new Promise((resolve, reject) => {
        wx.showLoading({ title: '保存信息...', mask: true });
        const token = wx.getStorageSync('access_token');
        wx.request({
            url: `${app.globalData.baseUrl}/ads/${this.data.id}/`,
            method: 'PATCH',
            data: {
                title: this.data.title,
                link: this.data.link,
                description: this.data.description,
                is_active: this.data.is_active
            },
            header: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            success: (res) => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    resolve(res.data);
                } else {
                    wx.showToast({ title: '保存失败: ' + res.statusCode, icon: 'none' });
                    reject(res);
                }
            },
            fail: reject
        });
    });
  },

  uploadAdImage(id) {
    wx.showLoading({ title: '上传图片...', mask: true });
    const token = wx.getStorageSync('access_token');
    
    // Use dedicated upload endpoint
    wx.uploadFile({
        url: `${app.globalData.baseUrl}/ads/${id}/upload_image/`,
        filePath: this.data.image,
        name: 'image',
        header: {
            'Authorization': `Bearer ${token}`
        },
        success: (res) => {
            wx.hideLoading();
            console.log('Upload result:', res);
            if (res.statusCode >= 200 && res.statusCode < 300) {
                    // Slight delay to ensure user sees the process and server has time to finalize
                    setTimeout(() => {
                        wx.hideLoading();
                        wx.showToast({ title: '上传成功' });
                        setTimeout(() => wx.navigateBack(), 1500);
                    }, 500);
                } else {
                    wx.hideLoading();
                    wx.showToast({ title: '图片上传失败', icon: 'none' });
                    this.setData({ submitting: false });
                }
        },
        fail: (err) => {
            console.error('Upload failed:', err);
            wx.hideLoading();
            wx.showToast({ title: '网络错误', icon: 'none' });
            this.setData({ submitting: false });
        }
    });
  },

  createAdWithImage() {
      wx.showLoading({ title: '创建并上传...', mask: true });
      const token = wx.getStorageSync('access_token');
      
      wx.uploadFile({
          url: `${app.globalData.baseUrl}/ads/`,
          filePath: this.data.image,
          name: 'image',
          formData: {
            'title': this.data.title,
            'link': this.data.link || '',
            'description': this.data.description || '',
            'is_active': this.data.is_active ? 'true' : 'false'
          },
          header: {
              'Authorization': `Bearer ${token}`
          },
          success: (res) => {
              wx.hideLoading();
              if (res.statusCode >= 200 && res.statusCode < 300) {
                  wx.showToast({ title: '创建成功' });
                  setTimeout(() => wx.navigateBack(), 1500);
              } else {
                  // uploadFile returns data as string
                  console.error('Create failed:', res.data);
                  wx.showToast({ title: '创建失败', icon: 'none' });
                  this.setData({ submitting: false });
              }
          },
          fail: (err) => {
              wx.hideLoading();
              wx.showToast({ title: '网络错误', icon: 'none' });
              this.setData({ submitting: false });
          }
      });
  },

  createAdText() {
      wx.showLoading({ title: '创建中...', mask: true });
      const token = wx.getStorageSync('access_token');
      wx.request({
        url: `${app.globalData.baseUrl}/ads/`,
        method: 'POST',
        data: {
            title: this.data.title,
            link: this.data.link,
            description: this.data.description,
            is_active: this.data.is_active,
            image: null
        },
        header: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        success: (res) => {
            wx.hideLoading();
            if (res.statusCode >= 200 && res.statusCode < 300) {
                wx.showToast({ title: '创建成功' });
                setTimeout(() => wx.navigateBack(), 1500);
            } else {
                wx.showToast({ title: '创建失败', icon: 'none' });
                this.setData({ submitting: false });
            }
        },
        fail: () => {
            wx.hideLoading();
            wx.showToast({ title: '网络错误', icon: 'none' });
            this.setData({ submitting: false });
        }
      });
  },

  sendData(base64Image) {
      const token = wx.getStorageSync('access_token');
      const data = {
          title: this.data.title,
          link: this.data.link,
          description: this.data.description,
          is_active: this.data.is_active
      };
      
      if (base64Image) {
          data.image = base64Image;
      } else if (!this.data.image) {
          // Explicitly cleared image
           data.image = null; 
      }
      // If image is existing URL (not null, not base64), we don't include it in data, so it remains unchanged.

      const method = this.data.id ? 'PATCH' : 'POST';
      const url = this.data.id 
        ? `${app.globalData.baseUrl}/ads/${this.data.id}/` 
        : `${app.globalData.baseUrl}/ads/`;

      wx.request({
          url: url,
          method: method,
          data: data,
          header: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
          },
          success: (res) => {
              wx.hideLoading();
              if (res.statusCode >= 200 && res.statusCode < 300) {
                  wx.showToast({ title: '提交成功' });
                  setTimeout(() => wx.navigateBack(), 1500);
              } else if (res.statusCode === 401) {
                  wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
                  wx.removeStorageSync('access_token');
                  setTimeout(() => {
                      wx.redirectTo({ url: '/pages/login/login' });
                  }, 1500);
              } else {
                  console.error('Submit failed:', res);
                  let errorMsg = '提交失败';
                  if (res.data) {
                      if (typeof res.data === 'string') {
                          // Try to detect HTML error page
                          if (res.data.includes('<!DOCTYPE html>')) {
                              errorMsg += ': 服务器错误';
                          } else {
                             errorMsg += ': ' + res.data.substring(0, 50);
                          }
                      } else if (typeof res.data === 'object') {
                          // Try to get the first error message
                          const values = Object.values(res.data);
                          if (values.length > 0) {
                              const firstError = Array.isArray(values[0]) ? values[0][0] : values[0];
                              errorMsg += ': ' + firstError;
                          }
                      }
                  }
                  wx.showToast({ title: errorMsg, icon: 'none', duration: 3000 });
              }
              this.setData({ submitting: false });
          },
          fail: (err) => {
              wx.hideLoading();
              console.error('Request failed:', err);
              wx.showToast({ title: '网络请求失败', icon: 'none' });
              this.setData({ submitting: false });
          }
      });
  }
});