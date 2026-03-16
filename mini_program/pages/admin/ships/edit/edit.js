const app = getApp();

Page({
  data: {
    id: null,
    typeIndex: 0,
    categoryIndex: 0,
    types: [
      { label: '出售', value: 'SELL' },
      { label: '求购', value: 'BUY' },
      { label: '出租', value: 'CHARTER_OFFER' },
      { label: '求租', value: 'CHARTER_REQUEST' }
    ],
    categories: [
      { label: '自航甲板驳', value: 'SELF_PROPELLED' },
      { label: '非自航甲板驳', value: 'NON_SELF_PROPELLED' }
    ],
    dwt: '',
    length: '',
    width: '',
    depth: '',
    build_year: '',
    description: '',
    contact_info: '',
    
    existingImages: [], // {id, image, is_schematic}
    newImages: [], // local paths
    
    submitting: false,
    isAdmin: false,
    status: ''
  },

  onLoad(options) {
    this.fetchUserInfo(); // Always fetch user info to check admin status
    
    if (options.id) {
      this.setData({ id: options.id });
      this.fetchDetail(options.id);
      wx.setNavigationBarTitle({ title: '编辑船源' });
    } else {
      wx.setNavigationBarTitle({ title: '发布船源' });
    }
  },

  fetchUserInfo() {
    const token = wx.getStorageSync('access_token');
    wx.request({
      url: `${app.globalData.baseUrl}/user/info/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
              isAdmin: res.data.is_staff || res.data.is_superuser
          });
          
          // If contact_info is empty, fill it with phone number (only for new listings usually)
          if (!this.data.id && !this.data.contact_info && res.data.phone_number) {
            this.setData({
              contact_info: res.data.phone_number
            });
          }
        }
      }
    });
  },

  fetchDetail(id) {
    const token = wx.getStorageSync('access_token');
    // Add manage=true to allow admins to see pending listings of other users
    wx.request({
      url: `${app.globalData.baseUrl}/listings/${id}/?manage=true`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const data = res.data;
          // Find indices for picker
          const typeIndex = this.data.types.findIndex(t => t.value === data.listing_type);
          const categoryIndex = this.data.categories.findIndex(c => c.value === data.ship_category);
          
          // Process images to ensure they have full URLs
          const API_BASE = app.globalData.baseUrl;
          const siteRoot = API_BASE.split('/api')[0];
          
          const existingImages = (data.images || []).map(img => {
            if (img.image && !img.image.startsWith('http')) {
                img.image = siteRoot + img.image;
            }
            return img;
          });
          
          this.setData({
            typeIndex: typeIndex >= 0 ? typeIndex : 0,
            categoryIndex: categoryIndex >= 0 ? categoryIndex : 0,
            dwt: data.dwt || '',
            length: data.length || '',
            width: data.width || '',
            depth: data.depth || '',
            build_year: data.build_year || '',
            description: data.description || '',
            contact_info: data.contact_info || '',
            existingImages: existingImages,
            status: data.status
          });
        }
      }
    });
  },

  handleAudit(e) {
      const status = e.currentTarget.dataset.status;
      const id = this.data.id;
      if (!id) return;

      const token = wx.getStorageSync('access_token');
      
      wx.showLoading({ title: '处理中...' });

      wx.request({
          url: `${app.globalData.baseUrl}/listings/${id}/?manage=true`,
          method: 'PATCH',
          header: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
          },
          data: { status: status },
          success: (res) => {
              if (res.statusCode >= 200 && res.statusCode < 300) {
                  wx.showToast({ title: '操作成功' });
                  this.setData({ status: status });
                  // Refresh previous page
                  const pages = getCurrentPages();
                  const prevPage = pages[pages.length - 2];
                  if (prevPage && prevPage.fetchShips) {
                      prevPage.fetchShips();
                  }
                  setTimeout(() => {
                      wx.navigateBack();
                  }, 1500);
              } else {
                  wx.showToast({ title: '操作失败', icon: 'none' });
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

  handleTypeChange(e) {
    this.setData({ typeIndex: e.detail.value });
  },

  handleCategoryChange(e) {
    this.setData({ categoryIndex: e.detail.value });
  },

  handleInput(e) {
    const field = e.currentTarget.dataset.field;
    this.setData({
      [field]: e.detail.value
    });
  },

  chooseImage() {
    wx.chooseImage({
      count: 9,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        this.setData({
          newImages: [...this.data.newImages, ...res.tempFilePaths]
        });
      }
    });
  },

  removeExistingImage(e) {
    const id = e.currentTarget.dataset.id;
    const index = e.currentTarget.dataset.index;
    const token = wx.getStorageSync('access_token');
    
    wx.showModal({
      title: '确认删除图片',
      content: '确定要删除这张图片吗？',
      success: (res) => {
        if (res.confirm) {
          // Call API to delete image
          wx.request({
            url: `${app.globalData.baseUrl}/listing_images/${id}/`,
            method: 'DELETE',
            header: {
              'Authorization': `Bearer ${token}`
            },
            success: (delRes) => {
              if (delRes.statusCode === 204) {
                const existingImages = this.data.existingImages;
                existingImages.splice(index, 1);
                this.setData({ existingImages });
                wx.showToast({ title: '已删除' });
              } else {
                wx.showToast({ title: '删除失败', icon: 'none' });
              }
            }
          });
        }
      }
    });
  },

  removeNewImage(e) {
    const index = e.currentTarget.dataset.index;
    const newImages = this.data.newImages;
    newImages.splice(index, 1);
    this.setData({ newImages });
  },

  handleSubmit() {
    const { 
      id, typeIndex, categoryIndex, types, categories,
      dwt, length, width, depth, build_year, description, contact_info,
      newImages 
    } = this.data;

    if (!contact_info) {
      wx.showToast({ title: '请填写联系方式', icon: 'none' });
      return;
    }

    this.setData({ submitting: true });
    
    const formData = {
      listing_type: types[typeIndex].value,
      ship_category: categories[categoryIndex].value,
      dwt: dwt || '',
      length: length || '',
      width: width || '',
      depth: depth || '',
      build_year: build_year || null,
      description: description,
      contact_info: contact_info
    };

    const token = wx.getStorageSync('access_token');
    const url = id ? `${app.globalData.baseUrl}/listings/${id}/?manage=true` : `${app.globalData.baseUrl}/listings/`;
    const method = id ? 'PATCH' : 'POST';

    wx.request({
      url: url,
      method: method,
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: formData,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          const listingId = res.data.id;
          
          // Upload new images if any
          if (newImages.length > 0) {
            this.uploadImages(listingId, newImages);
          } else {
            wx.showToast({ title: '提交成功' });
            setTimeout(() => {
              wx.navigateBack();
            }, 1500);
            this.setData({ submitting: false });
          }
        } else if (res.statusCode === 401) {
          wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
          wx.removeStorageSync('access_token');
          setTimeout(() => {
            wx.redirectTo({ url: '/pages/login/login' });
          }, 1500);
          this.setData({ submitting: false });
        } else {
          console.error(res);
          let msg = '提交失败';
          if (res.data) {
              // Try to extract first error message
              if (typeof res.data === 'object') {
                  const values = Object.values(res.data);
                  if (values.length > 0) {
                      const firstError = values[0];
                      if (Array.isArray(firstError)) {
                          msg = firstError[0];
                      } else if (typeof firstError === 'string') {
                          msg = firstError;
                      }
                  }
              }
          }
          wx.showToast({ title: msg, icon: 'none' });
          this.setData({ submitting: false });
        }
      },
      fail: (err) => {
        console.error(err);
        wx.showToast({ title: '网络错误', icon: 'none' });
        this.setData({ submitting: false });
      }
    });
  },

  uploadImages(listingId, images) {
    let uploadedCount = 0;
    const total = images.length;
    const token = wx.getStorageSync('access_token');
    
    // Recursive or loop upload? Parallel is faster but might hit limit.
    // Let's do parallel with Promise.all if supported, but wx.uploadFile is callback based.
    // Use simple loop with counter.
    
    let hasError = false;

    const uploadOne = (filePath) => {
      return new Promise((resolve, reject) => {
        wx.uploadFile({
          url: `${app.globalData.baseUrl}/listings/${listingId}/upload_image/`,
          filePath: filePath,
          name: 'image',
          header: {
            'Authorization': `Bearer ${token}`
          },
          success: (res) => {
            if (res.statusCode === 201 || res.statusCode === 200) {
              resolve();
            } else {
              reject(res);
            }
          },
          fail: (err) => reject(err)
        });
      });
    };

    const promises = images.map(img => uploadOne(img));

    Promise.all(promises)
      .then(() => {
        wx.showToast({ title: '提交成功' });
        setTimeout(() => {
          wx.navigateBack();
        }, 1500);
      })
      .catch((err) => {
        console.error('Image upload failed', err);
        if (err && err.statusCode === 401) {
            wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
            wx.removeStorageSync('access_token');
            setTimeout(() => {
                wx.redirectTo({ url: '/pages/login/login' });
            }, 1500);
        } else {
            wx.showToast({ title: '部分图片上传失败', icon: 'none' });
        }
      })
      .finally(() => {
        this.setData({ submitting: false });
      });
  }
});