const app = getApp()

Page({
  data: {
    crew: null,
    loading: false,
    genders: [],
    genderIndex: 0,
    types: [],
    typeIndex: 0,
    statuses: [],
    statusIndex: 0,
    isEdit: false,
    t: {}
  },

  onLoad: function (options) {
    this.updateLocales();
    this.checkProfile();
  },
  
  onShow: function() {
    this.updateLocales();
  },

  updateLocales: function() {
    const i18n = require('../../../utils/i18n.js');
    const lang = i18n.getLocale();
    this.setData({
      t: i18n.locales[lang],
      genders: [
        { value: 'M', label: i18n.t('gender_male') },
        { value: 'F', label: i18n.t('gender_female') }
      ],
      types: [
        { value: 'DOMESTIC', label: i18n.t('type_domestic') },
        { value: 'INTERNATIONAL', label: i18n.t('type_international') }
      ],
      statuses: [
        { value: 'AVAILABLE', label: i18n.t('status_available') },
        { value: 'BUSY', label: i18n.t('status_busy') },
        { value: 'ON_LEAVE', label: i18n.t('status_on_leave') }
      ]
    });
    wx.setNavigationBarTitle({
      title: i18n.t('crew_services')
    });
  },

  checkProfile: function () {
    const token = wx.getStorageSync('access_token');
    if (!token) return;

    wx.request({
      url: `${app.globalData.baseUrl}/user/info/`,
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        if (res.statusCode === 200) {
          const info = res.data;
          const crewProfile = info.crew_profile || {};
          
          // Map profile fields to form fields
          const formData = {
              name: crewProfile.real_name || info.username,
              position: crewProfile.position,
              gender: crewProfile.gender || 'M',
              total_sea_experience: crewProfile.years_of_experience,
              cert_number: crewProfile.certificate_number,
              phone: info.mobile || info.phone_number,
              email: info.email,
              status: crewProfile.status || 'AVAILABLE',
              resume: crewProfile.bio,
          };
          
          // Update indices
          const genderIndex = this.data.genders.findIndex(g => g.value === formData.gender);
          const statusIndex = this.data.statuses.findIndex(s => s.value === formData.status);
          
          this.setData({ 
              crew: formData,
              genderIndex: genderIndex > -1 ? genderIndex : 0,
              statusIndex: statusIndex > -1 ? statusIndex : 0,
              isEdit: true
          });
        } else if (res.statusCode === 401) {
            wx.removeStorageSync('access_token');
            wx.showModal({
                title: '提示',
                content: '登录已过期，请重新登录',
                showCancel: false,
                success: (res) => {
                    if (res.confirm) {
                        wx.navigateTo({ url: '/pages/login/login' });
                    }
                }
            });
        }
      },
      fail: () => {
          // Silent fail or toast
      }
    });
  },

  onGenderChange: function(e) {
      this.setData({ genderIndex: e.detail.value });
  },
  onTypeChange: function(e) {
      this.setData({ typeIndex: e.detail.value });
  },
  onStatusChange: function(e) {
      this.setData({ statusIndex: e.detail.value });
  },

  onSubmit: function (e) {
      const data = e.detail.value;
      this.setData({ loading: true });
      const token = wx.getStorageSync('access_token');
      
      // Map form fields back to profile fields
      const profileData = {
          role: 'CREW', // Ensure role switch
          real_name: data.name,
          position: data.position,
          gender: this.data.genders[this.data.genderIndex].value,
          years_of_experience: data.total_sea_experience,
          certificate_number: data.cert_number,
          status: this.data.statuses[this.data.statusIndex].value,
          bio: data.resume,
          // Mobile/Email updates basic user info
          mobile: data.phone,
          email: data.email
      };

      wx.request({
          url: `${app.globalData.baseUrl}/user/profile/update/`,
          method: 'PUT',
          header: { 
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
          },
          data: profileData,
          success: (res) => {
              if (res.statusCode === 200) {
                  wx.showToast({ title: '简历保存成功' });
                  setTimeout(() => wx.navigateBack(), 1500);
              } else {
                  wx.showToast({ title: '保存失败', icon: 'none' });
              }
          },
          complete: () => {
              this.setData({ loading: false });
          }
      });
  }
});
