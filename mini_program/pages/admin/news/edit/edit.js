const app = getApp();

Page({
  data: {
    id: null,
    title: '',
    title_en: '',
    content: '',
    content_en: '',
    imagePath: '',
    submitting: false,
    isNewImage: false
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ id: options.id });
      this.fetchDetail(options.id);
      wx.setNavigationBarTitle({ title: '编辑资讯' });
    } else {
      wx.setNavigationBarTitle({ title: '发布资讯' });
    }
  },

  fetchDetail(id) {
    const token = wx.getStorageSync('access_token');
    wx.request({
      url: `${app.globalData.baseUrl}/news/${id}/?manage=true`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const data = res.data;
          this.setData({
            title: data.title,
            title_en: data.title_en || '',
            content: data.content,
            content_en: data.content_en || '',
            imagePath: data.image
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

  chooseImage() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        this.setData({
          imagePath: res.tempFilePaths[0],
          isNewImage: true
        });
      }
    });
  },

  removeImage() {
    this.setData({
      imagePath: '',
      isNewImage: false
    });
  },

  handleSubmit() {
    const { id, title, title_en, content, content_en, imagePath, isNewImage } = this.data;
    
    if (!title || !content) {
      wx.showToast({ title: '请填写标题和内容', icon: 'none' });
      return;
    }

    this.setData({ submitting: true });
    const token = wx.getStorageSync('access_token');
    
    if (id) {
        // Update mode
        // 1. Update text
        wx.request({
            url: `${app.globalData.baseUrl}/news/${id}/`,
            method: 'PATCH',
            header: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            data: { title, title_en, content, content_en },
            success: (res) => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    if (isNewImage) {
                        // 2. Upload image if changed
                        this.uploadImage(id, token);
                    } else {
                        this.handleSuccess(res);
                    }
                } else {
                    this.handleSuccess(res);
                    this.setData({ submitting: false });
                }
            },
            fail: (err) => {
                this.handleFail(err);
                this.setData({ submitting: false });
            }
        });
    } else {
        // Create mode
        if (imagePath) {
             wx.uploadFile({
                url: `${app.globalData.baseUrl}/news/`,
                filePath: imagePath,
                name: 'image',
                formData: { title, title_en: title_en || '', content, content_en: content_en || '' },
                header: { 'Authorization': `Bearer ${token}` },
                success: (res) => {
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                        // wx.uploadFile returns data as string
                        let data = res.data;
                        try {
                            data = JSON.parse(data);
                        } catch (e) {}
                        this.handleSuccess({ statusCode: res.statusCode, data: data });
                    } else {
                        this.handleFail(res);
                        this.setData({ submitting: false });
                    }
                },
                fail: (err) => {
                    this.handleFail(err);
                    this.setData({ submitting: false });
                }
            });
        } else {
            // Text only create
             wx.request({
                url: `${app.globalData.baseUrl}/news/`,
                method: 'POST',
                header: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                data: { title, title_en, content, content_en },
                success: (res) => this.handleSuccess(res),
                fail: (err) => this.handleFail(err),
                complete: () => this.setData({ submitting: false })
            });
        }
    }
  },

  uploadImage(id, token) {
      wx.uploadFile({
          url: `${app.globalData.baseUrl}/news/${id}/upload_image/`,
          filePath: this.data.imagePath,
          name: 'image',
          header: { 'Authorization': `Bearer ${token}` },
          success: (res) => {
              if (res.statusCode >= 200 && res.statusCode < 300) {
                  this.handleSuccess({ statusCode: 200, data: {} });
              } else {
                  this.handleSuccess(res);
                  this.setData({ submitting: false });
              }
          },
          fail: (err) => {
              this.handleFail(err);
              this.setData({ submitting: false });
          }
      });
  },

  handleSuccess(res) {
    if (res.statusCode === 201 || res.statusCode === 200) {
      wx.showToast({ title: '提交成功' });
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    } else if (res.statusCode === 401) {
        wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
        wx.removeStorageSync('access_token');
        setTimeout(() => {
            wx.redirectTo({ url: '/pages/login/login' });
        }, 1500);
    } else {
      wx.showToast({ title: '提交失败: ' + res.statusCode, icon: 'none' });
      console.error(res);
    }
  },

  handleFail(err) {
    console.error(err);
    wx.showToast({ title: '网络错误', icon: 'none' });
  }
});