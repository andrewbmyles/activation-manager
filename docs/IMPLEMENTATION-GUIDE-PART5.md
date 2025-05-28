# Activation Manager - Implementation Guide (Part 5)

## Platform Integration Framework

### Platform Adapter Architecture

#### 1. Base Platform Adapter
```typescript
// packages/backend/src/modules/platform/adapters/base.adapter.ts
import { EventEmitter } from 'events';
import { Logger } from '@/common/logger';
import { 
  Platform, 
  PlatformCredentials, 
  AudienceData,
  DistributionResult,
  PlatformCapabilities,
  RateLimiter 
} from '@shared/types';

export abstract class BasePlatformAdapter extends EventEmitter {
  protected logger: Logger;
  protected rateLimiter: RateLimiter;
  protected credentials: PlatformCredentials;
  protected platform: Platform;

  constructor(platform: Platform, credentials: PlatformCredentials) {
    super();
    this.platform = platform;
    this.credentials = credentials;
    this.logger = new Logger(`${platform.name}Adapter`);
    this.rateLimiter = new RateLimiter(platform.rateLimits);
  }

  // Abstract methods that each platform must implement
  abstract validateCredentials(): Promise<boolean>;
  abstract uploadAudience(audienceData: AudienceData): Promise<DistributionResult>;
  abstract getAudienceStatus(audienceId: string): Promise<any>;
  abstract deleteAudience(audienceId: string): Promise<boolean>;
  abstract getCapabilities(): PlatformCapabilities;
  abstract testConnection(): Promise<boolean>;

  // Common methods shared across all platforms
  protected async executeWithRetry<T>(
    operation: () => Promise<T>,
    maxRetries = 3,
    backoffMs = 1000
  ): Promise<T> {
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        await this.rateLimiter.checkLimit();
        const result = await operation();
        this.emit('operation_success', { attempt });
        return result;
      } catch (error) {
        lastError = error as Error;
        this.logger.warn(`Operation failed (attempt ${attempt}/${maxRetries})`, error);
        
        if (attempt < maxRetries) {
          const delay = backoffMs * Math.pow(2, attempt - 1);
          await this.sleep(delay);
        }
      }
    }

    this.emit('operation_failed', { error: lastError, attempts: maxRetries });
    throw lastError;
  }

  protected async batchProcess<T, R>(
    items: T[],
    batchSize: number,
    processor: (batch: T[]) => Promise<R[]>
  ): Promise<R[]> {
    const results: R[] = [];
    
    for (let i = 0; i < items.length; i += batchSize) {
      const batch = items.slice(i, i + batchSize);
      const batchResults = await processor(batch);
      results.push(...batchResults);
      
      this.emit('batch_processed', {
        processed: i + batch.length,
        total: items.length,
        percentage: Math.round(((i + batch.length) / items.length) * 100),
      });
    }

    return results;
  }

  protected normalizeAudienceData(data: AudienceData): any {
    // Default normalization - can be overridden by specific adapters
    return {
      users: data.users.map(user => ({
        ...user,
        // Ensure all required fields are present
        email: user.email?.toLowerCase(),
        phone: this.normalizePhoneNumber(user.phone),
        // Add platform-specific identifiers
      })),
      metadata: {
        audienceId: data.audienceId,
        audienceName: data.audienceName,
        createdAt: new Date().toISOString(),
      },
    };
  }

  protected normalizePhoneNumber(phone?: string): string | undefined {
    if (!phone) return undefined;
    
    // Remove all non-numeric characters
    const cleaned = phone.replace(/\D/g, '');
    
    // Add country code if missing (assuming US)
    if (cleaned.length === 10) {
      return `+1${cleaned}`;
    }
    
    return `+${cleaned}`;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Rate Limiter Implementation
export class RateLimiter {
  private requests: number[] = [];
  private readonly windowMs: number;
  private readonly maxRequests: number;

  constructor(limits: { requestsPerMinute: number }) {
    this.windowMs = 60 * 1000; // 1 minute
    this.maxRequests = limits.requestsPerMinute;
  }

  async checkLimit(): Promise<void> {
    const now = Date.now();
    const windowStart = now - this.windowMs;
    
    // Remove old requests outside the window
    this.requests = this.requests.filter(time => time > windowStart);
    
    if (this.requests.length >= this.maxRequests) {
      const oldestRequest = this.requests[0];
      const waitTime = oldestRequest + this.windowMs - now;
      
      if (waitTime > 0) {
        throw new Error(`Rate limit exceeded. Wait ${Math.ceil(waitTime / 1000)}s`);
      }
    }
    
    this.requests.push(now);
  }
}
```

#### 2. Meta (Facebook) Adapter Implementation
```typescript
// packages/backend/src/modules/platform/adapters/meta.adapter.ts
import axios, { AxiosInstance } from 'axios';
import crypto from 'crypto';
import { BasePlatformAdapter } from './base.adapter';
import { 
  AudienceData, 
  DistributionResult, 
  PlatformCapabilities 
} from '@shared/types';

export class MetaAdapter extends BasePlatformAdapter {
  private client: AxiosInstance;
  private readonly API_VERSION = 'v18.0';
  private readonly BASE_URL = 'https://graph.facebook.com';

  constructor(platform: Platform, credentials: MetaCredentials) {
    super(platform, credentials);
    
    this.client = axios.create({
      baseURL: `${this.BASE_URL}/${this.API_VERSION}`,
      headers: {
        'Authorization': `Bearer ${credentials.accessToken}`,
        'Content-Type': 'application/json',
      },
    });
  }

  async validateCredentials(): Promise<boolean> {
    try {
      const response = await this.client.get('/me', {
        params: {
          fields: 'id,name',
        },
      });
      
      return response.status === 200;
    } catch (error) {
      this.logger.error('Credential validation failed', error);
      return false;
    }
  }

  async uploadAudience(audienceData: AudienceData): Promise<DistributionResult> {
    const startTime = Date.now();
    
    try {
      // Step 1: Create Custom Audience
      const audience = await this.createCustomAudience(audienceData);
      
      // Step 2: Hash user data
      const hashedData = this.hashUserData(audienceData.users);
      
      // Step 3: Upload in batches
      const batchSize = 10000; // Meta recommends max 10k per batch
      const uploadResults = await this.batchProcess(
        hashedData,
        batchSize,
        async (batch) => this.uploadBatch(audience.id, batch)
      );
      
      // Step 4: Get match statistics
      const stats = await this.getAudienceStats(audience.id);
      
      return {
        success: true,
        platformAudienceId: audience.id,
        recordsProcessed: audienceData.users.length,
        recordsMatched: stats.approximate_count || 0,
        matchRate: stats.approximate_count 
          ? (stats.approximate_count / audienceData.users.length) * 100 
          : 0,
        processingTimeMs: Date.now() - startTime,
        details: {
          audienceName: audience.name,
          deliveryStatus: audience.delivery_status,
        },
      };
    } catch (error) {
      this.logger.error('Audience upload failed', error);
      
      return {
        success: false,
        error: error.message,
        recordsProcessed: 0,
        recordsMatched: 0,
        matchRate: 0,
        processingTimeMs: Date.now() - startTime,
      };
    }
  }

  private async createCustomAudience(audienceData: AudienceData): Promise<any> {
    const response = await this.client.post(
      `/${this.credentials.adAccountId}/customaudiences`,
      {
        name: audienceData.audienceName,
        description: audienceData.description || 'Created via Activation Manager',
        customer_file_source: 'USER_PROVIDED_ONLY',
        subtype: 'CUSTOM',
        retention_days: 180,
      }
    );

    return response.data;
  }

  private hashUserData(users: any[]): any[] {
    return users.map(user => {
      const hashed: any = {};
      
      // Hash email
      if (user.email) {
        hashed.email = this.hashValue(user.email.toLowerCase());
      }
      
      // Hash phone
      if (user.phone) {
        hashed.phone = this.hashValue(this.normalizePhoneNumber(user.phone));
      }
      
      // Hash first name
      if (user.firstName) {
        hashed.fn = this.hashValue(user.firstName.toLowerCase());
      }
      
      // Hash last name
      if (user.lastName) {
        hashed.ln = this.hashValue(user.lastName.toLowerCase());
      }
      
      // Hash date of birth
      if (user.dateOfBirth) {
        hashed.dob = this.hashValue(user.dateOfBirth.replace(/-/g, ''));
      }
      
      // Add location data
      if (user.city) hashed.ct = this.hashValue(user.city.toLowerCase());
      if (user.state) hashed.st = this.hashValue(user.state.toLowerCase());
      if (user.zipCode) hashed.zip = this.hashValue(user.zipCode);
      if (user.country) hashed.country = this.hashValue(user.country.toLowerCase());
      
      return hashed;
    });
  }

  private hashValue(value: string): string {
    return crypto.createHash('sha256').update(value).digest('hex');
  }

  private async uploadBatch(audienceId: string, batch: any[]): Promise<any> {
    const response = await this.client.post(
      `/${audienceId}/users`,
      {
        payload: {
          schema: ['EMAIL', 'PHONE', 'FN', 'LN', 'DOB', 'CT', 'ST', 'ZIP', 'COUNTRY'],
          data: batch.map(user => [
            user.email,
            user.phone,
            user.fn,
            user.ln,
            user.dob,
            user.ct,
            user.st,
            user.zip,
            user.country,
          ]),
        },
      }
    );

    return response.data;
  }

  async getAudienceStatus(audienceId: string): Promise<any> {
    const response = await this.client.get(`/${audienceId}`, {
      params: {
        fields: 'name,approximate_count,delivery_status,operation_status',
      },
    });

    return response.data;
  }

  private async getAudienceStats(audienceId: string): Promise<any> {
    // Wait a bit for processing
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    return this.getAudienceStatus(audienceId);
  }

  async deleteAudience(audienceId: string): Promise<boolean> {
    try {
      await this.client.delete(`/${audienceId}`);
      return true;
    } catch (error) {
      this.logger.error('Failed to delete audience', error);
      return false;
    }
  }

  async testConnection(): Promise<boolean> {
    return this.validateCredentials();
  }

  getCapabilities(): PlatformCapabilities {
    return {
      supportsRealTimeSync: true,
      supportsBatchSync: true,
      maxAudienceSize: 30000000, // 30 million
      supportedDataTypes: ['email', 'phone', 'mobile_advertiser_id'],
      supportedOperations: ['create', 'update', 'delete'],
      rateLimits: {
        requestsPerMinute: 200,
        requestsPerDay: 100000,
      },
      features: {
        supportsIncrementalUpdates: true,
        supportsAudienceInsights: true,
        supportsLookalikeAudiences: true,
        supportsExclusions: true,
      },
    };
  }
}
```

#### 3. Google Ads Adapter Implementation
```typescript
// packages/backend/src/modules/platform/adapters/google.adapter.ts
import { GoogleAdsApi, Customer } from 'google-ads-api';
import { BasePlatformAdapter } from './base.adapter';
import { 
  AudienceData, 
  DistributionResult, 
  PlatformCapabilities 
} from '@shared/types';

export class GoogleAdsAdapter extends BasePlatformAdapter {
  private client: GoogleAdsApi;
  private customer: Customer;

  constructor(platform: Platform, credentials: GoogleCredentials) {
    super(platform, credentials);
    
    this.client = new GoogleAdsApi({
      client_id: credentials.clientId,
      client_secret: credentials.clientSecret,
      developer_token: credentials.developerToken,
      refresh_token: credentials.refreshToken,
    });

    this.customer = this.client.Customer({
      customer_id: credentials.customerId,
      login_customer_id: credentials.managerAccountId,
    });
  }

  async validateCredentials(): Promise<boolean> {
    try {
      const response = await this.customer.query(`
        SELECT customer.id, customer.descriptive_name
        FROM customer
        LIMIT 1
      `);
      
      return response.length > 0;
    } catch (error) {
      this.logger.error('Credential validation failed', error);
      return false;
    }
  }

  async uploadAudience(audienceData: AudienceData): Promise<DistributionResult> {
    const startTime = Date.now();
    
    try {
      // Step 1: Create User List
      const userList = await this.createUserList(audienceData);
      
      // Step 2: Format user data for upload
      const formattedData = this.formatUserData(audienceData.users);
      
      // Step 3: Upload in batches
      const batchSize = 1000000; // Google allows up to 1M per request
      await this.batchProcess(
        formattedData,
        batchSize,
        async (batch) => this.uploadUserData(userList.resourceName, batch)
      );
      
      // Step 4: Get match statistics (may take time to process)
      const stats = await this.getUserListStats(userList.resourceName);
      
      return {
        success: true,
        platformAudienceId: userList.id,
        recordsProcessed: audienceData.users.length,
        recordsMatched: stats.sizeForSearch || 0,
        matchRate: stats.sizeForSearch 
          ? (stats.sizeForSearch / audienceData.users.length) * 100 
          : 0,
        processingTimeMs: Date.now() - startTime,
        details: {
          userListName: userList.name,
          membershipStatus: userList.membershipStatus,
          sizeForDisplay: stats.sizeForDisplay,
          sizeForSearch: stats.sizeForSearch,
        },
      };
    } catch (error) {
      this.logger.error('Audience upload failed', error);
      
      return {
        success: false,
        error: error.message,
        recordsProcessed: 0,
        recordsMatched: 0,
        matchRate: 0,
        processingTimeMs: Date.now() - startTime,
      };
    }
  }

  private async createUserList(audienceData: AudienceData): Promise<any> {
    const userList = {
      name: audienceData.audienceName,
      description: audienceData.description || 'Created via Activation Manager',
      membershipLifeSpan: 540, // 540 days (maximum)
      crm_based_user_list: {
        upload_key_type: 'CONTACT_INFO',
        data_source_type: 'FIRST_PARTY',
      },
    };

    const operation = {
      create: userList,
    };

    const response = await this.customer.userLists.create([operation]);
    return response.results[0];
  }

  private formatUserData(users: any[]): any[] {
    return users.map(user => {
      const userIdentifier: any = {};
      
      // Add hashed email
      if (user.email) {
        userIdentifier.hashedEmail = this.hashSHA256(
          this.normalizeEmail(user.email)
        );
      }
      
      // Add hashed phone
      if (user.phone) {
        userIdentifier.hashedPhoneNumber = this.hashSHA256(
          this.normalizePhoneNumber(user.phone)
        );
      }
      
      // Add address info
      if (user.firstName || user.lastName || user.zipCode) {
        userIdentifier.addressInfo = {};
        
        if (user.firstName) {
          userIdentifier.addressInfo.hashedFirstName = this.hashSHA256(
            user.firstName.toLowerCase()
          );
        }
        
        if (user.lastName) {
          userIdentifier.addressInfo.hashedLastName = this.hashSHA256(
            user.lastName.toLowerCase()
          );
        }
        
        if (user.zipCode) {
          userIdentifier.addressInfo.zipCode = user.zipCode;
        }
        
        if (user.countryCode) {
          userIdentifier.addressInfo.countryCode = user.countryCode;
        }
      }
      
      return userIdentifier;
    });
  }

  private normalizeEmail(email: string): string {
    // Google's normalization rules
    const [localPart, domain] = email.toLowerCase().split('@');
    
    // Remove dots from gmail addresses
    if (domain === 'gmail.com') {
      const normalizedLocal = localPart.replace(/\./g, '');
      // Remove everything after + sign
      const plusIndex = normalizedLocal.indexOf('+');
      if (plusIndex > -1) {
        return normalizedLocal.substring(0, plusIndex) + '@' + domain;
      }
      return normalizedLocal + '@' + domain;
    }
    
    return email.toLowerCase();
  }

  private hashSHA256(value: string): string {
    return crypto.createHash('sha256').update(value).digest('hex');
  }

  private async uploadUserData(
    userListResourceName: string,
    userIdentifiers: any[]
  ): Promise<void> {
    const operations = userIdentifiers.map(userIdentifier => ({
      create: { userIdentifier },
    }));

    const request = {
      customerId: this.credentials.customerId,
      operations,
    };

    await this.customer.userListCustomerTypes.mutate(request);
  }

  private async getUserListStats(resourceName: string): Promise<any> {
    // Wait for processing
    await new Promise(resolve => setTimeout(resolve, 10000));
    
    const response = await this.customer.query(`
      SELECT 
        user_list.size_for_display,
        user_list.size_for_search,
        user_list.size_range_for_display,
        user_list.size_range_for_search,
        user_list.membership_status
      FROM user_list
      WHERE user_list.resource_name = '${resourceName}'
    `);
    
    return response[0]?.userList || {};
  }

  async getAudienceStatus(audienceId: string): Promise<any> {
    const response = await this.customer.query(`
      SELECT 
        user_list.id,
        user_list.name,
        user_list.size_for_display,
        user_list.size_for_search,
        user_list.membership_status,
        user_list.match_rate_percentage
      FROM user_list
      WHERE user_list.id = ${audienceId}
    `);
    
    return response[0]?.userList;
  }

  async deleteAudience(audienceId: string): Promise<boolean> {
    try {
      const operation = {
        remove: `customers/${this.credentials.customerId}/userLists/${audienceId}`,
      };
      
      await this.customer.userLists.remove([operation]);
      return true;
    } catch (error) {
      this.logger.error('Failed to delete audience', error);
      return false;
    }
  }

  async testConnection(): Promise<boolean> {
    return this.validateCredentials();
  }

  getCapabilities(): PlatformCapabilities {
    return {
      supportsRealTimeSync: false,
      supportsBatchSync: true,
      maxAudienceSize: 1000000000, // 1 billion
      supportedDataTypes: ['email', 'phone', 'address', 'mobile_id'],
      supportedOperations: ['create', 'append', 'remove', 'replace'],
      rateLimits: {
        requestsPerMinute: 100,
        requestsPerDay: 10000,
      },
      features: {
        supportsIncrementalUpdates: true,
        supportsAudienceInsights: false,
        supportsLookalikeAudiences: true,
        supportsExclusions: true,
        supportsCombinedAudiences: true,
      },
    };
  }
}
```

### Platform Integration Service

#### 1. Platform Service Implementation
```typescript
// packages/backend/src/modules/platform/services/platform.service.ts
import { injectable, inject } from 'inversify';
import { PrismaClient } from '@prisma/client';
import { EventBus } from '@/common/events';
import { CryptoService } from '@/common/crypto';
import { QueueService } from '@/common/queue';
import { PlatformAdapterFactory } from '../factories/platform-adapter.factory';
import { 
  Platform, 
  PlatformCredentials,
  ConnectPlatformDto,
  TestConnectionResult 
} from '@shared/types';

@injectable()
export class PlatformService {
  constructor(
    @inject('Prisma') private prisma: PrismaClient,
    @inject(EventBus) private eventBus: EventBus,
    @inject(CryptoService) private crypto: CryptoService,
    @inject(QueueService) private queue: QueueService,
    @inject(PlatformAdapterFactory) private adapterFactory: PlatformAdapterFactory
  ) {}

  async findAll(userId?: string): Promise<Platform[]> {
    const platforms = await this.prisma.platform.findMany({
      where: { isActive: true },
      include: {
        credentials: userId ? {
          where: { userId },
          select: {
            id: true,
            status: true,
            lastValidated: true,
          },
        } : false,
      },
    });

    return platforms.map(platform => ({
      ...platform,
      connected: platform.credentials?.length > 0 && 
                 platform.credentials[0].status === 'active',
    }));
  }

  async findById(id: string): Promise<Platform | null> {
    return this.prisma.platform.findUnique({
      where: { id },
    });
  }

  async connect(dto: ConnectPlatformDto, userId: string): Promise<Platform> {
    const platform = await this.findById(dto.platformId);
    if (!platform) {
      throw new Error('Platform not found');
    }

    // Encrypt credentials
    const encryptedCredentials = await this.crypto.encrypt(
      JSON.stringify(dto.credentials)
    );

    // Test connection first
    const testResult = await this.testPlatformConnection(
      platform,
      dto.credentials
    );

    if (!testResult.success) {
      throw new Error(`Connection failed: ${testResult.error}`);
    }

    // Store credentials
    const credential = await this.prisma.platformCredential.upsert({
      where: {
        platformId_userId: {
          platformId: dto.platformId,
          userId,
        },
      },
      update: {
        credentials: encryptedCredentials.encrypted,
        credentialsIv: encryptedCredentials.iv,
        status: 'active',
        lastValidated: new Date(),
      },
      create: {
        platformId: dto.platformId,
        userId,
        credentials: encryptedCredentials.encrypted,
        credentialsIv: encryptedCredentials.iv,
        status: 'active',
        lastValidated: new Date(),
      },
    });

    // Emit event
    await this.eventBus.publish({
      type: 'platform.connected',
      payload: {
        platformId: platform.id,
        userId,
        timestamp: new Date(),
      },
    });

    // Schedule validation job
    await this.queue.add('validate-platform-connection', {
      credentialId: credential.id,
    }, {
      delay: 24 * 60 * 60 * 1000, // 24 hours
      repeat: { every: 24 * 60 * 60 * 1000 },
    });

    return {
      ...platform,
      connected: true,
    };
  }

  async disconnect(platformId: string, userId: string): Promise<void> {
    const credential = await this.prisma.platformCredential.findUnique({
      where: {
        platformId_userId: {
          platformId,
          userId,
        },
      },
    });

    if (!credential) {
      throw new Error('Platform not connected');
    }

    // Update status
    await this.prisma.platformCredential.update({
      where: { id: credential.id },
      data: { status: 'disconnected' },
    });

    // Cancel validation jobs
    await this.queue.removeRepeatable('validate-platform-connection', {
      credentialId: credential.id,
    });

    // Emit event
    await this.eventBus.publish({
      type: 'platform.disconnected',
      payload: {
        platformId,
        userId,
        timestamp: new Date(),
      },
    });
  }

  async testConnection(
    platformId: string,
    userId: string
  ): Promise<TestConnectionResult> {
    const platform = await this.findById(platformId);
    if (!platform) {
      throw new Error('Platform not found');
    }

    const credential = await this.getDecryptedCredentials(platformId, userId);
    if (!credential) {
      throw new Error('Platform not connected');
    }

    return this.testPlatformConnection(platform, credential);
  }

  private async testPlatformConnection(
    platform: Platform,
    credentials: any
  ): Promise<TestConnectionResult> {
    try {
      const adapter = this.adapterFactory.create(platform, credentials);
      const isValid = await adapter.testConnection();

      return {
        success: isValid,
        timestamp: new Date(),
        details: isValid ? { status: 'Connected successfully' } : undefined,
        error: isValid ? undefined : 'Invalid credentials',
      };
    } catch (error) {
      this.logger.error('Connection test failed', { platform: platform.name, error });
      
      return {
        success: false,
        timestamp: new Date(),
        error: error.message,
        details: { errorCode: error.code },
      };
    }
  }

  async validateAllConnections(userId: string): Promise<void> {
    const credentials = await this.prisma.platformCredential.findMany({
      where: { userId, status: 'active' },
      include: { platform: true },
    });

    for (const credential of credentials) {
      try {
        const decrypted = await this.crypto.decrypt(
          credential.credentials,
          credential.credentialsIv
        );
        
        const testResult = await this.testPlatformConnection(
          credential.platform,
          JSON.parse(decrypted)
        );

        await this.prisma.platformCredential.update({
          where: { id: credential.id },
          data: {
            status: testResult.success ? 'active' : 'error',
            lastValidated: new Date(),
          },
        });
      } catch (error) {
        this.logger.error('Validation failed', { 
          credentialId: credential.id, 
          error 
        });
        
        await this.prisma.platformCredential.update({
          where: { id: credential.id },
          data: { status: 'error' },
        });
      }
    }
  }

  private async getDecryptedCredentials(
    platformId: string,
    userId: string
  ): Promise<any> {
    const credential = await this.prisma.platformCredential.findUnique({
      where: {
        platformId_userId: { platformId, userId },
      },
    });

    if (!credential) return null;

    const decrypted = await this.crypto.decrypt(
      credential.credentials,
      credential.credentialsIv
    );

    return JSON.parse(decrypted);
  }
}
```

---

## Platform Credential Management

### Secure Credential Storage

#### 1. Encryption Service
```typescript
// packages/backend/src/common/crypto/crypto.service.ts
import { injectable } from 'inversify';
import crypto from 'crypto';

interface EncryptedData {
  encrypted: Buffer;
  iv: Buffer;
}

@injectable()
export class CryptoService {
  private readonly algorithm = 'aes-256-gcm';
  private readonly keyLength = 32; // 256 bits
  private readonly ivLength = 16; // 128 bits
  private readonly tagLength = 16; // 128 bits
  private readonly saltLength = 64; // 512 bits
  private readonly iterations = 100000;

  private masterKey: Buffer;

  constructor() {
    // Load master key from environment or key management service
    this.masterKey = this.deriveMasterKey();
  }

  private deriveMasterKey(): Buffer {
    const masterPassword = process.env.MASTER_KEY;
    if (!masterPassword) {
      throw new Error('Master key not configured');
    }

    const salt = process.env.MASTER_SALT || 'default-salt';
    
    return crypto.pbkdf2Sync(
      masterPassword,
      salt,
      this.iterations,
      this.keyLength,
      'sha256'
    );
  }

  async encrypt(plaintext: string): Promise<EncryptedData> {
    // Generate random IV
    const iv = crypto.randomBytes(this.ivLength);
    
    // Create cipher
    const cipher = crypto.createCipheriv(this.algorithm, this.masterKey, iv);
    
    // Encrypt data
    const encrypted = Buffer.concat([
      cipher.update(plaintext, 'utf8'),
      cipher.final(),
    ]);
    
    // Get auth tag
    const tag = cipher.getAuthTag();
    
    // Combine encrypted data and auth tag
    const combined = Buffer.concat([encrypted, tag]);
    
    return {
      encrypted: combined,
      iv,
    };
  }

  async decrypt(encrypted: Buffer, iv: Buffer): Promise<string> {
    // Extract auth tag from end of encrypted data
    const tag = encrypted.slice(-this.tagLength);
    const data = encrypted.slice(0, -this.tagLength);
    
    // Create decipher
    const decipher = crypto.createDecipheriv(this.algorithm, this.masterKey, iv);
    decipher.setAuthTag(tag);
    
    // Decrypt data
    const decrypted = Buffer.concat([
      decipher.update(data),
      decipher.final(),
    ]);
    
    return decrypted.toString('utf8');
  }

  async rotateKey(oldKey: Buffer, newKey: Buffer): Promise<void> {
    // Re-encrypt all credentials with new key
    // This would be implemented as a background job
    this.masterKey = newKey;
  }

  generateRandomKey(): Buffer {
    return crypto.randomBytes(this.keyLength);
  }

  hashPassword(password: string): string {
    const salt = crypto.randomBytes(this.saltLength);
    const hash = crypto.pbkdf2Sync(
      password,
      salt,
      this.iterations,
      this.keyLength,
      'sha256'
    );
    
    return salt.toString('hex') + ':' + hash.toString('hex');
  }

  verifyPassword(password: string, storedHash: string): boolean {
    const [saltHex, hashHex] = storedHash.split(':');
    const salt = Buffer.from(saltHex, 'hex');
    const storedHashBuffer = Buffer.from(hashHex, 'hex');
    
    const hash = crypto.pbkdf2Sync(
      password,
      salt,
      this.iterations,
      this.keyLength,
      'sha256'
    );
    
    return crypto.timingSafeEqual(hash, storedHashBuffer);
  }
}
```

#### 2. Platform Credential UI Component
```typescript
// packages/frontend/src/components/PlatformCredentials/PlatformCredentials.tsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Eye, EyeOff, Shield, AlertTriangle } from 'lucide-react';
import { Platform, PlatformType } from '@shared/types';
import { useConnectPlatform, useTestConnection } from '@/hooks/usePlatforms';
import { Alert } from '@/components/ui/Alert';

interface PlatformCredentialsProps {
  platform: Platform;
  onSuccess?: () => void;
  onCancel?: () => void;
}

// Platform-specific credential schemas
const credentialSchemas = {
  meta: z.object({
    appId: z.string().min(1, 'App ID is required'),
    appSecret: z.string().min(1, 'App Secret is required'),
    accessToken: z.string().min(1, 'Access Token is required'),
    adAccountId: z.string().min(1, 'Ad Account ID is required'),
  }),
  google: z.object({
    clientId: z.string().min(1, 'Client ID is required'),
    clientSecret: z.string().min(1, 'Client Secret is required'),
    developerToken: z.string().min(1, 'Developer Token is required'),
    refreshToken: z.string().min(1, 'Refresh Token is required'),
    customerId: z.string().regex(/^\d{10}$/, 'Customer ID must be 10 digits'),
    managerAccountId: z.string().optional(),
  }),
  linkedin: z.object({
    clientId: z.string().min(1, 'Client ID is required'),
    clientSecret: z.string().min(1, 'Client Secret is required'),
    accessToken: z.string().min(1, 'Access Token is required'),
    organizationId: z.string().min(1, 'Organization ID is required'),
  }),
  tiktok: z.object({
    appId: z.string().min(1, 'App ID is required'),
    appSecret: z.string().min(1, 'App Secret is required'),
    accessToken: z.string().min(1, 'Access Token is required'),
    advertiserId: z.string().min(1, 'Advertiser ID is required'),
  }),
  netflix: z.object({
    partnerId: z.string().min(1, 'Partner ID is required'),
    apiKey: z.string().min(1, 'API Key is required'),
    apiSecret: z.string().min(1, 'API Secret is required'),
  }),
  ttd: z.object({
    partnerId: z.string().min(1, 'Partner ID is required'),
    apiToken: z.string().min(1, 'API Token is required'),
    advertiserId: z.string().min(1, 'Advertiser ID is required'),
  }),
};

export const PlatformCredentials: React.FC<PlatformCredentialsProps> = ({
  platform,
  onSuccess,
  onCancel,
}) => {
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});
  const [testResult, setTestResult] = useState<any>(null);

  const connectPlatform = useConnectPlatform();
  const testConnection = useTestConnection();

  const schema = credentialSchemas[platform.code as keyof typeof credentialSchemas];
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: any) => {
    try {
      // Test connection first
      const test = await testConnection.mutateAsync({
        platformId: platform.id,
        credentials: data,
      });

      if (!test.success) {
        setTestResult(test);
        return;
      }

      // Connect platform
      await connectPlatform.mutateAsync({
        platformId: platform.id,
        credentials: data,
      });

      onSuccess?.();
    } catch (error) {
      console.error('Failed to connect platform:', error);
    }
  };

  const toggleShowSecret = (field: string) => {
    setShowSecrets(prev => ({
      ...prev,
      [field]: !prev[field],
    }));
  };

  const getFieldConfig = (platformCode: string) => {
    const configs: Record<string, any> = {
      meta: [
        { name: 'appId', label: 'App ID', type: 'text', help: 'Found in your Facebook App settings' },
        { name: 'appSecret', label: 'App Secret', type: 'password', help: 'Keep this secret!' },
        { name: 'accessToken', label: 'Access Token', type: 'password', help: 'Generate from Graph API Explorer' },
        { name: 'adAccountId', label: 'Ad Account ID', type: 'text', help: 'Format: act_123456789' },
      ],
      google: [
        { name: 'clientId', label: 'OAuth Client ID', type: 'text' },
        { name: 'clientSecret', label: 'OAuth Client Secret', type: 'password' },
        { name: 'developerToken', label: 'Developer Token', type: 'password' },
        { name: 'refreshToken', label: 'Refresh Token', type: 'password' },
        { name: 'customerId', label: 'Customer ID', type: 'text', help: '10-digit customer ID' },
        { name: 'managerAccountId', label: 'Manager Account ID', type: 'text', help: 'Optional MCC ID' },
      ],
      // ... other platforms
    };

    return configs[platformCode] || [];
  };

  const fields = getFieldConfig(platform.code);

  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <h3 className="text-xl font-semibold mb-2">
          Connect to {platform.name}
        </h3>
        <p className="text-gray-600">
          Enter your {platform.name} credentials to enable audience distribution.
        </p>
      </div>

      <Alert variant="info" className="mb-6">
        <Shield className="w-5 h-5" />
        <div>
          <p className="font-medium">Your credentials are encrypted</p>
          <p className="text-sm mt-1">
            We use industry-standard encryption to protect your API credentials.
            They are never stored in plain text.
          </p>
        </div>
      </Alert>

      {testResult && !testResult.success && (
        <Alert variant="error" className="mb-6">
          <AlertTriangle className="w-5 h-5" />
          <div>
            <p className="font-medium">Connection test failed</p>
            <p className="text-sm mt-1">{testResult.error}</p>
          </div>
        </Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {fields.map((field: any) => (
          <div key={field.name}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
            </label>
            <div className="relative">
              <input
                {...register(field.name)}
                type={field.type === 'password' && !showSecrets[field.name] 
                  ? 'password' 
                  : 'text'}
                className={clsx(
                  'input-field pr-10',
                  errors[field.name] && 'input-error'
                )}
                placeholder={field.placeholder}
              />
              {field.type === 'password' && (
                <button
                  type="button"
                  onClick={() => toggleShowSecret(field.name)}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showSecrets[field.name] ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              )}
            </div>
            {field.help && (
              <p className="text-xs text-gray-500 mt-1">{field.help}</p>
            )}
            {errors[field.name] && (
              <p className="text-sm text-red-600 mt-1">
                {errors[field.name]?.message}
              </p>
            )}
          </div>
        ))}

        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary flex-1"
          >
            {isSubmitting ? 'Connecting...' : 'Connect Platform'}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="btn-secondary"
          >
            Cancel
          </button>
        </div>
      </form>

      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium text-gray-700 mb-2">
          Where to find these credentials:
        </h4>
        <PlatformInstructions platform={platform} />
      </div>
    </div>
  );
};

// Platform-specific instructions component
const PlatformInstructions: React.FC<{ platform: Platform }> = ({ platform }) => {
  const instructions: Record<string, JSX.Element> = {
    meta: (
      <ol className="text-sm text-gray-600 space-y-2">
        <li>1. Go to <a href="https://developers.facebook.com/apps" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Facebook Developers</a></li>
        <li>2. Select your app or create a new one</li>
        <li>3. Find App ID and App Secret in Settings → Basic</li>
        <li>4. Generate Access Token using Graph API Explorer</li>
        <li>5. Get Ad Account ID from Facebook Ads Manager</li>
      </ol>
    ),
    google: (
      <ol className="text-sm text-gray-600 space-y-2">
        <li>1. Visit <a href="https://console.cloud.google.com" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Google Cloud Console</a></li>
        <li>2. Create OAuth 2.0 credentials in APIs & Services</li>
        <li>3. Get Developer Token from Google Ads API Center</li>
        <li>4. Use OAuth playground to generate Refresh Token</li>
        <li>5. Find Customer ID in Google Ads account settings</li>
      </ol>
    ),
    // ... other platforms
  };

  return instructions[platform.code] || <p className="text-sm text-gray-600">Documentation coming soon.</p>;
};
```

This completes Part 5 of the implementation guide, covering the Platform Integration Framework and Credential Management. The guide continues with advanced integration topics.