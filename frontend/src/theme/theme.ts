export const theme = {
  colors: {
    light: {
      background: '#f8fafc',
      surface: '#ffffff',
      surfaceHighlight: '#f1f5f9',
      textPrimary: '#0f172a',
      textSecondary: '#64748b',
      border: '#e2e8f0',
      primary: '#3b82f6',
      primaryHover: '#2563eb',
      success: '#10b981',
      warning: '#f59e0b',
      danger: '#ef4444',
      accent: '#00ffc8',
      glass: 'rgba(255, 255, 255, 0.7)',
      glassBorder: 'rgba(0, 0, 0, 0.05)',
    },
    dark: {
      background: '#050814',
      surface: '#0f172a',
      surfaceHighlight: '#1e293b',
      textPrimary: '#f8fafc',
      textSecondary: '#94a3b8',
      border: '#1e293b',
      primary: '#3b82f6',
      primaryHover: '#60a5fa',
      success: '#10b981',
      warning: '#fbbf24',
      danger: '#f87171',
      accent: '#00ffc8',
      glass: 'rgba(15, 23, 42, 0.6)',
      glassBorder: 'rgba(255, 255, 255, 0.1)',
    }
  }
};

export type ThemeMode = 'light' | 'dark';
