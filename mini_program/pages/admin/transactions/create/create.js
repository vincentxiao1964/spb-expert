const app = getApp();
const i18n = require('../../../../utils/i18n.js');

Page({
    data: {
        currentStep: 1, // 1: Summary, 2: Select Seller, 3: Select Buyer, 4: Confirm
        
        // Step 1: Summary
        transactionTitle: '',
        
        // Common User List
        userList: [],
        
        // Step 2: Seller
        selectedSeller: null,
        sellerIndex: -1,

        // Step 3: Buyer
        selectedBuyer: null,
        buyerIndex: -1,

        loading: false
    },

    onLoad() {
        this.fetchUsers();
    },

    fetchUsers() {
        const token = wx.getStorageSync('access_token');
        wx.request({
            url: `${app.globalData.baseUrl}/user/search/`, // No query returns all (limit 100)
            header: { 'Authorization': `Bearer ${token}` },
            success: (res) => {
                if (res.statusCode === 200) {
                    const users = res.data.map(u => ({
                        ...u,
                        displayName: `${u.username} ${u.phone_number ? '('+u.phone_number+')' : ''}`
                    }));
                    this.setData({ userList: users });
                }
            }
        });
    },

    // Step 1: Title Input
    onTitleInput(e) {
        this.setData({ transactionTitle: e.detail.value });
    },

    confirmTitle() {
        if (!this.data.transactionTitle) return;
        this.setData({ currentStep: 2 });
    },

    // Step 2: Select Seller
    bindSellerChange(e) {
        const index = e.detail.value;
        const seller = this.data.userList[index];
        this.setData({
            sellerIndex: index,
            selectedSeller: seller
        });
    },

    confirmSeller() {
        if (!this.data.selectedSeller) {
            wx.showToast({ title: '请选择卖家', icon: 'none' });
            return;
        }
        this.setData({ currentStep: 3 });
    },

    // Step 3: Select Buyer
    bindBuyerChange(e) {
        const index = e.detail.value;
        const buyer = this.data.userList[index];
        this.setData({
            buyerIndex: index,
            selectedBuyer: buyer
        });
    },

    confirmBuyer() {
        if (!this.data.selectedBuyer) {
            wx.showToast({ title: '请选择买家', icon: 'none' });
            return;
        }
        this.setData({ currentStep: 4 });
    },

    // Reset steps
    resetStep1() {
        this.setData({ currentStep: 1, transactionTitle: '', selectedSeller: null, sellerIndex: -1 });
    },
    resetStep2() {
        this.setData({ currentStep: 2, selectedSeller: null, sellerIndex: -1 });
    },
    resetStep3() {
        this.setData({ currentStep: 3, selectedBuyer: null, buyerIndex: -1 });
    },

    // Step 4: Submit
    submitTransaction() {
        if (!this.data.transactionTitle || !this.data.selectedBuyer || !this.data.selectedSeller) return;
        
        const token = wx.getStorageSync('access_token');
        this.setData({ loading: true });

        wx.request({
            url: `${app.globalData.baseUrl}/transactions/`,
            method: 'POST',
            header: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            data: {
                title: this.data.transactionTitle,
                listing: null, // No listing linked
                seller: this.data.selectedSeller.id,
                buyer: this.data.selectedBuyer.id
            },
            success: (res) => {
                if (res.statusCode === 201) {
                    wx.showToast({ title: '发起成功' });
                    setTimeout(() => {
                        wx.redirectTo({
                            url: `/pages/transactions/detail/detail?id=${res.data.id}`
                        });
                    }, 1500);
                } else {
                    wx.showToast({ title: '失败: ' + (res.data.detail || 'Unknown'), icon: 'none' });
                }
            },
            fail: () => {
                wx.showToast({ title: '网络错误', icon: 'none' });
            },
            complete: () => {
                this.setData({ loading: false });
            }
        });
    }
});