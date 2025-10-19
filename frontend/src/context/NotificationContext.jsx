import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const NotificationContext = createContext();

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

export const NotificationProvider = ({ children }) => {
  const { currentUser } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  // Load notifications from localStorage on mount
  useEffect(() => {
    if (currentUser?.email) {
      loadNotifications();
    }
  }, [currentUser?.email]);

  // Update unread count whenever notifications change
  useEffect(() => {
    const count = notifications.filter(n => !n.read).length;
    setUnreadCount(count);
  }, [notifications]);

  const loadNotifications = () => {
    const storageKey = `notifications_${currentUser.email}`;
    const stored = localStorage.getItem(storageKey);
    
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setNotifications(parsed);
      } catch (e) {
        console.error('Error loading notifications:', e);
      }
    }
  };

  const saveNotifications = (newNotifications) => {
    const storageKey = `notifications_${currentUser.email}`;
    localStorage.setItem(storageKey, JSON.stringify(newNotifications));
    setNotifications(newNotifications);
  };

  // Add a new notification
  const addNotification = (notification) => {
    const newNotification = {
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      read: false,
      ...notification
    };

    const updated = [newNotification, ...notifications].slice(0, 50); // Keep max 50
    saveNotifications(updated);

    // Show browser notification if permitted
    if (notification.showBrowser && 'Notification' in window && Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/logo.png', // Add your logo path
        badge: '/logo.png'
      });
    }
  };

  // Mark notification as read
  const markAsRead = (notificationId) => {
    const updated = notifications.map(n =>
      n.id === notificationId ? { ...n, read: true } : n
    );
    saveNotifications(updated);
  };

  // Mark all as read
  const markAllAsRead = () => {
    const updated = notifications.map(n => ({ ...n, read: true }));
    saveNotifications(updated);
  };

  // Delete notification
  const deleteNotification = (notificationId) => {
    const updated = notifications.filter(n => n.id !== notificationId);
    saveNotifications(updated);
  };

  // Clear all notifications
  const clearAll = () => {
    saveNotifications([]);
  };

  // Request browser notification permission
  const requestPermission = async () => {
    if ('Notification' in window && Notification.permission === 'default') {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }
    return Notification.permission === 'granted';
  };

  // Smart notification triggers based on app events
  const triggerNotification = (type, data) => {
    const notificationTemplates = {
      // Portfolio notifications
      PORTFOLIO_UP: {
        type: 'success',
        title: 'Portfolio Gain! 📈',
        message: `Your portfolio is up ${data.percentage}% today (+${data.amount})`,
        category: 'portfolio',
        showBrowser: true
      },
      PORTFOLIO_DOWN: {
        type: 'warning',
        title: 'Portfolio Alert 📉',
        message: `Your portfolio is down ${data.percentage}% today (${data.amount})`,
        category: 'portfolio',
        showBrowser: true
      },
      
      // Risk notifications
      RISK_MISMATCH: {
        type: 'error',
        title: 'Risk Profile Mismatch ⚠️',
        message: 'Your portfolio risk doesn\'t match your stated tolerance. Review recommended.',
        category: 'risk',
        actionUrl: '/risk',
        showBrowser: true
      },
      HIGH_RISK: {
        type: 'warning',
        title: 'High Risk Detected',
        message: `Your risk score is ${data.score}/10. Consider rebalancing for stability.`,
        category: 'risk',
        actionUrl: '/risk'
      },
      
      // Recommendation notifications
      NEW_RECOMMENDATIONS: {
        type: 'info',
        title: 'New Recommendations Available',
        message: `${data.count} new actions recommended for your portfolio`,
        category: 'recommendations',
        actionUrl: '/recommendations'
      },
      URGENT_ACTION: {
        type: 'error',
        title: 'Urgent Action Required! 🚨',
        message: data.message,
        category: 'recommendations',
        actionUrl: '/recommendations',
        showBrowser: true
      },
      
      // Market notifications
      BIG_MOVE: {
        type: 'info',
        title: 'Big Market Move',
        message: `${data.symbol} ${data.change > 0 ? 'up' : 'down'} ${Math.abs(data.change)}%`,
        category: 'market',
        actionUrl: '/market'
      },
      
      // System notifications
      CACHE_CLEARED: {
        type: 'info',
        title: 'Cache Cleared',
        message: 'Your data has been refreshed with the latest information',
        category: 'system'
      },
      DATA_SYNCED: {
        type: 'success',
        title: 'Data Synced ✓',
        message: 'Your portfolio data is up to date',
        category: 'system'
      }
    };

    const template = notificationTemplates[type];
    if (template) {
      addNotification(template);
    }
  };

  // Auto-check for important events
  useEffect(() => {
    if (!currentUser?.email) return;

    const checkInterval = setInterval(() => {
      checkForImportantEvents();
    }, 5 * 60 * 1000); // Check every 5 minutes

    return () => clearInterval(checkInterval);
  }, [currentUser, notifications]);

  const checkForImportantEvents = async () => {
    try {
      // Check if we should notify about cache expiry
      const keys = ['recommendations', 'risk_analysis', 'market_trends'];
      
      keys.forEach(key => {
        const cacheKey = `${key}_${currentUser.email}`;
        const cached = localStorage.getItem(cacheKey);
        
        if (cached) {
          const { timestamp } = JSON.parse(cached);
          const age = Date.now() - timestamp;
          const cacheDurations = {
            recommendations: 5 * 60 * 1000,
            risk_analysis: 10 * 60 * 1000,
            market_trends: 2 * 60 * 1000
          };
          
          // Notify if cache is about to expire (within 1 minute)
          if (age > cacheDurations[key] - 60000 && age < cacheDurations[key]) {
            const lastNotified = localStorage.getItem(`notified_${cacheKey}`);
            if (!lastNotified || Date.now() - parseInt(lastNotified) > cacheDurations[key]) {
              addNotification({
                type: 'info',
                title: 'Data Refresh Recommended',
                message: `Your ${key.replace('_', ' ')} data will refresh soon`,
                category: 'system'
              });
              localStorage.setItem(`notified_${cacheKey}`, Date.now().toString());
            }
          }
        }
      });
    } catch (e) {
      console.error('Error checking events:', e);
    }
  };

  const value = {
    notifications,
    unreadCount,
    addNotification,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearAll,
    requestPermission,
    triggerNotification
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};