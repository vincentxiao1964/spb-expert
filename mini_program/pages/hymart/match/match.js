const app = getApp();

Page({
  data: {
    cargoTypes: [
      { label: '散货 (Bulk)', value: 'BULK' },
      { label: '件杂货 (General)', value: 'GENERAL' },
      { label: '集装箱 (Container)', value: 'CONTAINER' },
      { label: '液货 (Liquid)', value: 'LIQUID' }
    ],
    cargoTypeIndex: 0,
    loadingDate: '',
    today: new Date().toISOString().substring(0, 10),
    submitting: false,
    matches: null,
    cargoId: null,
    sortModes: [
      { label: '按综合得分', value: 'score' },
      { label: '载重更贴近', value: 'dwt' },
      { label: '吃水更贴近', value: 'draft' }
    ],
    sortModeIndex: 0
  },

  onLoad: function (options) {
    // 允许未登录查看，提交时再检查
  },

  bindCargoTypeChange: function(e) {
    this.setData({
      cargoTypeIndex: e.detail.value
    });
  },

  bindDateChange: function(e) {
    this.setData({
      loadingDate: e.detail.value
    });
  },

  submitForm: function(e) {
    const formData = e.detail.value;
    const that = this;
    
    // Check login first
    const token = wx.getStorageSync('access_token');
    if (!token) {
        wx.showModal({
            title: '需要登录',
            content: '使用 Hymart 智能匹配需要先登录账号。',
            confirmText: '去登录',
            success: (res) => {
                if (res.confirm) {
                    wx.switchTab({ url: '/pages/mine/mine' });
                }
            }
        });
        return;
    }

    // Validation
    if (!formData.weight) {
      wx.showToast({
        title: '请填写货物重量',
        icon: 'none'
      });
      return;
    }

    this.setData({ submitting: true, matches: null });

    // 1. Create Cargo Request
    const dwtTol = formData.dwt_tolerance_percent ? parseFloat(formData.dwt_tolerance_percent) : 10;
    const draftTol = formData.draft_tolerance_percent ? parseFloat(formData.draft_tolerance_percent) : 10;
    const requestData = {
      cargo_type: this.data.cargoTypes[this.data.cargoTypeIndex].value,
      weight: parseFloat(formData.weight),
      volume: formData.volume ? parseFloat(formData.volume) : null,
      max_draft: formData.max_draft ? parseFloat(formData.max_draft) : null,
      dwt_tolerance_percent: isNaN(dwtTol) ? 10 : dwtTol,
      draft_tolerance_percent: isNaN(draftTol) ? 10 : draftTol,
      origin: 'ANY', // Default value since field is removed
      destination: 'ANY', // Default value
      loading_date: this.data.today // Default to today
    };

    // Construct Base URL correctly (remove /api/v1 if present, as hymart is at root)
    let baseUrl = app.globalData.baseUrl;
    if (baseUrl.endsWith('/api/v1')) {
        baseUrl = baseUrl.replace('/api/v1', '');
    }
    // Remove trailing slash if present
    if (baseUrl.endsWith('/')) {
        baseUrl = baseUrl.slice(0, -1);
    }

    wx.request({
      url: `${baseUrl}/hymart/api/cargo-requests/`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: requestData,
      success: (res) => {
        if (res.statusCode === 201) {
          wx.showToast({
            title: '匹配完成',
            icon: 'success'
          });
          
          // Get the cargo ID from response
          const cargoId = res.data.id; // Or res.data.cargo.id depending on view return
          
          // Fetch matches
          that.findMatches(cargoId);
          
        } else if (res.statusCode === 401) {
          wx.showModal({
            title: '登录过期',
            content: '您的登录信息已过期（或环境已切换），请重新登录。',
            showCancel: false,
            success: (res) => {
              if (res.confirm) {
                wx.removeStorageSync('access_token');
                wx.switchTab({ url: '/pages/mine/mine' });
              }
            }
          });
          that.setData({ submitting: false });
        } else {
          wx.showToast({
            title: '提交失败: ' + (JSON.stringify(res.data.detail || res.data)),
            icon: 'none',
            duration: 3000
          });
          that.setData({ submitting: false });
        }
      },
      fail(err) {
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
        that.setData({ submitting: false });
      }
    });
  },

  findMatches: function(cargoId) {
    const that = this;
    const token = wx.getStorageSync('access_token');
    
    // Construct Base URL correctly
    let baseUrl = app.globalData.baseUrl;
    if (baseUrl.endsWith('/api/v1')) {
        baseUrl = baseUrl.replace('/api/v1', '');
    }
    if (baseUrl.endsWith('/')) {
        baseUrl = baseUrl.slice(0, -1);
    }

    wx.request({
      url: `${baseUrl}/hymart/api/cargo-requests/${cargoId}/find_matches/`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success(res) {
        if (res.statusCode === 200) {
          const cargo = res.data.cargo || null;
          const matches = res.data.matches || [];
          const sorted = that.sortMatches(matches);
          that.setData({
            matches: sorted,
            cargoId: cargo ? cargo.id : null
          });
          
          if (matches.length === 0) {
              wx.showToast({ title: '暂无匹配', icon: 'none' });
          } else {
              wx.showToast({ title: `找到 ${matches.length} 条匹配`, icon: 'success' });
          }
        } else {
            wx.showToast({
                title: '获取结果失败',
                icon: 'none'
            });
        }
      },
      fail(err) {
          console.error('Find matches failed', err);
          wx.showToast({
              title: '网络请求失败',
              icon: 'none'
          });
      },
      complete() {
        that.setData({ submitting: false });
      }
    });
  },

  sortMatches: function(matches) {
    if (!matches || matches.length === 0) return [];
    const modeObj = this.data.sortModes[this.data.sortModeIndex] || this.data.sortModes[0];
    const mode = modeObj.value;
    const list = matches.slice();

    if (mode === 'score') {
      list.sort((a, b) => {
        const av = typeof a.score === 'number' ? a.score : 0;
        const bv = typeof b.score === 'number' ? b.score : 0;
        return bv - av;
      });
    } else if (mode === 'dwt') {
      list.sort((a, b) => {
        const ad = typeof a.dwt_diff_percent === 'number' ? Math.abs(a.dwt_diff_percent) : Number.MAX_VALUE;
        const bd = typeof b.dwt_diff_percent === 'number' ? Math.abs(b.dwt_diff_percent) : Number.MAX_VALUE;
        return ad - bd;
      });
    } else if (mode === 'draft') {
      list.sort((a, b) => {
        const au = typeof a.draft_utilization_percent === 'number' ? Math.abs(100 - a.draft_utilization_percent) : Number.MAX_VALUE;
        const bu = typeof b.draft_utilization_percent === 'number' ? Math.abs(100 - b.draft_utilization_percent) : Number.MAX_VALUE;
        return au - bu;
      });
    }

    return list;
  },

  onSortModeChange: function(e) {
    const index = parseInt(e.detail.value, 10) || 0;
    this.setData({ sortModeIndex: index });
    if (this.data.matches && this.data.matches.length > 0) {
      const sorted = this.sortMatches(this.data.matches);
      this.setData({ matches: sorted });
    }
  },

  viewShipDetail: function(e) {
    const shipId = e.currentTarget.dataset.id;
    const matchId = e.currentTarget.dataset.matchId;
    const cargoId = this.data.cargoId;

    const token = wx.getStorageSync('access_token');
    if (matchId && cargoId && token) {
      let baseUrl = app.globalData.baseUrl;
      if (baseUrl.endsWith('/api/v1')) {
          baseUrl = baseUrl.replace('/api/v1', '');
      }
      if (baseUrl.endsWith('/')) {
          baseUrl = baseUrl.slice(0, -1);
      }

      wx.request({
        url: `${baseUrl}/hymart/api/cargo-requests/${cargoId}/mark_match_viewed/`,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        data: {
          match_id: matchId
        }
      });
    }

    wx.navigateTo({
      url: `/pages/listings/detail/detail?id=${shipId}`
    });
  },

  deleteMatch: function(e) {
    const matchId = e.currentTarget.dataset.matchId;
    const cargoId = this.data.cargoId;
    const that = this;

    if (!matchId || !cargoId) return;

    wx.showModal({
        title: '删除确认',
        content: '确定要删除这条匹配结果吗？',
        success(res) {
            if (res.confirm) {
                that.doDeleteMatch(cargoId, matchId);
            }
        }
    });
  },

  doDeleteMatch: function(cargoId, matchId) {
      const that = this;
      const token = wx.getStorageSync('access_token');
      
      let baseUrl = app.globalData.baseUrl;
      if (baseUrl.endsWith('/api/v1')) {
          baseUrl = baseUrl.replace('/api/v1', '');
      }
      if (baseUrl.endsWith('/')) {
          baseUrl = baseUrl.slice(0, -1);
      }

      wx.request({
          url: `${baseUrl}/hymart/api/cargo-requests/${cargoId}/delete_match/`,
          method: 'POST',
          header: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
          },
          data: { match_id: matchId },
          success(res) {
              if (res.statusCode === 200) {
                  wx.showToast({ title: '删除成功' });
                  // Remove from local list
                  const newMatches = that.data.matches.filter(m => m.id !== matchId);
                  that.setData({ matches: newMatches });
              } else {
                  wx.showToast({ title: '删除失败', icon: 'none' });
              }
          },
          fail() {
              wx.showToast({ title: '网络错误', icon: 'none' });
          }
      });
  }
});
