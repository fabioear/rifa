import React, { createContext, useEffect, useState, ReactNode } from 'react';
import { theme, ThemeMode } from './theme';

interface ThemeContextType {
  mode: ThemeMode;
  toggleTheme: () => void;
  setTheme: (mode: ThemeMode) => void;
}

export const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [mode, setMode] = useState<ThemeMode>(() => {
    // Check localStorage first
    const saved = localStorage.getItem('theme_preference');
    if (saved === 'dark' || saved === 'light') return saved;
    
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'dark'; // Default to dark for "High-end SaaS" feel
  });

  useEffect(() => {
    const root = window.document.documentElement;
    
    // Remove old class
    root.classList.remove('light', 'dark');
    // Add new class
    root.classList.add(mode);
    
    // Set data-theme attribute
    root.setAttribute('data-theme', mode);
    
    // Update CSS variables
    const colors = theme.colors[mode];
    Object.entries(colors).forEach(([key, value]) => {
      // Convert camelCase to kebab-case for CSS variables
      const cssVar = `--color-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`;
      root.style.setProperty(cssVar, value);
    });

    // Save to localStorage
    localStorage.setItem('theme_preference', mode);
  }, [mode]);

  const toggleTheme = () => {
    setMode((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const setTheme = (newMode: ThemeMode) => {
    setMode(newMode);
  };

  return (
    <ThemeContext.Provider value={{ mode, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
