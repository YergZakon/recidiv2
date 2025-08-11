import { Notification } from '../components/notifications/NotificationCenter';

class NotificationService {
  private static instance: NotificationService;
  private listeners: ((notifications: Notification[]) => void)[] = [];
  private notifications: Notification[] = [];

  static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  private constructor() {
    this.initializeNotifications();
  }

  private initializeNotifications() {
    // Initialize with some mock notifications
    this.notifications = [
      {
        id: 'init_001',
        type: 'info',
        title: 'Система инициализирована',
        message: 'Система раннего предупреждения преступлений запущена успешно.',
        timestamp: new Date().toISOString(),
        read: true,
        actionRequired: false
      }
    ];
  }

  // Subscribe to notification updates
  subscribe(callback: (notifications: Notification[]) => void): () => void {
    this.listeners.push(callback);
    // Immediately call with current notifications
    callback(this.notifications);
    
    // Return unsubscribe function
    return () => {
      this.listeners = this.listeners.filter(listener => listener !== callback);
    };
  }

  // Notify all listeners
  private notifyListeners() {
    this.listeners.forEach(listener => listener([...this.notifications]));
  }

  // Add a new notification
  addNotification(notification: Omit<Notification, 'id' | 'timestamp' | 'read'>): string {
    const id = `notify_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newNotification: Notification = {
      ...notification,
      id,
      timestamp: new Date().toISOString(),
      read: false
    };

    this.notifications.unshift(newNotification); // Add to beginning
    this.notifyListeners();

    // Auto-remove non-critical notifications after 24 hours
    if (notification.type !== 'critical') {
      setTimeout(() => {
        this.removeNotification(id);
      }, 24 * 60 * 60 * 1000);
    }

    return id;
  }

  // Create critical risk notification
  createCriticalRiskNotification(iin: string, riskScore: number, region?: string): string {
    return this.addNotification({
      type: 'critical',
      title: 'Критический риск обнаружен',
      message: `Лицо с ИИН ${iin} имеет критический уровень риска (${riskScore.toFixed(1)} балла). Требует немедленного вмешательства.`,
      actionRequired: true,
      relatedPersonIIN: iin,
      region
    });
  }

  // Create high risk notification
  createHighRiskNotification(iin: string, riskScore: number, region?: string): string {
    return this.addNotification({
      type: 'warning',
      title: 'Высокий риск',
      message: `Лицо с ИИН ${iin} имеет высокий уровень риска (${riskScore.toFixed(1)} балла). Рекомендуется усиленный контроль.`,
      actionRequired: true,
      relatedPersonIIN: iin,
      region
    });
  }

  // Create escalation warning
  createEscalationWarning(iin: string, region?: string): string {
    return this.addNotification({
      type: 'warning',
      title: 'Предупреждение об эскалации',
      message: `Лицо с ИИН ${iin} показывает признаки эскалации преступного поведения.`,
      actionRequired: true,
      relatedPersonIIN: iin,
      region
    });
  }

  // Create prevention success notification
  createPreventionSuccessNotification(iin: string, region?: string): string {
    return this.addNotification({
      type: 'success',
      title: 'Успешное предотвращение',
      message: `Благодаря раннему вмешательству удалось предотвратить потенциальное преступление (ИИН: ${iin}).`,
      actionRequired: false,
      relatedPersonIIN: iin,
      region
    });
  }

  // Create regional alert
  createRegionalAlert(region: string, criticalCount: number): string {
    return this.addNotification({
      type: 'critical',
      title: `Превышение порога: ${region}`,
      message: `Количество лиц критического риска в регионе "${region}" превысило пороговое значение (${criticalCount} лиц).`,
      actionRequired: true,
      region
    });
  }

  // Mark notification as read
  markAsRead(id: string): void {
    const notification = this.notifications.find(n => n.id === id);
    if (notification && !notification.read) {
      notification.read = true;
      this.notifyListeners();
    }
  }

  // Mark all notifications as read
  markAllAsRead(): void {
    let changed = false;
    this.notifications.forEach(notification => {
      if (!notification.read) {
        notification.read = true;
        changed = true;
      }
    });
    if (changed) {
      this.notifyListeners();
    }
  }

  // Remove notification
  removeNotification(id: string): void {
    const index = this.notifications.findIndex(n => n.id === id);
    if (index !== -1) {
      this.notifications.splice(index, 1);
      this.notifyListeners();
    }
  }

  // Get all notifications
  getNotifications(): Notification[] {
    return [...this.notifications];
  }

  // Get unread count
  getUnreadCount(): number {
    return this.notifications.filter(n => !n.read).length;
  }

  // Get critical count
  getCriticalCount(): number {
    return this.notifications.filter(n => n.type === 'critical' && !n.read).length;
  }

  // Process risk calculation result and create appropriate notifications
  processRiskCalculation(
    iin: string, 
    riskScore: number, 
    riskLevel: string, 
    region?: string,
    hasEscalation?: boolean
  ): void {
    // Create notification based on risk level
    if (riskScore >= 7.0 || riskLevel.includes('Критический')) {
      this.createCriticalRiskNotification(iin, riskScore, region);
    } else if (riskScore >= 5.0 || riskLevel.includes('Высокий')) {
      this.createHighRiskNotification(iin, riskScore, region);
    }

    // Create escalation warning if applicable
    if (hasEscalation) {
      this.createEscalationWarning(iin, region);
    }
  }

  // Simulate real-time notifications (for demo purposes)
  startDemo(): void {
    const demoNotifications = [
      () => this.createCriticalRiskNotification('111111111111', 8.7, 'г. Алматы'),
      () => this.createHighRiskNotification('222222222222', 6.2, 'г. Астана'),
      () => this.createEscalationWarning('333333333333', 'Алматинская область'),
      () => this.createRegionalAlert('г. Алматы', 52),
      () => this.createPreventionSuccessNotification('444444444444', 'г. Шымкент')
    ];

    // Add demo notifications with random intervals
    demoNotifications.forEach((createNotification, index) => {
      setTimeout(() => {
        createNotification();
      }, (index + 1) * 30000); // Every 30 seconds
    });
  }
}

export default NotificationService;