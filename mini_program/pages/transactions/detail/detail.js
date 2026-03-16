const app = getApp();
const i18n = require('../../../utils/i18n.js');

Page({
  data: {
    transaction: null,
    loading: true,
    t: {},
    userInfo: null,
    isBuyer: false,
    isSeller: false
  },
  onLoad: function (options) {
    this.updateLocales();
    this.checkUserRole();
    if (options.id) {
      this.fetchTransaction(options.id);
    }
  },
  onShow: function() {
    this.updateLocales();
    this.checkUserRole();
    if (this.data.transaction) {
        this.fetchTransaction(this.data.transaction.id);
    }
  },
  updateLocales: function() {
    const lang = i18n.getLocale();
    this.setData({ t: i18n.locales[lang] });
  },
  checkUserRole() {
      const userInfo = wx.getStorageSync('user_info');
      this.setData({ userInfo });
  },
  fetchTransaction: function(id) {
    const token = wx.getStorageSync('access_token');
    const userInfo = this.data.userInfo;
    
    wx.request({
      url: `${app.globalData.baseUrl}/transactions/${id}/`,
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        if (res.statusCode === 200) {
          const txn = res.data;
          
          // Determine Role
          const isBuyer = userInfo && txn.buyer === userInfo.id;
          const isSeller = userInfo && txn.seller === userInfo.id;
          
          // Format status display
          txn.status_display = this.data.t[`txn_status_${txn.status}`] || txn.status;
          // Format Date
          if (txn.created_at) txn.created_at = txn.created_at.split('T')[0];
          
          if (txn.logs) {
              txn.logs.forEach(log => {
                  if (log.timestamp) {
                      log.timestamp = log.timestamp.replace('T', ' ').substring(0, 16);
                  }
              });
          }
          
          if (txn.documents) {
              const docTypeMap = {
                  'OWNERSHIP_CERT': i18n.t('doc_name_ownership'),
                  'CLASS_CERT': i18n.t('doc_name_class'),
                  'ID_CARD': i18n.t('doc_name_id_card'),
                  'CONTRACT_DRAFT': i18n.t('doc_name_contract_draft'),
                  'SIGNED_CONTRACT': i18n.t('doc_name_signed_contract'),
                  'PAYMENT_PROOF': i18n.t('doc_name_payment_proof'),
                  'TRANSFER_PROOF': i18n.t('doc_name_transfer_proof'),
                  'OTHER': i18n.t('doc_name_other')
              };
              txn.documents.forEach(doc => {
                  doc.type_display = docTypeMap[doc.doc_type] || doc.doc_type;
                  if (doc.uploaded_at) {
                    doc.uploaded_at = doc.uploaded_at.split('T')[0];
                  }
                  // Ensure full URL for preview
                  if (doc.file && !doc.file.startsWith('http')) {
                       doc.file = app.globalData.baseUrl.replace('/api/v1', '') + doc.file;
                  }
              });
              txn.has_transfer_proof = txn.documents.some(d => d.doc_type === 'TRANSFER_PROOF');
          }

          this.setData({ 
              transaction: txn, 
              loading: false,
              isBuyer,
              isSeller
          });
        } else if (res.statusCode === 401) {
          wx.showToast({ title: '请先登录', icon: 'none' });
          setTimeout(() => {
              this.goToLogin();
          }, 1500);
        }
      }
    });
  },

  chooseDocument() {
      const that = this;
      const itemList = [
          i18n.t('doc_name_spec'),
          i18n.t('doc_name_ownership'),
          i18n.t('doc_name_class'),
          i18n.t('doc_name_transfer_proof'),
          i18n.t('doc_name_other')
      ];
      const itemKeys = ['SPECIFICATION', 'OWNERSHIP_CERT', 'CLASS_CERT', 'TRANSFER_PROOF', 'OTHER'];
      
      wx.showActionSheet({
          itemList,
          success(res) {
              const docType = itemKeys[res.tapIndex];
              wx.chooseMessageFile({
                  count: 1,
                  type: 'file',
                  success(fileRes) {
                      const file = fileRes.tempFiles[0];
                      that.uploadDocument(file, docType);
                  }
              });
          }
      });
  },

  // Buyer Review Actions
  approveDocs() {
      const that = this;
      wx.showModal({
          title: i18n.t('confirm_approve'),
          content: i18n.t('confirm_approve_content'),
          success(res) {
              if (res.confirm) {
                  that.submitDocReview(true);
              }
          }
      });
  },

  rejectDocs() {
      const that = this;
      wx.showModal({
          title: i18n.t('reject_upload'),
          content: i18n.t('reject_reason_input'),
          editable: true,
          placeholderText: i18n.t('reject_reason_placeholder'),
          success(res) {
              if (res.confirm && res.content) {
                  that.submitDocReview(false, res.content);
              }
          }
      });
  },

  submitDocReview(approved, feedback = '') {
      const token = wx.getStorageSync('access_token');
      wx.request({
          url: `${app.globalData.baseUrl}/transactions/${this.data.transaction.id}/review_docs/`,
          method: 'POST',
          header: { 'Authorization': `Bearer ${token}` },
          data: { approved, feedback },
          success: (res) => {
              if (res.statusCode === 200) {
                  wx.showToast({ title: approved ? i18n.t('approved') : i18n.t('rejected'), icon: 'success' });
                  this.fetchTransaction(this.data.transaction.id);
              }
          }
      });
  },

  previewContract() {
      // For now, just show a toast or preview a dummy PDF
      // In real app, download and open document
      const contractDoc = this.data.transaction.documents.find(d => d.doc_type === 'CONTRACT_DRAFT' || d.doc_type === 'SIGNED_CONTRACT');
      if (contractDoc) {
          this.previewDoc({ currentTarget: { dataset: { url: contractDoc.file } } });
      } else {
          wx.showToast({ title: i18n.t('contract_not_ready'), icon: 'none' });
      }
  },

  openSignModal() {
      const that = this;
      // 1. Identity Verification Simulation
      wx.showLoading({ title: i18n.t('verifying_identity'), mask: true });
      
      setTimeout(() => {
          // 2. Face Auth Simulation
          wx.showLoading({ title: i18n.t('face_recognition'), mask: true });
          
          setTimeout(() => {
              wx.hideLoading();
              
              // 3. Confirm Sign
              wx.showModal({
                  title: i18n.t('e_sign'),
                  content: i18n.t('identity_verified_sign_confirm'),
                  confirmText: i18n.t('confirm_sign'),
                  success(res) {
                      if (res.confirm) {
                          that.signContract();
                      }
                  }
              });
          }, 1500);
      }, 1500);
  },

  uploadDocument(file, docType) {
      const token = wx.getStorageSync('access_token');
      const that = this;
      
      wx.showLoading({ title: i18n.t('uploading') });
      
      wx.uploadFile({
          url: `${app.globalData.baseUrl}/transaction-documents/`,
          filePath: file.path,
          name: 'file',
          formData: {
              'transaction': this.data.transaction.id,
              'doc_type': docType,
              'description': file.name
          },
          header: {
              'Authorization': `Bearer ${token}`
          },
          success(res) {
              wx.hideLoading();
              if (res.statusCode === 201) {
                  wx.showToast({ title: i18n.t('upload_success'), icon: 'success' });
                  that.fetchTransaction(that.data.transaction.id);
                  
                  // Do not auto-update status to DOCS_REVIEW. 
                  // Let Admin review and move status, or Seller manually submit.
              } else {
                  wx.showToast({ title: i18n.t('upload_fail'), icon: 'none' });
              }
          },
          fail() {
              wx.hideLoading();
              wx.showToast({ title: i18n.t('network_error'), icon: 'none' });
          }
      });
  },

  updateStatus(status, note) {
      const token = wx.getStorageSync('access_token');
      const that = this;
      wx.request({
          url: `${app.globalData.baseUrl}/transactions/${that.data.transaction.id}/update_status/`,
          method: 'POST',
          header: { 'Authorization': `Bearer ${token}` },
          data: { status: status, note: note },
          success(res) {
              if (res.statusCode === 200) {
                  that.fetchTransaction(that.data.transaction.id);
              }
          }
      });
  },

  signContract() {
      const that = this;
      wx.showModal({
          title: i18n.t('sign_contract_title'),
          content: i18n.t('sign_contract_confirm'),
          success(res) {
              if (res.confirm) {
                  that.doSign();
              }
          }
      });
  },

  doSign() {
      const token = wx.getStorageSync('access_token');
      const that = this;
      wx.showLoading({ title: i18n.t('signing') });
      
      wx.request({
          url: `${app.globalData.baseUrl}/transactions/${that.data.transaction.id}/sign/`,
          method: 'POST',
          header: { 'Authorization': `Bearer ${token}` },
          success(res) {
              wx.hideLoading();
              if (res.statusCode === 200) {
                  wx.showToast({ title: i18n.t('sign_success'), icon: 'success' });
                  that.fetchTransaction(that.data.transaction.id);
              } else if (res.data.status === 'already signed') {
                  wx.showToast({ title: i18n.t('already_signed'), icon: 'none' });
              } else {
                  wx.showToast({ title: i18n.t('sign_fail'), icon: 'none' });
              }
          },
          fail() {
              wx.hideLoading();
              wx.showToast({ title: i18n.t('network_error'), icon: 'none' });
          }
      });
  },
  
  viewPaymentInfo() {
      wx.showModal({
          title: i18n.t('escrow_info_title'),
          content: i18n.t('escrow_info_content'),
          showCancel: false
      });
  },

  previewDoc(e) {
      const url = e.currentTarget.dataset.url;
      // Check if it's an image or doc
      const fileType = url.split('.').pop().toLowerCase();
      if (['jpg', 'jpeg', 'png', 'gif'].includes(fileType)) {
          wx.previewImage({
              urls: [url]
          });
      } else {
          wx.downloadFile({
              url: url,
              success(res) {
                  const filePath = res.tempFilePath;
                  wx.openDocument({
                      filePath: filePath,
                      showMenu: true
                  });
              }
          });
      }
  }
});
