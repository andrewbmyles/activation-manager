/**
 * Utility functions for audience management
 */

import { Users, Gamepad2, ShoppingBag, Heart, Briefcase, Home, Car, Plane, Music, Book, Coffee, Camera, Palette, Globe, Dumbbell, Sparkles } from 'lucide-react';

// Generate a random audience size between min and max
export function generateRandomAudienceSize(min: number = 56798, max: number = 89380): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// Generate audience name based on criteria
export function generateAudienceName(query: string): string {
  const queryLower = query.toLowerCase();
  
  // Extract key concepts
  const ageGroups: Record<string, string> = {
    '18-24': 'Gen Z',
    '25-34': 'Millennial',
    '35-44': 'Gen X',
    '45-54': 'Generation X',
    '55-64': 'Baby Boomer',
    '65+': 'Senior',
    'millennial': 'Millennial',
    'gen z': 'Gen Z',
    'gen x': 'Gen X',
    'young': 'Young',
    'middle aged': 'Middle-Aged',
    'senior': 'Senior',
    'elderly': 'Senior'
  };
  
  const genders: Record<string, string> = {
    'female': 'Women',
    'male': 'Males',
    'women': 'Women',
    'men': 'Males',
    'woman': 'Women',
    'man': 'Males'
  };
  
  const interests: Record<string, string> = {
    'fashion': 'Fashion-Forward',
    'gaming': 'Gaming-Enthusiast',
    'video game': 'Gaming-Enthusiast',
    'game': 'Gaming-Enthusiast',
    'sports': 'Sports-Loving',
    'technology': 'Tech-Savvy',
    'travel': 'Travel-Minded',
    'food': 'Food-Loving',
    'fitness': 'Fitness-Focused',
    'music': 'Music-Loving',
    'art': 'Art-Appreciating',
    'environment': 'Eco-Conscious',
    'sustainable': 'Sustainability-Minded',
    'luxury': 'Luxury-Seeking',
    'budget': 'Value-Conscious',
    'parent': 'Family-Oriented',
    'executive': 'Executive',
    'professional': 'Career-Driven',
    'entrepreneur': 'Entrepreneurial',
    'student': 'Student',
    'health': 'Health-Conscious'
  };
  
  const locations: Record<string, string> = {
    'suburban': 'Suburban',
    'urban': 'Urban',
    'rural': 'Rural',
    'city': 'Metropolitan',
    'metro': 'Metro',
    'downtown': 'Downtown'
  };
  
  // Build name components
  let nameComponents: string[] = [];
  
  // Add interest/behavior modifier
  for (const [key, value] of Object.entries(interests)) {
    if (queryLower.includes(key)) {
      nameComponents.push(value);
      break;
    }
  }
  
  // Add location if present
  for (const [key, value] of Object.entries(locations)) {
    if (queryLower.includes(key)) {
      nameComponents.push(value);
      break;
    }
  }
  
  // Add age group
  for (const [key, value] of Object.entries(ageGroups)) {
    if (queryLower.includes(key)) {
      nameComponents.push(value);
      break;
    }
  }
  
  // Add gender
  for (const [key, value] of Object.entries(genders)) {
    if (queryLower.includes(key)) {
      nameComponents.push(value);
      break;
    }
  }
  
  // If no components found, use generic name
  if (nameComponents.length === 0) {
    return 'Custom Audience Segment';
  }
  
  // Join components intelligently
  return nameComponents.join(' ');
}

// Convert technical criteria to natural language
export function formatCriteriaNaturalLanguage(
  query: string,
  selectedVariables?: string[],
  variableDetails?: any[]
): string {
  const queryLower = query.toLowerCase();
  let components: string[] = [];
  
  // Extract demographic info
  const genderMatch = queryLower.match(/\b(males?|females?|men|women|man|woman)\b/gi);
  if (genderMatch) {
    const gender = genderMatch[0].toLowerCase();
    if (gender === 'male' || gender === 'males' || gender === 'men' || gender === 'man') {
      components.push('Males');
    } else {
      components.push('Females');
    }
  }
  
  // Extract age range
  const ageRangeMatch = queryLower.match(/(\d+)\s*[-–]\s*(\d+)/);
  const ageMatch = queryLower.match(/age[sd]?\s+(\d+)\s*[-–]\s*(\d+)/i);
  
  if (ageRangeMatch || ageMatch) {
    const match = ageRangeMatch || ageMatch;
    if (match) {
      components.push(`between the ages of ${match[1]} and ${match[2]}`);
    }
  } else if (queryLower.includes('millennial')) {
    components.push('between the ages of 25 and 40');
  } else if (queryLower.includes('gen z')) {
    components.push('between the ages of 18 and 24');
  } else if (queryLower.includes('senior')) {
    components.push('aged 65 and above');
  }
  
  // Extract interests and behaviors
  const interestPhrases: Record<string, string> = {
    'fashion': 'are interested in fashion',
    'gaming': 'are interested in video games',
    'sports': 'are sports enthusiasts',
    'technology': 'are interested in technology',
    'travel': 'enjoy traveling',
    'food': 'are food enthusiasts',
    'fitness': 'are focused on fitness and health',
    'music': 'are music lovers',
    'art': 'appreciate art and culture',
    'environment': 'are environmentally conscious',
    'sustainable': 'value sustainability',
    'luxury': 'prefer luxury products and services',
    'budget': 'are value-conscious shoppers',
    'parent': 'are parents',
    'professional': 'are career-driven professionals',
    'entrepreneur': 'have entrepreneurial interests',
    'student': 'are students',
    'health': 'prioritize health and wellness'
  };
  
  let interests: string[] = [];
  for (const [key, phrase] of Object.entries(interestPhrases)) {
    if (queryLower.includes(key)) {
      interests.push(phrase);
    }
  }
  
  // Add location info
  if (queryLower.includes('urban') || queryLower.includes('city')) {
    interests.push('live in urban areas');
  } else if (queryLower.includes('suburban')) {
    interests.push('live in suburban areas');
  } else if (queryLower.includes('rural')) {
    interests.push('live in rural areas');
  }
  
  // Add income info
  if (queryLower.includes('high income') || queryLower.includes('affluent') || queryLower.includes('high disposable income')) {
    interests.push('have high disposable income');
  } else if (queryLower.includes('middle income')) {
    interests.push('are middle-income earners');
  }
  
  // Combine components
  let description = components.join(' ');
  
  if (interests.length > 0) {
    if (description) {
      description += ' who ';
    } else {
      description = 'People who ';
    }
    
    if (interests.length === 1) {
      description += interests[0];
    } else if (interests.length === 2) {
      description += interests.join(' and ');
    } else {
      const lastInterest = interests.pop();
      description += interests.join(', ') + ', and ' + lastInterest;
    }
  }
  
  // Fallback if no description generated
  if (!description) {
    description = 'Custom audience based on selected criteria';
  }
  
  return description;
}

// Get appropriate icon for audience based on criteria
export function getAudienceIcon(query: string) {
  const queryLower = query.toLowerCase();
  
  // Check for specific interests/categories
  if (queryLower.includes('gaming') || queryLower.includes('video game')) {
    return Gamepad2;
  }
  if (queryLower.includes('fashion') || queryLower.includes('shopping')) {
    return ShoppingBag;
  }
  if (queryLower.includes('health') || queryLower.includes('fitness')) {
    return Dumbbell;
  }
  if (queryLower.includes('family') || queryLower.includes('families') || queryLower.includes('parent') || queryLower.includes('children')) {
    return Heart;
  }
  if (queryLower.includes('professional') || queryLower.includes('business')) {
    return Briefcase;
  }
  if (queryLower.includes('travel')) {
    return Plane;
  }
  if (queryLower.includes('music')) {
    return Music;
  }
  if (queryLower.includes('education') || queryLower.includes('student')) {
    return Book;
  }
  if (queryLower.includes('food') || queryLower.includes('dining')) {
    return Coffee;
  }
  if (queryLower.includes('art') || queryLower.includes('creative')) {
    return Palette;
  }
  if (queryLower.includes('technology') || queryLower.includes('tech')) {
    return Globe;
  }
  if (queryLower.includes('photo') || queryLower.includes('visual')) {
    return Camera;
  }
  if (queryLower.includes('home') || queryLower.includes('real estate')) {
    return Home;
  }
  if (queryLower.includes('auto') || queryLower.includes('car')) {
    return Car;
  }
  
  // Default icon
  return Users;
}

// Get icon color based on audience type
export function getAudienceIconColor(query: string): string {
  const queryLower = query.toLowerCase();
  
  if (queryLower.includes('gaming')) return '#8B5CF6'; // Purple
  if (queryLower.includes('fashion')) return '#EC4899'; // Pink
  if (queryLower.includes('health') || queryLower.includes('fitness')) return '#10B981'; // Green
  if (queryLower.includes('family')) return '#EF4444'; // Red
  if (queryLower.includes('professional') || queryLower.includes('business')) return '#3B82F6'; // Blue
  if (queryLower.includes('travel')) return '#06B6D4'; // Cyan
  if (queryLower.includes('music')) return '#F59E0B'; // Amber
  if (queryLower.includes('education')) return '#6366F1'; // Indigo
  if (queryLower.includes('food')) return '#F97316'; // Orange
  if (queryLower.includes('technology')) return '#14B8A6'; // Teal
  
  return '#6B7280'; // Default gray
}

// Generate audience insights
export function generateAudienceInsights(query: string, size: number): string[] {
  const insights: string[] = [];
  const sizeK = Math.round(size / 1000);
  
  // Size-based insight
  if (size > 80000) {
    insights.push(`Large audience with ${sizeK}K+ potential customers`);
  } else if (size > 70000) {
    insights.push(`Strong audience reach of ${sizeK}K+ individuals`);
  } else {
    insights.push(`Focused audience of ${sizeK}K+ targeted users`);
  }
  
  // Query-based insights
  const queryLower = query.toLowerCase();
  
  if (queryLower.includes('high income') || queryLower.includes('affluent') || queryLower.includes('high disposable income')) {
    insights.push('High purchasing power demographic');
  }
  
  if (queryLower.includes('urban')) {
    insights.push('Concentrated in metropolitan areas');
  }
  
  if (queryLower.includes('millennial') || queryLower.includes('gaming') || queryLower.includes('gen z')) {
    insights.push('Digital-native generation');
  }
  
  if (queryLower.includes('parent') || queryLower.includes('families') || queryLower.includes('family')) {
    insights.push('Family decision makers');
  }
  
  if (queryLower.includes('professional')) {
    insights.push('Career-focused individuals');
  }
  
  return insights;
}