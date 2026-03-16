const app = getApp()
const i18n = require('../../../utils/i18n.js');

Page({
  data: {
    currentTab: 0,
    
    // Forum Data
    messages: [],
    page: 1,
    hasMore: true,
    loading: false,
    
    // Chat Data
    conversations: [],
    unreadChatCount: 0,
    
    // Notification Data
    notifications: [],
    unreadNotifCount: 0,
    
    t: {},
    currentLang: 'zh',
    isRefreshing: false
  },
  
  onLoad() {
    this.setData({ currentLang: i18n.getLocale() });
    this.updateLocales();
    this.loadCurrentTabData();
    this.fetchUnreadCounts();
  },

  onShow() {
    this.updateLocales();
    i18n.updateTabBar(this);
    
    const lang = i18n.getLocale();
    if (lang !== this.data.currentLang) {
       this.setData({ currentLang: lang });
       // Reset forum data if lang changed
       if (this.data.currentTab === 0) {
           this.setData({ messages: [], page: 1, hasMore: true });
       }
    }
    
    this.loadCurrentTabData();
    this.fetchUnreadCounts();
  },

  updateLocales() {
      const lang = i18n.getLocale();
      this.setData({
          t: i18n.locales[lang]
      });
      wx.setNavigationBarTitle({ title: i18n.locales[lang]['tabbar_forum'] });
  },
  
  switchTab(e) {
    const idx = parseInt(e.currentTarget.dataset.idx);
    if (idx === this.data.currentTab) return;
    
    this.setData({ currentTab: idx });
    this.loadCurrentTabData();
  },
  
  loadCurrentTabData() {
      if (this.data.currentTab === 0) {
          if (this.data.messages.length === 0) this.fetchMessages(true);
      } else if (this.data.currentTab === 1) {
          this.fetchConversations();
      } else if (this.data.currentTab === 2) {
          this.fetchNotifications();
      }
  },

  onRefresherRefresh() {
    this.setData({ isRefreshing: true });
    if (this.data.currentTab === 0) this.fetchMessages(true);
    else if (this.data.currentTab === 1) this.fetchConversations();
    else if (this.data.currentTab === 2) this.fetchNotifications();
  },

  preventTouchMove() {},
  
  onReachBottom() {
    if (this.data.currentTab === 0) {
        this.fetchMessages(false);
    }
    // Implement pagination for others if needed
  },
  
  // --- Forum Methods ---
  
  fetchMessages(refresh) {
    if (this.data.loading || (!refresh && !this.data.hasMore)) return;
    
    this.setData({ loading: true });
    
    if (refresh) {
      this.setData({ page: 1, hasMore: true });
    }
    
    wx.request({
      url: `${app.globalData.baseUrl}/messages/`,
      method: 'GET',
      data: { page: this.data.page },
      success: (res) => {
        if (res.statusCode === 200) {
          const results = res.data.results || res.data;
          this.setData({
            messages: refresh ? results : [...this.data.messages, ...results],
            page: this.data.page + 1,
            hasMore: !!res.data.next,
            loading: false
          });
        } else {
          this.setData({ loading: false });
        }
      },
      fail: () => {
        this.setData({ loading: false });
      },
      complete: () => {
        this.setData({ isRefreshing: false });
        if (refresh) wx.stopPullDownRefresh();
      }
    });
  },
  
  // --- Chat Methods ---
  
  fetchConversations() {
      const token = wx.getStorageSync('access_token');
      if (!token) return;

      wx.request({
          url: `${app.globalData.baseUrl}/private-messages/conversations/`,
          method: 'GET',
          header: { 'Authorization': `Bearer ${token}` },
          success: (res) => {
              if (res.statusCode === 200) {
                  const convs = res.data.map(c => ({
                      ...c,
                      last_message_time_formatted: this.formatTime(c.last_message_time)
                  }));
                  this.setData({ conversations: convs });
              }
          },
          complete: () => {
             this.setData({ isRefreshing: false });
             wx.stopPullDownRefresh(); 
          }
      });
  },
  
  fetchUnreadCounts() {
      // Just sum up from local data or call a specific API if available
      // For now, conversations API returns unread_count per conv
      // We can also check notifications
      // Actually, let's rely on the fetch calls to update counts
      // But if we are in tab 0, we might want to know if tab 1 has unread
      // Ideally we need a separate 'stats' API or similar. 
      // For now, simply fetching conversations updates the chat count.
      
      const token = wx.getStorageSync('access_token');
      if (!token) return;
      
      // Fetch conversations to get unread chat count
      wx.request({
          url: `${app.globalData.baseUrl}/private-messages/conversations/`,
          method: 'GET',
          header: { 'Authorization': `Bearer ${token}` },
          success: (res) => {
              if (res.statusCode === 200) {
                  let count = 0;
                  res.data.forEach(c => count += c.unread_count);
                  this.setData({ unreadChatCount: count });
              }
          }
      });
      
      // Fetch notifications to get unread notif count
      wx.request({
          url: `${app.globalData.baseUrl}/notifications/`,
          method: 'GET',
          header: { 'Authorization': `Bearer ${token}` },
          success: (res) => {
              if (res.statusCode === 200) {
                  const results = res.data.results || res.data;
                  const count = results.filter(n => !n.is_read).length;
                  this.setData({ 
                      unreadNotifCount: count,
                      // Also update list if we are not in tab 2 (if we are, fetchNotifications handles it)
                      // But fetchNotifications is better for full list
                   });
              }
          }
      });
  },
  
  goToChat(e) {
      const userId = e.currentTarget.dataset.id;
      const username = e.currentTarget.dataset.name;
      wx.navigateTo({
          url: `/pages/messages/chat/chat?userId=${userId}&username=${username}`
      });
  },
  
  // --- Notification Methods ---
  
  fetchNotifications() {
      const token = wx.getStorageSync('access_token');
      if (!token) return;

      wx.request({
          url: `${app.globalData.baseUrl}/notifications/`,
          method: 'GET',
          header: { 'Authorization': `Bearer ${token}` },
          success: (res) => {
              if (res.statusCode === 200) {
                  const results = res.data.results || res.data;
                  const formatted = results.map(n => ({
                      ...n,
                      created_at_formatted: this.formatTime(n.created_at)
                  }));
                  this.setData({ notifications: formatted });
                  
                  // Update count
                  const count = formatted.filter(n => !n.is_read).length;
                  this.setData({ unreadNotifCount: count });
              }
          },
          complete: () => {
             this.setData({ isRefreshing: false });
             wx.stopPullDownRefresh(); 
          }
      });
  },
  
  markAllRead() {
      const token = wx.getStorageSync('access_token');
      if (!token) return;
      
      wx.request({
          url: `${app.globalData.baseUrl}/notifications/mark_all_read/`,
          method: 'POST',
          header: { 'Authorization': `Bearer ${token}` },
          success: (res) => {
              if (res.statusCode === 200) {
                  this.fetchNotifications();
                  wx.showToast({ title: '已全部标记为已读', icon: 'none' });
              }
          }
      });
  },
  
  handleNotification(e) {
      const item = e.currentTarget.dataset.item;
      const token = wx.getStorageSync('access_token');
      
      // Mark as read
      if (!item.is_read) {
          wx.request({
              url: `${app.globalData.baseUrl}/notifications/${item.id}/read/`,
              method: 'POST',
              header: { 'Authorization': `Bearer ${token}` }
          });
      }
      
      // Navigate
      if (item.target_url) {
          // If it's a tab page, use switchTab
          if (item.target_url.includes('/pages/messages/list/list')) {
             // Already here, maybe switch tab?
             // But usually target_url points to detail pages
          } else {
             wx.navigateTo({
                 url: item.target_url,
                 fail: (err) => {
                     // Try switchTab if navigateTo fails
                     wx.switchTab({ url: item.target_url });
                 }
             });
          }
      }
      
      // Refresh list to show read status
      this.fetchNotifications();
  },
  
  // --- Utils ---
  
  formatTime(isoString) {
      if (!isoString) return '';
      const date = new Date(isoString);
      const now = new Date();
      const diff = now - date;
      
      // If within 24 hours
      if (diff < 24 * 60 * 60 * 1000 && date.getDate() === now.getDate()) {
          const hours = date.getHours().toString().padStart(2, '0');
          const minutes = date.getMinutes().toString().padStart(2, '0');
          return `${hours}:${minutes}`;
      }
      
      // If yesterday
      const yesterday = new Date(now);
      yesterday.setDate(now.getDate() - 1);
      if (date.getDate() === yesterday.getDate() && date.getMonth() === yesterday.getMonth()) {
          return '昨天';
      }
      
      // Otherwise
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const day = date.getDate().toString().padStart(2, '0');
      return `${month}-${day}`;
  },

  goAdd() {
    wx.navigateTo({
      url: '/pages/messages/add/add'
    });
  },
  
  goToDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/messages/detail/detail?id=${id}`
    });
  },
  
  goToReply(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/messages/detail/detail?id=${id}&focus=true`
    });
  },

  goToProfile(e) {
    const userId = e.currentTarget.dataset.id;
    if (!userId) return;
    wx.navigateTo({
      url: `/pages/users/detail/detail?id=${userId}`
    });
  },

  goToChat(e) {
    const userId = e.currentTarget.dataset.id;
    const username = e.currentTarget.dataset.name;
    wx.navigateTo({
        url: `/pages/messages/chat/chat?targetUserId=${userId}&targetUsername=${username}`
    });
  }
})
