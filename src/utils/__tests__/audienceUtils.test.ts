/**
 * Unit tests for audienceUtils.ts
 */

import {
  generateAudienceName,
  formatCriteriaNaturalLanguage,
  generateRandomAudienceSize,
  getAudienceIcon,
  getAudienceIconColor,
  generateAudienceInsights
} from '../audienceUtils';

import { 
  Users, Gamepad2, ShoppingBag, Heart, Briefcase, Home, Car, Plane, 
  Music, Book, Coffee, Camera, Palette, Globe, Dumbbell 
} from 'lucide-react';

describe('audienceUtils', () => {
  
  describe('generateAudienceName', () => {
    it('should generate gaming-related names', () => {
      const queries = [
        'Find gaming enthusiasts who own consoles',
        'Video game players aged 18-24',
        'Gaming console owners'
      ];
      
      queries.forEach(query => {
        const name = generateAudienceName(query);
        expect(name).toContain('Gaming-Enthusiast');
      });
    });

    it('should generate fashion-related names', () => {
      const queries = [
        'Fashion-forward millennials interested in luxury brands',
        'Women who shop for fashionable clothing',
        'Fashion enthusiasts with high spending'
      ];
      
      queries.forEach(query => {
        const name = generateAudienceName(query);
        expect(name).toContain('Fashion-Forward');
      });
    });

    it('should include demographic information', () => {
      const testCases = [
        { query: 'millennial women interested in fashion', expected: ['Millennial', 'Women'] },
        { query: 'urban males aged 25-34', expected: ['Urban'] },
        { query: 'suburban families with children', expected: ['Suburban'] },
        { query: 'professional executives in business', expected: ['Executive'] }
      ];

      testCases.forEach(({ query, expected }) => {
        const name = generateAudienceName(query);
        expected.forEach(term => {
          expect(name).toContain(term);
        });
      });
    });

    it('should return fallback name for unrecognized queries', () => {
      const name = generateAudienceName('completely unrecognized random text xyz123');
      expect(name).toBe('Custom Audience Segment');
    });

    it('should handle empty or null inputs gracefully', () => {
      expect(generateAudienceName('')).toBe('Custom Audience Segment');
      expect(generateAudienceName('   ')).toBe('Custom Audience Segment');
    });

    it('should combine multiple components intelligently', () => {
      const name = generateAudienceName('luxury fashion enthusiasts in urban millennial women');
      const components = name.split(' ');
      expect(components.length).toBeGreaterThan(1);
      expect(name).toMatch(/Fashion-Forward|Luxury-Seeking/);
      expect(name).toMatch(/Urban|Millennial|Women/);
    });
  });

  describe('formatCriteriaNaturalLanguage', () => {
    it('should format gender and age criteria', () => {
      const testCases = [
        {
          query: 'Find males aged 25-34 who are interested in gaming',
          expected: 'Males between the ages of 25 and 34 who are interested in video games'
        },
        {
          query: 'Female millennials interested in fashion',
          expected: 'Females between the ages of 25 and 40 who are interested in fashion'
        }
      ];

      testCases.forEach(({ query, expected }) => {
        const result = formatCriteriaNaturalLanguage(query);
        expect(result).toBe(expected);
      });
    });

    it('should handle multiple interests', () => {
      const query = 'Urban professionals interested in technology and travel';
      const result = formatCriteriaNaturalLanguage(query);
      
      expect(result).toContain('are interested in technology');
      expect(result).toContain('enjoy traveling');
      expect(result).toContain('live in urban areas');
      expect(result).toContain(' and ');
    });

    it('should format income levels', () => {
      const query = 'High income families in suburban areas';
      const result = formatCriteriaNaturalLanguage(query);
      
      expect(result).toContain('have high disposable income');
    });

    it('should handle age groups without specific ranges', () => {
      const testCases = [
        { query: 'millennial professionals', expected: 'between the ages of 25 and 40' },
        { query: 'gen z gamers', expected: 'between the ages of 18 and 24' },
        { query: 'senior citizens', expected: 'aged 65 and above' }
      ];

      testCases.forEach(({ query, expected }) => {
        const result = formatCriteriaNaturalLanguage(query);
        expect(result).toContain(expected);
      });
    });

    it('should return fallback for unrecognized queries', () => {
      const result = formatCriteriaNaturalLanguage('completely random unrecognized text');
      expect(result).toBe('Custom audience based on selected criteria');
    });

    it('should handle complex multi-faceted queries', () => {
      const query = 'Find environmentally conscious millennial women with high income in urban areas';
      const result = formatCriteriaNaturalLanguage(query);
      
      expect(result).toContain('Females');
      expect(result).toContain('between the ages of 25 and 40');
      expect(result).toContain('environmentally conscious');
      expect(result).toContain('live in urban areas');
      expect(result).toContain('high disposable income');
    });
  });

  describe('generateRandomAudienceSize', () => {
    it('should generate sizes within default range', () => {
      for (let i = 0; i < 100; i++) {
        const size = generateRandomAudienceSize();
        expect(size).toBeGreaterThanOrEqual(56798);
        expect(size).toBeLessThanOrEqual(89380);
        expect(Number.isInteger(size)).toBe(true);
      }
    });

    it('should generate sizes within custom range', () => {
      const min = 10000;
      const max = 20000;
      
      for (let i = 0; i < 50; i++) {
        const size = generateRandomAudienceSize(min, max);
        expect(size).toBeGreaterThanOrEqual(min);
        expect(size).toBeLessThanOrEqual(max);
      }
    });

    it('should handle edge cases', () => {
      // Same min and max
      expect(generateRandomAudienceSize(50000, 50000)).toBe(50000);
      
      // Min = 1, Max = 1
      expect(generateRandomAudienceSize(1, 1)).toBe(1);
    });

    it('should generate different values on multiple calls', () => {
      const sizes = new Set();
      for (let i = 0; i < 20; i++) {
        sizes.add(generateRandomAudienceSize());
      }
      // Should have multiple different values (very high probability)
      expect(sizes.size).toBeGreaterThan(1);
    });
  });

  describe('getAudienceIcon', () => {
    it('should return correct icons for different audience types', () => {
      const testCases = [
        { query: 'gaming console enthusiasts', expected: Gamepad2 },
        { query: 'fashion shopping lovers', expected: ShoppingBag },
        { query: 'health fitness focused individuals', expected: Dumbbell },
        { query: 'families with children', expected: Heart },
        { query: 'professional business executives', expected: Briefcase },
        { query: 'travel enthusiasts who vacation frequently', expected: Plane },
        { query: 'music lovers and entertainment fans', expected: Music },
        { query: 'students in education programs', expected: Book },
        { query: 'technology early adopters', expected: Globe },
        { query: 'home real estate investors', expected: Home },
        { query: 'automotive car enthusiasts', expected: Car }
      ];

      testCases.forEach(({ query, expected }) => {
        const icon = getAudienceIcon(query);
        expect(icon).toBe(expected);
      });
    });

    it('should return default icon for unrecognized queries', () => {
      const icon = getAudienceIcon('completely random unrelated text');
      expect(icon).toBe(Users);
    });

    it('should be case insensitive', () => {
      const upperCase = getAudienceIcon('GAMING CONSOLE ENTHUSIASTS');
      const lowerCase = getAudienceIcon('gaming console enthusiasts');
      const mixedCase = getAudienceIcon('Gaming Console Enthusiasts');
      
      expect(upperCase).toBe(Gamepad2);
      expect(lowerCase).toBe(Gamepad2);
      expect(mixedCase).toBe(Gamepad2);
    });

    it('should handle empty strings', () => {
      expect(getAudienceIcon('')).toBe(Users);
      expect(getAudienceIcon('   ')).toBe(Users);
    });
  });

  describe('getAudienceIconColor', () => {
    it('should return correct colors for different audience types', () => {
      const testCases = [
        { query: 'gaming enthusiasts', expected: '#8B5CF6' }, // Purple
        { query: 'fashion lovers', expected: '#EC4899' }, // Pink
        { query: 'health fitness focused', expected: '#10B981' }, // Green
        { query: 'family oriented', expected: '#EF4444' }, // Red
        { query: 'professional business', expected: '#3B82F6' }, // Blue
        { query: 'travel enthusiasts', expected: '#06B6D4' }, // Cyan
        { query: 'music lovers', expected: '#F59E0B' }, // Amber
        { query: 'education students', expected: '#6366F1' }, // Indigo
        { query: 'food dining enthusiasts', expected: '#F97316' }, // Orange
        { query: 'technology adopters', expected: '#14B8A6' } // Teal
      ];

      testCases.forEach(({ query, expected }) => {
        const color = getAudienceIconColor(query);
        expect(color).toBe(expected);
      });
    });

    it('should return default color for unrecognized queries', () => {
      const color = getAudienceIconColor('completely random text');
      expect(color).toBe('#6B7280'); // Default gray
    });

    it('should be case insensitive', () => {
      const upperCase = getAudienceIconColor('GAMING ENTHUSIASTS');
      const lowerCase = getAudienceIconColor('gaming enthusiasts');
      
      expect(upperCase).toBe('#8B5CF6');
      expect(lowerCase).toBe('#8B5CF6');
    });

    it('should return valid hex color codes', () => {
      const queries = [
        'gaming', 'fashion', 'health', 'family', 'professional',
        'travel', 'music', 'education', 'food', 'technology', 'random'
      ];

      queries.forEach(query => {
        const color = getAudienceIconColor(query);
        expect(color).toMatch(/^#[0-9A-F]{6}$/i);
      });
    });
  });

  describe('generateAudienceInsights', () => {
    it('should generate size-based insights', () => {
      const testCases = [
        { size: 85000, expected: 'Large audience with 85K+ potential customers' },
        { size: 75000, expected: 'Strong audience reach of 75K+ individuals' },
        { size: 60000, expected: 'Focused audience of 60K+ targeted users' }
      ];

      testCases.forEach(({ size, expected }) => {
        const insights = generateAudienceInsights('generic query', size);
        expect(insights).toContain(expected);
      });
    });

    it('should generate query-based insights', () => {
      const testCases = [
        {
          query: 'high income urban millennials',
          expected: ['High purchasing power demographic', 'Concentrated in metropolitan areas', 'Digital-native generation']
        },
        {
          query: 'professional executives with families',
          expected: ['Career-focused individuals', 'Family decision makers']
        },
        {
          query: 'parent families with children',
          expected: ['Family decision makers']
        }
      ];

      testCases.forEach(({ query, expected }) => {
        const insights = generateAudienceInsights(query, 70000);
        expected.forEach(expectedInsight => {
          expect(insights).toContain(expectedInsight);
        });
      });
    });

    it('should always include at least one insight', () => {
      const insights = generateAudienceInsights('random text', 50000);
      expect(insights.length).toBeGreaterThan(0);
    });

    it('should handle edge cases', () => {
      // Very small audience
      const smallInsights = generateAudienceInsights('test', 1000);
      expect(smallInsights.length).toBeGreaterThan(0);
      expect(smallInsights[0]).toContain('1K+');

      // Very large audience
      const largeInsights = generateAudienceInsights('test', 150000);
      expect(largeInsights.length).toBeGreaterThan(0);
      expect(largeInsights[0]).toContain('150K+');
    });

    it('should not duplicate insights', () => {
      const insights = generateAudienceInsights('high income urban millennial professional parent', 80000);
      const uniqueInsights = new Set(insights);
      expect(insights.length).toBe(uniqueInsights.size);
    });

    it('should format size correctly in insights', () => {
      const testCases = [
        { size: 67842, expected: '68K+' },
        { size: 84720, expected: '85K+' },
        { size: 56798, expected: '57K+' }
      ];

      testCases.forEach(({ size, expected }) => {
        const insights = generateAudienceInsights('test query', size);
        expect(insights[0]).toContain(expected);
      });
    });
  });

  describe('Integration tests', () => {
    it('should work together for complete audience enhancement', () => {
      const originalQuery = 'Find environmentally conscious millennials with high disposable income in urban areas';
      
      const enhancedName = generateAudienceName(originalQuery);
      const naturalLanguage = formatCriteriaNaturalLanguage(originalQuery);
      const randomSize = generateRandomAudienceSize();
      const icon = getAudienceIcon(originalQuery);
      const color = getAudienceIconColor(originalQuery);
      const insights = generateAudienceInsights(originalQuery, randomSize);
      
      // Verify all components work together
      expect(enhancedName).toBeTruthy();
      expect(enhancedName).not.toBe('Custom Audience Segment');
      expect(naturalLanguage).toContain('environmentally conscious');
      expect(randomSize).toBeGreaterThanOrEqual(56798);
      expect(randomSize).toBeLessThanOrEqual(89380);
      expect(icon).toBeDefined();
      expect(color).toMatch(/^#[0-9A-F]{6}$/i);
      expect(insights.length).toBeGreaterThan(0);
    });

    it('should handle edge case queries consistently', () => {
      const edgeCases = ['', '   ', 'xyz123random', 'a'];
      
      edgeCases.forEach(query => {
        const name = generateAudienceName(query);
        const criteria = formatCriteriaNaturalLanguage(query);
        const icon = getAudienceIcon(query);
        const color = getAudienceIconColor(query);
        const insights = generateAudienceInsights(query, 60000);
        
        // Should not throw errors and provide fallbacks
        expect(name).toBeTruthy();
        expect(criteria).toBeTruthy();
        expect(icon).toBe(Users);
        expect(color).toBe('#6B7280');
        expect(insights.length).toBeGreaterThan(0);
      });
    });
  });
});