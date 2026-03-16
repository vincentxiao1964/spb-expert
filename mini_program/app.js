App({
  onLaunch() {
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)
  },
  globalData: {
    userInfo: null,
    project: 'spb',
    env: 'prod',
    baseUrls: {
      spb: {
        dev: 'http://127.0.0.1:8000/api/v1',
        prod: 'https://www.barge-expert.com/api/v1'
      },
      hymart: {
        dev: 'http://127.0.0.1:8001/api/v1',
        prod: 'https://hymartt.com/api/v1'
      }
    },
    get baseUrl() {
      const env = this.env || 'dev'
      const project = this.project || 'spb'
      const map = this.baseUrls[project] || this.baseUrls['spb']
      return map[env]
    }
  }
})
