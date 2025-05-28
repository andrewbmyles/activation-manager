import React from 'react';
import { PlatformLogos } from '../data/platformLogos';

interface PlatformLogoProps {
  platform: string;
  className?: string;
}

export function PlatformLogo({ platform, className = "w-6 h-6" }: PlatformLogoProps) {
  const logo = PlatformLogos[platform as keyof typeof PlatformLogos];
  
  if (logo) {
    return <div className={`${className} flex items-center justify-center`}>
      {React.cloneElement(logo, {
        className: "w-full h-full object-contain"
      })}
    </div>;
  }
  
  // Fallback for unknown platforms
  return <div className={`${className} bg-gray-300 rounded flex items-center justify-center`}>
    <span className="text-gray-600 text-xs font-bold">{platform.charAt(0).toUpperCase()}</span>
  </div>;
}