const app = getApp()

Page({
  data: {
    stats: null,
    loading: true
  },

  onLoad() {
    this.fetchStats();
  },

  fetchStats() {
    const token = wx.getStorageSync('access_token');
    wx.showLoading({ title: '加载中' });
    
    wx.request({
      url: `${app.globalData.baseUrl}/admin/stats/`,
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        if (res.statusCode === 200) {
            const stats = res.data;
            if(stats.visitor_stats && stats.visitor_stats.recent_visitors) {
                stats.visitor_stats.recent_visitors.forEach(v => {
                    v.time = v.time.substring(11, 19); // HH:MM:SS
                });
            }
            if(stats.visitor_stats && stats.visitor_stats.online_visitors) {
                stats.visitor_stats.online_visitors.forEach(v => {
                    v.last_seen = v.last_seen.substring(11, 19); // HH:MM:SS
                });
            }

          this.setData({ stats: stats, loading: false });
          
          setTimeout(() => {
              this.drawCurve(stats.visitor_stats.curve);
          }, 100);
        } else {
          wx.showToast({ title: '加载失败', icon: 'none' });
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

  drawCurve(curveData) {
    if (!curveData || curveData.length === 0) return;

    const query = wx.createSelectorQuery()
    query.select('#curveCanvas')
      .fields({ node: true, size: true })
      .exec((res) => {
        if (!res[0]) return;
        
        const canvas = res[0].node
        const ctx = canvas.getContext('2d')
        const width = res[0].width
        const height = res[0].height

        const dpr = wx.getSystemInfoSync().pixelRatio
        canvas.width = width * dpr
        canvas.height = height * dpr
        ctx.scale(dpr, dpr)

        ctx.clearRect(0, 0, width, height)

        const maxVal = Math.max(...curveData.map(d => d.count)) || 10
        const padding = 30
        const graphWidth = width - padding * 2
        const graphHeight = height - padding * 2
        
        // Draw Grid
        ctx.beginPath()
        ctx.strokeStyle = '#f0f0f0'
        ctx.lineWidth = 0.5
        for(let i=0; i<=5; i++) {
             const y = height - padding - (i/5 * graphHeight);
             ctx.moveTo(padding, y);
             ctx.lineTo(width - padding, y);
        }
        ctx.stroke();

        // Draw Axes
        ctx.beginPath()
        ctx.strokeStyle = '#e5e5e5'
        ctx.lineWidth = 1
        ctx.moveTo(padding, padding)
        ctx.lineTo(padding, height - padding)
        ctx.lineTo(width - padding, height - padding)
        ctx.stroke()

        // Draw Line
        ctx.beginPath()
        ctx.strokeStyle = '#1890ff'
        ctx.lineWidth = 2
        
        const stepX = graphWidth / 23 
        
        curveData.forEach((d, index) => {
            const x = padding + d.hour * stepX
            const y = height - padding - (d.count / maxVal * graphHeight)
            
            if (index === 0) {
                ctx.moveTo(x, y)
            } else {
                ctx.lineTo(x, y)
            }
        })
        ctx.stroke()
        
        // Draw labels
        ctx.fillStyle = '#999'
        ctx.font = '10px sans-serif'
        ctx.textAlign = 'center'
        
        const xLabels = [0, 6, 12, 18, 23]
        xLabels.forEach(h => {
             const x = padding + h * stepX
             ctx.fillText(h + 'h', x, height - padding + 15)
        })
        
        ctx.textAlign = 'right'
        ctx.fillText(maxVal, padding - 5, padding + 10)
        ctx.fillText('0', padding - 5, height - padding)
      })
  }
})