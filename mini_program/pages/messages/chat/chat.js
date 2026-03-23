const app = getApp()

Page({
  data: {
    messages: [],
    inputValue: '',
    toView: '',
    targetUserId: null,
    targetUserName: '',
    myUserId: null,
    loading: false
  },

  onLoad(options) {
    const targetId = options.userId || options.targetUserId;
    const targetName = options.userName || options.targetUsername || '用户';
    
    if (targetId) {
      this.setData({
        targetUserId: parseInt(targetId),
        targetUserName: targetName
      });
      wx.setNavigationBarTitle({
        title: `与 ${this.data.targetUserName} 对话`
      });
    }
    
    const myUserId = wx.getStorageSync('user_id');
    if (myUserId) {
        this.setData({ myUserId: parseInt(myUserId) });
    }
    
    this.fetchMessages();
    
    this.timer = setInterval(() => {
        this.fetchMessages(true);
    }, 10000);
  },
  
  onUnload() {
      if (this.timer) clearInterval(this.timer);
  },

  onInput(e) {
    this.setData({
      inputValue: e.detail.value
    });
  },
  
  fetchMessages(silent = false) {
      if (!silent) wx.showLoading({ title: '加载中' });
      const token = wx.getStorageSync('access_token');
      if (!token) return;

      wx.request({
          url: `${app.globalData.baseUrl}/private-messages/?target_user_id=${this.data.targetUserId}`,
          header: { 'Authorization': `Bearer ${token}` },
          success: (res) => {
              if (res.statusCode === 200) {
                  const msgs = res.data.results || res.data;
                  // API sorts by created_at asc now
                  
                  this.setData({
                      messages: msgs,
                      toView: msgs.length > 0 ? `msg-${msgs[msgs.length - 1].id}` : ''
                  });
              }
          },
          complete: () => {
              if (!silent) wx.hideLoading();
              wx.stopPullDownRefresh();
          }
      })
  },

  chooseImage() {
    wx.chooseImage({
      count: 1,
      sizeType: ['original', 'compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePaths = res.tempFilePaths;
        this.uploadImage(tempFilePaths[0]);
      }
    })
  },

  uploadImage(filePath) {
    const token = wx.getStorageSync('access_token');
    wx.showLoading({ title: '发送中' });
    
    wx.uploadFile({
      url: `${app.globalData.baseUrl}/private-messages/`,
      filePath: filePath,
      name: 'image',
      header: {
        'Authorization': `Bearer ${token}`
      },
      formData: {
        'receiver': this.data.targetUserId,
        'content': '' // Optional: send empty content or some placeholder
      },
      success: (res) => {
        if (res.statusCode === 201) {
          this.fetchMessages(true);
        } else {
          if (res.statusCode === 400) {
            let msg = '内容可能含违规信息';
            try {
              const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
              if (data && (data.detail || data.error)) msg = data.detail || data.error;
            } catch (e) {}
            wx.showToast({ title: msg, icon: 'none' });
            return;
          }
          wx.showToast({ title: '发送失败', icon: 'none' });
        }
      },
      fail: (err) => {
        wx.showToast({ title: '网络错误', icon: 'none' });
      },
      complete: () => {
        wx.hideLoading();
      }
    })
  },

  previewImage(e) {
    const current = e.currentTarget.dataset.src;
    wx.previewImage({
      current: current, // Current image
      urls: [current] // To be robust, ideally collect all images in chat, but single is fine for now
    })
  },

  goToProfile(e) {
    const userId = e.currentTarget.dataset.id;
    if (!userId) return;
    wx.navigateTo({
      url: `/pages/users/detail/detail?id=${userId}`
    });
  },

  sendMessage() {
    const content = this.data.inputValue.trim();
    if (!content) return;

    const token = wx.getStorageSync('access_token');
    
    wx.request({
        url: `${app.globalData.baseUrl}/private-messages/`,
        method: 'POST',
        header: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        data: {
            receiver: this.data.targetUserId,
            content: content
        },
        success: (res) => {
            if (res.statusCode === 201) {
                this.setData({ inputValue: '' });
                this.fetchMessages(true);
            } else {
                if (res.statusCode === 400) {
                    wx.showToast({ title: '内容可能含违规信息', icon: 'none' });
                    return;
                }
                wx.showToast({ title: '发送失败', icon: 'none' });
            }
        }
    });
  },
  
  onPullDownRefresh() {
      this.fetchMessages();
  }
})
