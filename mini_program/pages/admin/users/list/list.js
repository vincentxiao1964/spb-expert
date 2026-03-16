const app = getApp();

Page({
  data: {
    users: [],
    query: '',
    isLoading: false
  },

  onLoad(options) {
    this.fetchUsers();
  },

  onPullDownRefresh() {
    this.fetchUsers();
  },

  onInput(e) {
    this.setData({ query: e.detail.value });
  },

  onSearch() {
    this.fetchUsers();
  },

  fetchUsers() {
    this.setData({ isLoading: true });
    const token = wx.getStorageSync('access_token');
    
    let url = `${app.globalData.baseUrl}/user/search/`;
    if (this.data.query) {
      url += `?q=${this.data.query}`;
    }

    wx.request({
      url: url,
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ users: res.data });
        }
      },
      complete: () => {
        this.setData({ isLoading: false });
        wx.stopPullDownRefresh();
      }
    });
  },
  
  callUser(e) {
      const phone = e.currentTarget.dataset.phone;
      if (phone) {
          wx.makePhoneCall({ phoneNumber: phone });
      } else {
          wx.showToast({ title: '无电话号码', icon: 'none' });
      }
  }
});