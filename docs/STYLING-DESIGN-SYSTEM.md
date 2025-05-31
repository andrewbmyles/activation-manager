# Styling and Design System Guide

## Table of Contents
1. [Design System Overview](#design-system-overview)
2. [Tailwind CSS Configuration](#tailwind-css-configuration)
3. [Color System](#color-system)
4. [Typography](#typography)
5. [Spacing and Layout](#spacing-and-layout)
6. [Component Styling Patterns](#component-styling-patterns)
7. [Responsive Design](#responsive-design)
8. [Accessibility Guidelines](#accessibility-guidelines)
9. [CSS Architecture](#css-architecture)
10. [Custom Utilities](#custom-utilities)

## Design System Overview

The Activation Manager uses a custom design system built on top of Tailwind CSS, providing consistent visual language and user experience across all components.

### Design Principles
- **Consistency**: Unified visual language across all components
- **Accessibility**: WCAG 2.1 AA compliance
- **Responsive**: Mobile-first design approach
- **Performance**: Optimized CSS bundle size
- **Maintainability**: Systematic approach to styling

### Visual Hierarchy
```
Primary Brand Color: Blue (#2563eb)
Secondary Colors: Green, Purple, Orange, Red
Neutral Grays: 50-900 scale
Surface Colors: White, Gray-50, Gray-100
```

## Tailwind CSS Configuration

### tailwind.config.js
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary brand colors
        primary: {
          DEFAULT: '#2563eb',
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          hover: '#1d4ed8',
        },
        // Secondary colors for different states and categories
        secondary: {
          green: '#10b981',
          purple: '#8b5cf6',
          orange: '#f59e0b',
          red: '#ef4444',
        },
        // Extended gray scale
        gray: {
          25: '#fcfcfd',
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        },
      },
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          'sans-serif',
        ],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'DEFAULT': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
      },
      borderRadius: {
        'sm': '0.125rem',
        'DEFAULT': '0.25rem',
        'md': '0.375rem',
        'lg': '0.5rem',
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-in-out',
        'slide-down': 'slideDown 0.2s ease-out',
        'slide-up': 'slideUp 0.2s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### PostCSS Configuration
```javascript
// postcss.config.js
module.exports = {
  plugins: [
    require('tailwindcss'),
    require('autoprefixer'),
  ],
}
```

## Color System

### Primary Color Palette
```css
/* Primary Blue */
.text-primary { color: #2563eb; }
.bg-primary { background-color: #2563eb; }
.border-primary { border-color: #2563eb; }

/* Primary variants */
.bg-primary/10 { background-color: rgba(37, 99, 235, 0.1); }
.bg-primary/20 { background-color: rgba(37, 99, 235, 0.2); }
.text-primary-hover { color: #1d4ed8; }
```

### Secondary Color Palette
```css
/* Success Green */
.text-secondary-green { color: #10b981; }
.bg-secondary-green { background-color: #10b981; }

/* Warning Orange */
.text-secondary-orange { color: #f59e0b; }
.bg-secondary-orange { background-color: #f59e0b; }

/* Error Red */
.text-secondary-red { color: #ef4444; }
.bg-secondary-red { background-color: #ef4444; }

/* Info Purple */
.text-secondary-purple { color: #8b5cf6; }
.bg-secondary-purple { background-color: #8b5cf6; }
```

### Usage Guidelines
```typescript
// Color usage examples
const colorVariants = {
  primary: 'bg-primary text-white hover:bg-primary-hover',
  secondary: 'bg-gray-100 text-gray-800 hover:bg-gray-200',
  success: 'bg-secondary-green text-white',
  warning: 'bg-secondary-orange text-white',
  error: 'bg-secondary-red text-white',
  info: 'bg-secondary-purple text-white',
};

// Status colors
const statusColors = {
  connected: 'text-secondary-green bg-green-50',
  disconnected: 'text-secondary-red bg-red-50',
  pending: 'text-secondary-orange bg-orange-50',
  inactive: 'text-gray-500 bg-gray-50',
};
```

## Typography

### Font System
```css
/* Font family */
.font-sans {
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Font weights */
.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }

/* Font sizes with line heights */
.text-xs { font-size: 0.75rem; line-height: 1rem; }
.text-sm { font-size: 0.875rem; line-height: 1.25rem; }
.text-base { font-size: 1rem; line-height: 1.5rem; }
.text-lg { font-size: 1.125rem; line-height: 1.75rem; }
.text-xl { font-size: 1.25rem; line-height: 1.75rem; }
.text-2xl { font-size: 1.5rem; line-height: 2rem; }
.text-3xl { font-size: 1.875rem; line-height: 2.25rem; }
```

### Typography Scale
```typescript
// Typography usage patterns
const textStyles = {
  // Page titles
  h1: 'text-3xl font-semibold text-gray-800',
  h2: 'text-2xl font-semibold text-gray-800',
  h3: 'text-xl font-semibold text-gray-800',
  
  // Body text
  body: 'text-base text-gray-700',
  bodySmall: 'text-sm text-gray-600',
  caption: 'text-xs text-gray-500',
  
  // Interactive elements
  link: 'text-primary hover:text-primary-hover underline',
  button: 'text-sm font-medium',
  
  // Status and labels
  label: 'text-sm font-medium text-gray-700',
  help: 'text-xs text-gray-500',
  error: 'text-sm text-secondary-red',
  success: 'text-sm text-secondary-green',
};
```

## Spacing and Layout

### Spacing Scale
```css
/* Padding and margin scale */
.p-0 { padding: 0; }
.p-1 { padding: 0.25rem; }
.p-2 { padding: 0.5rem; }
.p-3 { padding: 0.75rem; }
.p-4 { padding: 1rem; }
.p-6 { padding: 1.5rem; }
.p-8 { padding: 2rem; }

/* Component-specific spacing */
.space-y-2 > * + * { margin-top: 0.5rem; }
.space-y-4 > * + * { margin-top: 1rem; }
.space-y-6 > * + * { margin-top: 1.5rem; }

/* Grid gaps */
.gap-2 { gap: 0.5rem; }
.gap-3 { gap: 0.75rem; }
.gap-4 { gap: 1rem; }
.gap-6 { gap: 1.5rem; }
```

### Layout Patterns
```css
/* Container patterns */
.container {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* Card layout */
.card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
}

/* Grid layouts */
.grid-auto-fit {
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.grid-responsive {
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .grid-responsive {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .grid-responsive {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

## Component Styling Patterns

### Button Components
```css
/* Base button styles */
.btn-base {
  @apply inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-primary {
  @apply btn-base bg-primary text-white hover:bg-primary-hover focus:ring-primary;
}

.btn-secondary {
  @apply btn-base bg-gray-100 text-gray-800 hover:bg-gray-200 focus:ring-gray-500;
}

.btn-outline {
  @apply btn-base border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-primary;
}

/* Button sizes */
.btn-sm {
  @apply px-3 py-1.5 text-xs;
}

.btn-lg {
  @apply px-6 py-3 text-base;
}
```

### Form Components
```css
/* Input field base */
.input-field {
  @apply block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors;
}

.input-error {
  @apply border-secondary-red focus:border-secondary-red focus:ring-secondary-red/20;
}

/* Select dropdown */
.select-field {
  @apply input-field pr-10 bg-white;
}

/* Textarea */
.textarea-field {
  @apply input-field resize-vertical min-h-[80px];
}

/* Checkbox and radio */
.checkbox-field {
  @apply h-4 w-4 text-primary border-gray-300 rounded focus:ring-primary/20;
}

.radio-field {
  @apply h-4 w-4 text-primary border-gray-300 focus:ring-primary/20;
}
```

### Card Components
```css
/* Base card */
.card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 p-6;
}

.card-hover {
  @apply card hover:shadow-md transition-shadow cursor-pointer;
}

/* Card variants */
.card-outlined {
  @apply bg-white rounded-lg border-2 border-gray-200 p-6;
}

.card-elevated {
  @apply bg-white rounded-lg shadow-lg border border-gray-100 p-6;
}

/* Card sections */
.card-header {
  @apply mb-4 pb-4 border-b border-gray-200;
}

.card-footer {
  @apply mt-6 pt-4 border-t border-gray-200;
}
```

### Navigation Components
```css
/* Sidebar navigation */
.nav-link {
  @apply flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors;
}

.nav-link-active {
  @apply nav-link bg-primary/10 text-primary border border-primary/20;
}

.nav-link-inactive {
  @apply nav-link text-gray-600 hover:bg-gray-50 hover:text-gray-900;
}

/* Breadcrumb navigation */
.breadcrumb {
  @apply flex items-center space-x-2 text-sm text-gray-500;
}

.breadcrumb-separator {
  @apply text-gray-300;
}

.breadcrumb-current {
  @apply text-gray-900 font-medium;
}
```

### Table Components
```css
/* Table base */
.table {
  @apply min-w-full divide-y divide-gray-200;
}

.table-header {
  @apply bg-gray-50;
}

.table-header-cell {
  @apply px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider;
}

.table-body {
  @apply bg-white divide-y divide-gray-200;
}

.table-row {
  @apply hover:bg-gray-50 transition-colors;
}

.table-cell {
  @apply px-6 py-4 whitespace-nowrap text-sm text-gray-900;
}

/* Table variants */
.table-compact .table-cell {
  @apply py-2;
}

.table-striped .table-row:nth-child(even) {
  @apply bg-gray-25;
}
```

## Responsive Design

### Breakpoint System
```css
/* Tailwind breakpoints */
/* sm: 640px */
/* md: 768px */
/* lg: 1024px */
/* xl: 1280px */
/* 2xl: 1536px */

/* Mobile-first responsive patterns */
.responsive-grid {
  @apply grid grid-cols-1 gap-4;
  @apply md:grid-cols-2;
  @apply lg:grid-cols-3;
  @apply xl:grid-cols-4;
}

.responsive-text {
  @apply text-sm;
  @apply md:text-base;
  @apply lg:text-lg;
}

.responsive-padding {
  @apply p-4;
  @apply md:p-6;
  @apply lg:p-8;
}
```

### Layout Patterns
```css
/* Sidebar layout */
.layout-sidebar {
  @apply min-h-screen bg-gray-50;
}

.layout-sidebar-nav {
  @apply fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out;
  @apply -translate-x-full lg:translate-x-0 lg:static lg:inset-0;
}

.layout-sidebar-main {
  @apply lg:pl-64;
}

/* Responsive containers */
.container-responsive {
  @apply w-full max-w-7xl mx-auto px-4;
  @apply sm:px-6;
  @apply lg:px-8;
}
```

## Accessibility Guidelines

### Focus States
```css
/* Focus ring styles */
.focus-ring {
  @apply focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary;
}

.focus-ring-error {
  @apply focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-secondary-red;
}

/* Skip link for screen readers */
.skip-link {
  @apply absolute -top-10 left-6 z-50 px-4 py-2 bg-primary text-white rounded-md focus:top-6 transition-all;
}
```

### Color Contrast
```css
/* High contrast text combinations */
.text-high-contrast {
  @apply text-gray-900; /* 21:1 ratio on white */
}

.text-medium-contrast {
  @apply text-gray-700; /* 10.8:1 ratio on white */
}

.text-subtle {
  @apply text-gray-600; /* 7.2:1 ratio on white */
}

/* Status colors with sufficient contrast */
.status-success {
  @apply text-green-800 bg-green-100; /* 7.1:1 ratio */
}

.status-warning {
  @apply text-amber-800 bg-amber-100; /* 7.5:1 ratio */
}

.status-error {
  @apply text-red-800 bg-red-100; /* 7.9:1 ratio */
}
```

### Screen Reader Support
```css
/* Screen reader only content */
.sr-only {
  @apply absolute w-px h-px p-0 -m-px overflow-hidden whitespace-nowrap border-0;
  clip: rect(0, 0, 0, 0);
}

/* Not screen reader only (for toggling) */
.not-sr-only {
  @apply static w-auto h-auto p-0 m-0 overflow-visible whitespace-normal;
  clip: auto;
}
```

## CSS Architecture

### File Organization
```
src/
├── index.css              # Main CSS file with Tailwind imports
├── components/
│   ├── buttons.css        # Button component styles
│   ├── forms.css          # Form component styles
│   ├── cards.css          # Card component styles
│   └── navigation.css     # Navigation component styles
└── utilities/
    ├── animations.css     # Custom animations
    ├── layout.css         # Layout utilities
    └── typography.css     # Typography utilities
```

### Main CSS File
```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom base styles */
@layer base {
  html {
    @apply text-base;
  }
  
  body {
    @apply font-sans text-gray-900 bg-gray-50 antialiased;
  }
  
  * {
    @apply border-gray-200;
  }
}

/* Custom component styles */
@layer components {
  .btn {
    @apply inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed;
  }
  
  .input-field {
    @apply block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors;
  }
  
  .card {
    @apply bg-white rounded-lg shadow-sm border border-gray-200 p-6;
  }
}

/* Custom utilities */
@layer utilities {
  .text-shadow {
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .scrollbar-thin {
    scrollbar-width: thin;
    scrollbar-color: #cbd5e1 #f1f5f9;
  }
  
  .scrollbar-thin::-webkit-scrollbar {
    width: 6px;
  }
  
  .scrollbar-thin::-webkit-scrollbar-track {
    background: #f1f5f9;
  }
  
  .scrollbar-thin::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 3px;
  }
}
```

## Custom Utilities

### Animation Utilities
```css
/* Loading states */
.skeleton {
  @apply animate-pulse bg-gray-200 rounded;
}

.skeleton-text {
  @apply skeleton h-4 w-full;
}

.skeleton-circle {
  @apply skeleton rounded-full;
}

/* Fade animations */
.fade-in {
  @apply animate-fade-in;
}

.slide-down {
  @apply animate-slide-down;
}

/* Hover effects */
.hover-lift {
  @apply transition-transform hover:-translate-y-1;
}

.hover-scale {
  @apply transition-transform hover:scale-105;
}
```

### Layout Utilities
```css
/* Flexbox utilities */
.flex-center {
  @apply flex items-center justify-center;
}

.flex-between {
  @apply flex items-center justify-between;
}

.flex-start {
  @apply flex items-center justify-start;
}

.flex-end {
  @apply flex items-center justify-end;
}

/* Grid utilities */
.grid-center {
  @apply grid place-items-center;
}

.grid-auto-fill {
  grid-template-columns: repeat(auto-fill, minmax(var(--min-width, 200px), 1fr));
}

.grid-auto-fit {
  grid-template-columns: repeat(auto-fit, minmax(var(--min-width, 200px), 1fr));
}
```

### Typography Utilities
```css
/* Text truncation */
.truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.truncate-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Text decoration */
.text-gradient {
  background: linear-gradient(135deg, #2563eb, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

This comprehensive styling guide ensures consistent, accessible, and maintainable styling across the entire Activation Manager application.