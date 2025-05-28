// Debug helper for demo testing
export const debugLog = (component: string, action: string, data?: any) => {
  if (process.env.NODE_ENV === 'development') {
    console.log(`[${component}] ${action}`, data || '');
  }
};

// Check if images are loading properly
export const checkImageLoad = (imageSrc: string): Promise<boolean> => {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      debugLog('ImageLoader', `Successfully loaded: ${imageSrc}`);
      resolve(true);
    };
    img.onerror = () => {
      debugLog('ImageLoader', `Failed to load: ${imageSrc}`);
      resolve(false);
    };
    img.src = imageSrc;
  });
};

// Check localStorage for any saved data
export const checkLocalStorage = () => {
  const keys = Object.keys(localStorage);
  debugLog('LocalStorage', `Found ${keys.length} items`, keys);
  return keys;
};

// Performance check
export const measurePerformance = (componentName: string) => {
  const startTime = performance.now();
  
  return () => {
    const endTime = performance.now();
    const duration = endTime - startTime;
    debugLog('Performance', `${componentName} rendered in ${duration.toFixed(2)}ms`);
  };
};