import React from 'react';
import { 
  Users, 
  ShoppingCart, 
  Cpu, 
  Building2, 
  TrendingUp, 
  UserCheck,
  Calendar,
  DollarSign,
  Target,
  Globe
} from 'lucide-react';

interface AudienceIconProps {
  audienceName: string;
  className?: string;
}

export function AudienceIcon({ audienceName, className = "w-5 h-5" }: AudienceIconProps) {
  const name = audienceName.toLowerCase();
  
  // Determine icon based on audience name
  if (name.includes('value') || name.includes('vip')) {
    return <DollarSign className={className} />;
  } else if (name.includes('cart') || name.includes('abandon')) {
    return <ShoppingCart className={className} />;
  } else if (name.includes('tech') || name.includes('digital')) {
    return <Cpu className={className} />;
  } else if (name.includes('millennial') || name.includes('gen')) {
    return <Users className={className} />;
  } else if (name.includes('frequent') || name.includes('loyal')) {
    return <TrendingUp className={className} />;
  } else if (name.includes('lookalike') || name.includes('similar')) {
    return <UserCheck className={className} />;
  } else if (name.includes('b2b') || name.includes('business') || name.includes('decision')) {
    return <Building2 className={className} />;
  } else if (name.includes('weekend') || name.includes('seasonal')) {
    return <Calendar className={className} />;
  } else if (name.includes('global') || name.includes('international')) {
    return <Globe className={className} />;
  }
  
  // Default icon
  return <Target className={className} />;
}