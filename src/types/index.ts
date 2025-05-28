export interface Platform {
  id: string;
  name: string;
  logo: string;
  connected: boolean;
  lastSync?: Date;
}

export interface AudienceCriteria {
  id: string;
  type: 'demographic' | 'behavior' | 'interest';
  field: string;
  operator: 'equals' | 'contains' | 'greater_than' | 'less_than' | 'between';
  value: any;
}

export interface Audience {
  id: string;
  name: string;
  description?: string;
  type?: '1st-party' | '3rd-party' | 'clean-room';
  subtype?: 'rampid' | 'uid2' | 'google-pair' | 'yahoo-connect' | 'maid' | 'postal-code' | 'prizm-segment' | 'partner-id';
  criteria: AudienceCriteria[];
  estimatedSize: number;
  createdAt: Date;
  updatedAt: Date;
  platforms: string[];
}

export interface Distribution {
  id: string;
  audienceId: string;
  platformId: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  startedAt: Date;
  completedAt?: Date;
  recordsProcessed?: number;
  error?: string;
}

export interface AnalyticsData {
  date: string;
  audienceId: string;
  platformId: string;
  impressions: number;
  clicks: number;
  conversions: number;
  spend: number;
}