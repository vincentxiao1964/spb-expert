const app = getApp();

Page({
    data: {
        transactions: [],
        loading: false,
        t: {}
    },
    onLoad() {
        this.updateLocales();
    },
    onShow() {
        this.updateLocales();
        this.fetchTransactions();
    },
    updateLocales() {
        const i18n = require('../../../../../utils/i18n.js');
        const lang = i18n.getLocale();
        this.setData({
            t: i18n.locales[lang]
        });
        wx.setNavigationBarTitle({
            title: i18n.t('transaction_manager')
        });
    },
    fetchTransactions() {
        const token = wx.getStorageSync('access_token');
        if (!token) return;

        this.setData({ loading: true });
        
        const i18n = require('../../../../../utils/i18n.js');
        const lang = i18n.getLocale();
        
        wx.request({
            url: `${app.globalData.baseUrl}/transactions/`,
            header: { 
                'Authorization': `Bearer ${token}`,
                'Accept-Language': lang === 'zh' ? 'zh-hans' : 'en'
            },
            success: (res) => {
                if (res.statusCode === 200) {
                    this.setData({ transactions: res.data.results || res.data });
                }
            },
            complete: () => {
                this.setData({ loading: false });
            }
        });
    },
    handleCancel(e) {
        const id = e.currentTarget.dataset.id;
        const token = wx.getStorageSync('access_token');
        const i18n = require('../../../../../utils/i18n.js');
        const lang = i18n.getLocale();
        const t = i18n.locales[lang];
        
        const item = (this.data.transactions || []).find(x => String(x.id) === String(id));
        if (!item) return;
        
        const blockedStatuses = ['COMPLETED', 'PAYMENT_VERIFIED', 'CONTRACT_SIGNING'];
        if (blockedStatuses.includes(item.status)) {
            wx.showToast({ title: '当前状态不可取消', icon: 'none' });
            return;
        }
        
        wx.showModal({
            title: '取消交易',
            content: '确定要将该交易标记为【已取消】吗？此操作不可恢复。',
            confirmColor: '#e64340',
            success: (res) => {
                if (!res.confirm) return;
                wx.request({
                    url: `${app.globalData.baseUrl}/transactions/${id}/update_status/`,
                    method: 'POST',
                    header: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                    data: { status: 'CANCELLED', note: 'Admin cancel via manager' },
                    success: (res2) => {
                        if (res2.statusCode === 200) {
                            wx.showToast({ title: '已取消', icon: 'none' });
                            this.setData({
                                transactions: this.data.transactions.map(x => {
                                    if (String(x.id) === String(id)) {
                                        return { ...x, status: 'CANCELLED', status_display: t.txn_status_CANCELLED || '已取消' };
                                    }
                                    return x;
                                })
                            });
                        } else if (res2.statusCode === 403) {
                            wx.showToast({ title: '无权限取消', icon: 'none' });
                        } else if (res2.statusCode === 401) {
                            wx.showToast({ title: t.login_expired || '登录已过期', icon: 'none' });
                        } else {
                            const msg = (res2.data && (res2.data.error || res2.data.detail)) || '操作失败';
                            wx.showToast({ title: msg, icon: 'none' });
                        }
                    },
                    fail: () => {
                        wx.showToast({ title: t.network_error || '网络错误', icon: 'none' });
                    }
                });
            }
        });
    },
    goToCreate() {
        wx.navigateTo({
            url: '/pages/admin/transactions/create/create'
        });
    }
});
