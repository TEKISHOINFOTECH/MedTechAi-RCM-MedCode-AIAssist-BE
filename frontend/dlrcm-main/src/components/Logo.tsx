import { useState } from 'react';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  showStatusIndicator?: boolean;
}

export function Logo({ size = 'md', className = '', showStatusIndicator = false }: LogoProps) {
  const [imageLoaded, setImageLoaded] = useState(false);
  
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  return (
    <div className={`logo-container ${className}`}>
      {!imageLoaded && (
        <div 
          className={`${sizeClasses[size]} bg-slate-200 animate-pulse rounded-lg flex items-center justify-center`}
        >
          <span className="text-slate-500 text-xs font-medium">MedTechAi</span>
        </div>
      )}
      <img 
        src="/medtechai-logo.png" 
        alt="MedTechAi Logo" 
        className={`logo-hover object-contain ${sizeClasses[size]} ${imageLoaded ? 'block' : 'hidden'}`}
        onLoad={() => setImageLoaded(true)}
        onError={() => setImageLoaded(true)}
      />
      {showStatusIndicator && imageLoaded && (
        <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full border-2 border-white animate-pulse"></div>
      )}
    </div>
  );
}