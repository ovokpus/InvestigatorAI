/**
 * Frontend logging utility for InvestigatorAI
 * Provides structured logging with different levels and optional remote logging
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  CRITICAL = 4
}

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: Record<string, unknown>;
  error?: Error;
  userId?: string;
  sessionId?: string;
  investigationId?: string;
  component?: string;
  action?: string;
}

export interface LoggerConfig {
  level: LogLevel;
  enableConsole: boolean;
  enableRemote: boolean;
  remoteEndpoint?: string;
  enableStorage: boolean;
  maxStorageEntries: number;
  enablePerformanceLogging: boolean;
}

class Logger {
  private config: LoggerConfig;
  private sessionId: string;
  private logBuffer: LogEntry[] = [];

  constructor(config: Partial<LoggerConfig> = {}) {
    this.config = {
      level: LogLevel.INFO,
      enableConsole: true,
      enableRemote: false,
      enableStorage: true,
      maxStorageEntries: 1000,
      enablePerformanceLogging: true,
      ...config
    };

    // Generate session ID
    this.sessionId = this.generateSessionId();
    
    // Initialize storage cleanup
    if (this.config.enableStorage) {
      this.cleanupOldLogs();
    }

    // Setup error handlers
    this.setupGlobalErrorHandlers();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private shouldLog(level: LogLevel): boolean {
    return level >= this.config.level;
  }

  private formatMessage(level: LogLevel, message: string, context?: Record<string, unknown>): string {
    const timestamp = new Date().toISOString();
    const levelName = LogLevel[level];
    const contextStr = context ? ` | ${JSON.stringify(context)}` : '';
    return `[${timestamp}] ${levelName}: ${message}${contextStr}`;
  }

  private createLogEntry(
    level: LogLevel,
    message: string,
    context?: Record<string, unknown>,
    error?: Error
  ): LogEntry {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      error,
      sessionId: this.sessionId,
      component: context?.component as string | undefined,
      action: context?.action as string | undefined,
      userId: context?.userId as string | undefined,
      investigationId: context?.investigationId as string | undefined
    };
  }

  private logToConsole(entry: LogEntry): void {
    if (!this.config.enableConsole) return;

    const formattedMessage = this.formatMessage(entry.level, entry.message, entry.context);
    
    switch (entry.level) {
      case LogLevel.DEBUG:
        console.debug(formattedMessage, entry.error);
        break;
      case LogLevel.INFO:
        console.info(formattedMessage);
        break;
      case LogLevel.WARN:
        console.warn(formattedMessage);
        break;
      case LogLevel.ERROR:
      case LogLevel.CRITICAL:
        console.error(formattedMessage, entry.error);
        break;
    }
  }

  private async logToRemote(entry: LogEntry): Promise<void> {
    if (!this.config.enableRemote || !this.config.remoteEndpoint) return;

    try {
      await fetch(this.config.remoteEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(entry)
      });
    } catch (error) {
      // Fallback to console if remote logging fails
      console.error('Failed to send log to remote endpoint:', error);
    }
  }

  private logToStorage(entry: LogEntry): void {
    if (!this.config.enableStorage || typeof window === 'undefined') return;

    try {
      this.logBuffer.push(entry);
      
      // Keep buffer size manageable
      if (this.logBuffer.length > this.config.maxStorageEntries) {
        this.logBuffer = this.logBuffer.slice(-this.config.maxStorageEntries);
      }

      // Store in localStorage
      localStorage.setItem('investigator_ai_logs', JSON.stringify(this.logBuffer));
    } catch (error) {
      console.warn('Failed to store log entry:', error);
    }
  }

  private cleanupOldLogs(): void {
    if (typeof window === 'undefined') return; // Skip on server-side
    
    try {
      const stored = localStorage.getItem('investigator_ai_logs');
      if (stored) {
        const logs: LogEntry[] = JSON.parse(stored);
        const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000;
        
        this.logBuffer = logs.filter(log => 
          new Date(log.timestamp).getTime() > oneDayAgo
        );
        
        localStorage.setItem('investigator_ai_logs', JSON.stringify(this.logBuffer));
      }
    } catch (error) {
      console.warn('Failed to cleanup old logs:', error);
    }
  }

  private setupGlobalErrorHandlers(): void {
    if (typeof window === 'undefined') return; // Skip on server-side
    
    // Capture unhandled errors
    window.addEventListener('error', (event) => {
      this.error('Unhandled error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        component: 'global'
      }, event.error);
    });

    // Capture unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.error('Unhandled promise rejection', {
        reason: event.reason,
        component: 'global'
      });
    });
  }

  private log(level: LogLevel, message: string, context?: Record<string, unknown>, error?: Error): void {
    if (!this.shouldLog(level)) return;

    const entry = this.createLogEntry(level, message, context, error);

    // Log to different outputs
    this.logToConsole(entry);
    this.logToStorage(entry);
    
    // Async remote logging
    if (this.config.enableRemote) {
      this.logToRemote(entry).catch(() => {
        // Silent fail for remote logging
      });
    }
  }

  // Public logging methods
  debug(message: string, context?: Record<string, unknown>): void {
    this.log(LogLevel.DEBUG, message, context);
  }

  info(message: string, context?: Record<string, unknown>): void {
    this.log(LogLevel.INFO, message, context);
  }

  warn(message: string, context?: Record<string, unknown>): void {
    this.log(LogLevel.WARN, message, context);
  }

  error(message: string, context?: Record<string, unknown>, error?: Error): void {
    this.log(LogLevel.ERROR, message, context, error);
  }

  critical(message: string, context?: Record<string, unknown>, error?: Error): void {
    this.log(LogLevel.CRITICAL, message, context, error);
  }

  // Specialized logging methods
  logInvestigationEvent(event: string, investigationId: string, context?: Record<string, unknown>): void {
    this.info(`Investigation Event: ${event}`, {
      ...context,
      investigationId,
      component: 'investigation',
      action: event
    });
  }

  logUserAction(action: string, context?: Record<string, unknown>): void {
    this.info(`User Action: ${action}`, {
      ...context,
      component: 'user-interaction',
      action
    });
  }

  logApiCall(method: string, url: string, status: number, duration: number, context?: Record<string, unknown>): void {
    const level = status >= 400 ? LogLevel.ERROR : LogLevel.INFO;
    this.log(level, `API Call: ${method} ${url} - ${status} (${duration}ms)`, {
      ...context,
      component: 'api',
      method,
      url,
      status,
      duration
    });
  }

  logPerformance(operation: string, duration: number, context?: Record<string, unknown>): void {
    if (!this.config.enablePerformanceLogging) return;
    
    this.info(`Performance: ${operation} completed in ${duration}ms`, {
      ...context,
      component: 'performance',
      operation,
      duration
    });
  }

  // Utility methods
  getLogs(): LogEntry[] {
    return [...this.logBuffer];
  }

  clearLogs(): void {
    this.logBuffer = [];
    if (this.config.enableStorage && typeof window !== 'undefined') {
      localStorage.removeItem('investigator_ai_logs');
    }
  }

  exportLogs(): string {
    return JSON.stringify(this.logBuffer, null, 2);
  }

  setLevel(level: LogLevel): void {
    this.config.level = level;
  }

  setUserId(userId: string): void {
    // Add userId to all future logs
    this.info('User session started', { userId, component: 'auth' });
  }
}

// Create default logger instance
const defaultConfig: Partial<LoggerConfig> = {
  level: process.env.NODE_ENV === 'development' ? LogLevel.DEBUG : LogLevel.INFO,
  enableConsole: true,
  enableRemote: process.env.NODE_ENV === 'production',
  remoteEndpoint: process.env.NEXT_PUBLIC_LOG_ENDPOINT,
  enableStorage: true,
  maxStorageEntries: 1000,
  enablePerformanceLogging: true
};

export const logger = new Logger(defaultConfig);

// Export Logger class for custom instances
export { Logger };

// Convenience functions
export const logDebug = (message: string, context?: Record<string, unknown>) => logger.debug(message, context);
export const logInfo = (message: string, context?: Record<string, unknown>) => logger.info(message, context);
export const logWarn = (message: string, context?: Record<string, unknown>) => logger.warn(message, context);
export const logError = (message: string, context?: Record<string, unknown>, error?: Error) => logger.error(message, context, error);
export const logCritical = (message: string, context?: Record<string, unknown>, error?: Error) => logger.critical(message, context, error);

// Performance logging helper
export const measurePerformance = <T>(operation: string, fn: () => T, context?: Record<string, unknown>): T => {
  const start = performance.now();
  try {
    const result = fn();
    const duration = performance.now() - start;
    logger.logPerformance(operation, duration, context);
    return result;
  } catch (error) {
    const duration = performance.now() - start;
    logger.error(`Performance: ${operation} failed after ${duration}ms`, context, error as Error);
    throw error;
  }
};

// Async performance logging helper
export const measurePerformanceAsync = async <T>(
  operation: string, 
  fn: () => Promise<T>, 
  context?: Record<string, unknown>
): Promise<T> => {
  const start = performance.now();
  try {
    const result = await fn();
    const duration = performance.now() - start;
    logger.logPerformance(operation, duration, context);
    return result;
  } catch (error) {
    const duration = performance.now() - start;
    logger.error(`Performance: ${operation} failed after ${duration}ms`, context, error as Error);
    throw error;
  }
};
