const app = getApp();
Page({
    data: { inquiries: [], loading: true },
    onShow() { this.fetchInquiries(); },
    fetchInquiries() {
        const token = wx.getStorageSync('access_token');
        if (!token) return;
        wx.request({
            url: `${app.globalData.baseUrl}/inquiries/`,
            header: { 'Authorization': `Bearer ${token}` },
            success: (res) => {
                if(res.statusCode === 200) {
                    this.setData({ inquiries: res.data.results || res.data, loading: false });
                }
            }
        });
    },
    goToDetail(e) {
        wx.navigateTo({ url: `/pages/inquiries/detail/detail?id=${e.currentTarget.dataset.id}` });
    }
});
