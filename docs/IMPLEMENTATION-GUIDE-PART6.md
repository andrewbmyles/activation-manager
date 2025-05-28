# Activation Manager Implementation Guide - Part 6: Audience Storage and Management

## Table of Contents
1. [Database Architecture for Audience Storage](#database-architecture)
2. [Audience Data Models](#audience-data-models)
3. [Storage Strategies](#storage-strategies)
4. [Caching Layer](#caching-layer)
5. [Data Partitioning](#data-partitioning)
6. [Audience Versioning](#audience-versioning)
7. [Data Retention Policies](#data-retention)

## 1. Database Architecture for Audience Storage

### PostgreSQL Schema Design

```sql
-- Audience metadata table
CREATE TABLE audiences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL CHECK (type IN ('1st-party', '3rd-party', 'clean-room')),
    subtype VARCHAR(50),
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    size BIGINT DEFAULT 0,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    activated_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    CONSTRAINT unique_audience_name_per_org UNIQUE (organization_id, name)
);

-- Audience segments for large audiences
CREATE TABLE audience_segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audience_id UUID NOT NULL REFERENCES audiences(id) ON DELETE CASCADE,
    segment_number INT NOT NULL,
    total_segments INT NOT NULL,
    size BIGINT NOT NULL,
    data_location VARCHAR(500) NOT NULL, -- S3 path or file location
    checksum VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_segment UNIQUE (audience_id, segment_number)
);

-- Audience members table for smaller audiences
CREATE TABLE audience_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audience_id UUID NOT NULL REFERENCES audiences(id) ON DELETE CASCADE,
    identifier_type VARCHAR(50) NOT NULL,
    identifier_value VARCHAR(500) NOT NULL,
    attributes JSONB DEFAULT '{}',
    added_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    CONSTRAINT unique_member UNIQUE (audience_id, identifier_type, identifier_value)
);

-- Audience rules for dynamic audiences
CREATE TABLE audience_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audience_id UUID NOT NULL REFERENCES audiences(id) ON DELETE CASCADE,
    rule_order INT NOT NULL,
    variable_id VARCHAR(100) NOT NULL,
    operator VARCHAR(50) NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audience history for versioning
CREATE TABLE audience_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audience_id UUID NOT NULL REFERENCES audiences(id),
    version INT NOT NULL,
    change_type VARCHAR(50) NOT NULL,
    change_description TEXT,
    previous_state JSONB,
    new_state JSONB,
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_version UNIQUE (audience_id, version)
);

-- Create indexes for performance
CREATE INDEX idx_audiences_org_status ON audiences(organization_id, status);
CREATE INDEX idx_audiences_created_at ON audiences(created_at DESC);
CREATE INDEX idx_audience_members_audience ON audience_members(audience_id);
CREATE INDEX idx_audience_members_identifier ON audience_members(identifier_type, identifier_value);
CREATE INDEX idx_audience_segments_audience ON audience_segments(audience_id);
CREATE INDEX idx_audience_rules_audience ON audience_rules(audience_id, rule_order);
```

### MongoDB Alternative for Flexible Storage

```typescript
// MongoDB schema for audiences with flexible member storage
const audienceSchema = new Schema({
  _id: { type: String, default: () => new ObjectId().toString() },
  organizationId: { type: String, required: true, index: true },
  name: { type: String, required: true },
  description: String,
  type: { 
    type: String, 
    enum: ['1st-party', '3rd-party', 'clean-room'],
    required: true 
  },
  subtype: String,
  status: { 
    type: String, 
    enum: ['draft', 'active', 'paused', 'archived'],
    default: 'draft' 
  },
  rules: [{
    variableId: String,
    operator: String,
    value: Schema.Types.Mixed
  }],
  members: {
    count: { type: Number, default: 0 },
    storageType: { 
      type: String, 
      enum: ['inline', 'segmented', 'external'] 
    },
    segments: [{
      segmentNumber: Number,
      size: Number,
      location: String,
      checksum: String
    }]
  },
  metadata: {
    createdBy: String,
    createdAt: { type: Date, default: Date.now },
    updatedAt: { type: Date, default: Date.now },
    activatedAt: Date,
    expiresAt: Date,
    tags: [String],
    customAttributes: Schema.Types.Mixed
  },
  history: [{
    version: Number,
    changeType: String,
    changeDescription: String,
    changedBy: String,
    changedAt: Date,
    snapshot: Schema.Types.Mixed
  }]
});

// Compound indexes for performance
audienceSchema.index({ organizationId: 1, name: 1 }, { unique: true });
audienceSchema.index({ organizationId: 1, status: 1, createdAt: -1 });
audienceSchema.index({ 'metadata.tags': 1 });
audienceSchema.index({ type: 1, subtype: 1 });
```

## 2. Audience Data Models

### TypeScript Models

```typescript
// Core audience model
export interface Audience {
  id: string;
  organizationId: string;
  name: string;
  description?: string;
  type: AudienceType;
  subtype?: AudienceSubtype;
  status: AudienceStatus;
  size: number;
  rules: AudienceRule[];
  metadata: AudienceMetadata;
  storage: AudienceStorage;
  createdAt: Date;
  updatedAt: Date;
}

export enum AudienceType {
  FIRST_PARTY = '1st-party',
  THIRD_PARTY = '3rd-party',
  CLEAN_ROOM = 'clean-room'
}

export enum AudienceStatus {
  DRAFT = 'draft',
  PROCESSING = 'processing',
  ACTIVE = 'active',
  PAUSED = 'paused',
  ARCHIVED = 'archived',
  ERROR = 'error'
}

export interface AudienceRule {
  id: string;
  variableId: string;
  operator: RuleOperator;
  value: any;
  order: number;
}

export interface AudienceMetadata {
  createdBy: string;
  activatedAt?: Date;
  expiresAt?: Date;
  tags: string[];
  customAttributes: Record<string, any>;
  qualityScore?: number;
  matchRate?: number;
}

export interface AudienceStorage {
  type: StorageType;
  location?: string;
  segments?: AudienceSegment[];
  compression?: CompressionType;
  encryption?: EncryptionConfig;
}

export enum StorageType {
  DATABASE = 'database',      // Small audiences < 100k
  SEGMENTED = 'segmented',    // Medium audiences 100k-10M
  EXTERNAL = 'external'       // Large audiences > 10M
}

export interface AudienceSegment {
  id: string;
  segmentNumber: number;
  totalSegments: number;
  size: number;
  location: string;
  checksum: string;
  createdAt: Date;
}

// Audience member model
export interface AudienceMember {
  id: string;
  audienceId: string;
  identifierType: IdentifierType;
  identifierValue: string;
  attributes: Record<string, any>;
  addedAt: Date;
  expiresAt?: Date;
  score?: number;
}

export enum IdentifierType {
  EMAIL = 'email',
  PHONE = 'phone',
  RAMP_ID = 'ramp_id',
  UID2 = 'uid2',
  MAID = 'maid',
  COOKIE_ID = 'cookie_id',
  CUSTOMER_ID = 'customer_id'
}
```

### Repository Pattern Implementation

```typescript
// Audience repository interface
export interface IAudienceRepository {
  create(audience: CreateAudienceDto): Promise<Audience>;
  findById(id: string): Promise<Audience | null>;
  findByOrganization(organizationId: string, options?: FindOptions): Promise<PaginatedResult<Audience>>;
  update(id: string, updates: UpdateAudienceDto): Promise<Audience>;
  delete(id: string): Promise<void>;
  addMembers(audienceId: string, members: AudienceMember[]): Promise<void>;
  removeMembers(audienceId: string, memberIds: string[]): Promise<void>;
  getMembers(audienceId: string, options?: FindOptions): Promise<PaginatedResult<AudienceMember>>;
  createVersion(audienceId: string, description: string): Promise<AudienceVersion>;
  getVersionHistory(audienceId: string): Promise<AudienceVersion[]>;
}

// PostgreSQL implementation
export class PostgresAudienceRepository implements IAudienceRepository {
  constructor(private prisma: PrismaClient) {}

  async create(dto: CreateAudienceDto): Promise<Audience> {
    const audience = await this.prisma.audience.create({
      data: {
        name: dto.name,
        description: dto.description,
        type: dto.type,
        subtype: dto.subtype,
        organizationId: dto.organizationId,
        createdBy: dto.userId,
        rules: {
          create: dto.rules.map((rule, index) => ({
            variableId: rule.variableId,
            operator: rule.operator,
            value: rule.value,
            ruleOrder: index
          }))
        }
      },
      include: {
        rules: true,
        segments: true
      }
    });

    // Create initial version
    await this.createVersion(audience.id, 'Initial creation');

    return this.mapToAudience(audience);
  }

  async addMembers(audienceId: string, members: AudienceMember[]): Promise<void> {
    const audience = await this.findById(audienceId);
    if (!audience) throw new Error('Audience not found');

    // Determine storage strategy based on size
    const newSize = audience.size + members.length;
    
    if (newSize < 100000) {
      // Store in database
      await this.addMembersToDatabase(audienceId, members);
    } else if (newSize < 10000000) {
      // Use segmented storage
      await this.addMembersSegmented(audienceId, members);
    } else {
      // Use external storage (S3)
      await this.addMembersExternal(audienceId, members);
    }

    // Update audience size
    await this.prisma.audience.update({
      where: { id: audienceId },
      data: { 
        size: newSize,
        updatedAt: new Date()
      }
    });
  }

  private async addMembersToDatabase(
    audienceId: string, 
    members: AudienceMember[]
  ): Promise<void> {
    // Batch insert with conflict handling
    const chunks = this.chunkArray(members, 1000);
    
    for (const chunk of chunks) {
      await this.prisma.$executeRaw`
        INSERT INTO audience_members (
          audience_id, identifier_type, identifier_value, attributes, added_at
        )
        SELECT 
          ${audienceId},
          ${Prisma.sql`unnest(${chunk.map(m => m.identifierType)}::text[])`},
          ${Prisma.sql`unnest(${chunk.map(m => m.identifierValue)}::text[])`},
          ${Prisma.sql`unnest(${chunk.map(m => JSON.stringify(m.attributes))}::jsonb[])`},
          NOW()
        ON CONFLICT (audience_id, identifier_type, identifier_value) 
        DO UPDATE SET
          attributes = EXCLUDED.attributes,
          added_at = EXCLUDED.added_at
      `;
    }
  }

  private async addMembersSegmented(
    audienceId: string,
    members: AudienceMember[]
  ): Promise<void> {
    // Group members into segments of 1M each
    const segmentSize = 1000000;
    const segments = this.chunkArray(members, segmentSize);
    
    // Get current segment info
    const lastSegment = await this.prisma.audienceSegment.findFirst({
      where: { audienceId },
      orderBy: { segmentNumber: 'desc' }
    });

    let currentSegmentNumber = lastSegment?.segmentNumber || 0;

    for (const segment of segments) {
      currentSegmentNumber++;
      
      // Serialize segment data
      const segmentData = Buffer.from(
        JSON.stringify(segment),
        'utf-8'
      );
      
      // Compress data
      const compressed = await this.compressData(segmentData);
      
      // Calculate checksum
      const checksum = crypto
        .createHash('sha256')
        .update(compressed)
        .digest('hex');
      
      // Upload to S3
      const location = await this.uploadToS3(
        `audiences/${audienceId}/segment-${currentSegmentNumber}.gz`,
        compressed
      );
      
      // Save segment metadata
      await this.prisma.audienceSegment.create({
        data: {
          audienceId,
          segmentNumber: currentSegmentNumber,
          totalSegments: segments.length,
          size: segment.length,
          dataLocation: location,
          checksum
        }
      });
    }
  }

  private async addMembersExternal(
    audienceId: string,
    members: AudienceMember[]
  ): Promise<void> {
    // For very large audiences, stream directly to S3
    const stream = new PassThrough();
    const gzip = zlib.createGzip();
    
    // Start upload
    const uploadPromise = this.s3Client.upload({
      Bucket: process.env.S3_BUCKET!,
      Key: `audiences/${audienceId}/members-${Date.now()}.ndjson.gz`,
      Body: stream.pipe(gzip),
      ContentType: 'application/x-ndjson',
      ContentEncoding: 'gzip'
    }).promise();

    // Stream members as NDJSON
    for (const member of members) {
      stream.write(JSON.stringify(member) + '\n');
    }
    stream.end();

    const result = await uploadPromise;

    // Update audience storage info
    await this.prisma.audience.update({
      where: { id: audienceId },
      data: {
        metadata: {
          update: {
            storageType: 'external',
            storageLocation: result.Location
          }
        }
      }
    });
  }

  private chunkArray<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }

  private async compressData(data: Buffer): Promise<Buffer> {
    return new Promise((resolve, reject) => {
      zlib.gzip(data, (err, compressed) => {
        if (err) reject(err);
        else resolve(compressed);
      });
    });
  }
}
```

## 3. Storage Strategies

### Hybrid Storage Approach

```typescript
// Storage strategy factory
export class AudienceStorageStrategy {
  private strategies: Map<StorageType, IStorageStrategy>;

  constructor(
    private config: StorageConfig,
    private s3Client: AWS.S3,
    private redisClient: Redis
  ) {
    this.strategies = new Map([
      [StorageType.DATABASE, new DatabaseStorageStrategy(config)],
      [StorageType.SEGMENTED, new SegmentedStorageStrategy(config, s3Client)],
      [StorageType.EXTERNAL, new ExternalStorageStrategy(config, s3Client)]
    ]);
  }

  getStrategy(size: number): IStorageStrategy {
    if (size < this.config.databaseThreshold) {
      return this.strategies.get(StorageType.DATABASE)!;
    } else if (size < this.config.segmentedThreshold) {
      return this.strategies.get(StorageType.SEGMENTED)!;
    } else {
      return this.strategies.get(StorageType.EXTERNAL)!;
    }
  }
}

// Storage strategy interface
export interface IStorageStrategy {
  store(audienceId: string, members: AudienceMember[]): Promise<StorageResult>;
  retrieve(audienceId: string, options?: RetrieveOptions): Promise<AudienceMember[]>;
  delete(audienceId: string): Promise<void>;
  getStorageInfo(audienceId: string): Promise<StorageInfo>;
}

// Database storage for small audiences
export class DatabaseStorageStrategy implements IStorageStrategy {
  constructor(private config: StorageConfig) {}

  async store(
    audienceId: string, 
    members: AudienceMember[]
  ): Promise<StorageResult> {
    const startTime = Date.now();
    
    // Use bulk insert with batching
    const batchSize = 5000;
    const batches = Math.ceil(members.length / batchSize);
    
    for (let i = 0; i < batches; i++) {
      const batch = members.slice(i * batchSize, (i + 1) * batchSize);
      
      await this.bulkInsert(audienceId, batch);
      
      // Progress tracking
      if (this.config.onProgress) {
        this.config.onProgress({
          audienceId,
          processed: Math.min((i + 1) * batchSize, members.length),
          total: members.length,
          percentage: Math.round(((i + 1) / batches) * 100)
        });
      }
    }

    return {
      storageType: StorageType.DATABASE,
      duration: Date.now() - startTime,
      recordsStored: members.length,
      location: 'postgresql://audience_members'
    };
  }

  async retrieve(
    audienceId: string,
    options: RetrieveOptions = {}
  ): Promise<AudienceMember[]> {
    const { limit = 1000000, offset = 0, filters = {} } = options;

    const query = this.buildRetrieveQuery(audienceId, filters);
    
    const members = await prisma.$queryRaw<AudienceMember[]>`
      ${query}
      LIMIT ${limit}
      OFFSET ${offset}
    `;

    return members;
  }

  private buildRetrieveQuery(
    audienceId: string, 
    filters: Record<string, any>
  ): Prisma.Sql {
    let query = Prisma.sql`
      SELECT 
        id,
        identifier_type as "identifierType",
        identifier_value as "identifierValue",
        attributes,
        added_at as "addedAt",
        expires_at as "expiresAt"
      FROM audience_members
      WHERE audience_id = ${audienceId}
    `;

    // Add filters
    if (filters.identifierType) {
      query = Prisma.sql`${query} AND identifier_type = ${filters.identifierType}`;
    }

    if (filters.addedAfter) {
      query = Prisma.sql`${query} AND added_at > ${filters.addedAfter}`;
    }

    if (filters.notExpired) {
      query = Prisma.sql`${query} AND (expires_at IS NULL OR expires_at > NOW())`;
    }

    return query;
  }
}

// Segmented storage for medium audiences
export class SegmentedStorageStrategy implements IStorageStrategy {
  constructor(
    private config: StorageConfig,
    private s3Client: AWS.S3
  ) {}

  async store(
    audienceId: string,
    members: AudienceMember[]
  ): Promise<StorageResult> {
    const segmentSize = this.config.segmentSize || 1000000;
    const segments = this.createSegments(members, segmentSize);
    const results: SegmentUploadResult[] = [];

    // Parallel upload with concurrency control
    const uploadQueue = new PQueue({ concurrency: 5 });

    for (let i = 0; i < segments.length; i++) {
      uploadQueue.add(async () => {
        const result = await this.uploadSegment(
          audienceId,
          segments[i],
          i,
          segments.length
        );
        results.push(result);
      });
    }

    await uploadQueue.onIdle();

    // Store segment metadata in database
    await this.storeSegmentMetadata(audienceId, results);

    return {
      storageType: StorageType.SEGMENTED,
      duration: Date.now() - startTime,
      recordsStored: members.length,
      segments: results.length,
      location: `s3://${this.config.bucket}/audiences/${audienceId}/`
    };
  }

  private async uploadSegment(
    audienceId: string,
    segment: AudienceMember[],
    segmentNumber: number,
    totalSegments: number
  ): Promise<SegmentUploadResult> {
    // Convert to NDJSON format
    const ndjson = segment
      .map(member => JSON.stringify(member))
      .join('\n');

    // Compress
    const compressed = await this.compress(Buffer.from(ndjson));

    // Calculate checksum
    const checksum = crypto
      .createHash('sha256')
      .update(compressed)
      .digest('hex');

    // Upload to S3
    const key = `audiences/${audienceId}/segment-${segmentNumber}.ndjson.gz`;
    
    await this.s3Client.putObject({
      Bucket: this.config.bucket,
      Key: key,
      Body: compressed,
      ContentType: 'application/x-ndjson',
      ContentEncoding: 'gzip',
      Metadata: {
        'audience-id': audienceId,
        'segment-number': segmentNumber.toString(),
        'total-segments': totalSegments.toString(),
        'record-count': segment.length.toString(),
        'checksum': checksum
      }
    }).promise();

    return {
      segmentNumber,
      size: segment.length,
      compressedSize: compressed.length,
      location: `s3://${this.config.bucket}/${key}`,
      checksum
    };
  }

  async retrieve(
    audienceId: string,
    options: RetrieveOptions = {}
  ): Promise<AudienceMember[]> {
    // Get segment metadata
    const segments = await this.getSegmentMetadata(audienceId);
    
    if (segments.length === 0) {
      return [];
    }

    // Determine which segments to load based on options
    const segmentsToLoad = this.selectSegments(segments, options);
    
    // Parallel download with streaming
    const members: AudienceMember[] = [];
    const downloadQueue = new PQueue({ concurrency: 3 });

    for (const segment of segmentsToLoad) {
      downloadQueue.add(async () => {
        const segmentMembers = await this.downloadSegment(segment);
        members.push(...segmentMembers);
      });
    }

    await downloadQueue.onIdle();

    // Apply any post-retrieval filters
    return this.applyFilters(members, options.filters || {});
  }

  private async downloadSegment(
    segment: SegmentMetadata
  ): Promise<AudienceMember[]> {
    const params = {
      Bucket: this.config.bucket,
      Key: segment.location.replace(`s3://${this.config.bucket}/`, '')
    };

    const stream = this.s3Client.getObject(params).createReadStream();
    const gunzip = zlib.createGunzip();
    const members: AudienceMember[] = [];

    return new Promise((resolve, reject) => {
      stream
        .pipe(gunzip)
        .pipe(split2())
        .on('data', (line: string) => {
          if (line.trim()) {
            members.push(JSON.parse(line));
          }
        })
        .on('end', () => resolve(members))
        .on('error', reject);
    });
  }
}
```

## 4. Caching Layer

### Redis-based Caching Strategy

```typescript
// Audience cache service
export class AudienceCacheService {
  private readonly TTL = {
    METADATA: 3600,        // 1 hour
    MEMBERS: 1800,         // 30 minutes
    SUMMARY: 7200,         // 2 hours
    SEGMENT_INFO: 3600     // 1 hour
  };

  constructor(
    private redis: Redis,
    private config: CacheConfig
  ) {}

  // Cache audience metadata
  async cacheAudienceMetadata(audience: Audience): Promise<void> {
    const key = this.getMetadataKey(audience.id);
    
    await this.redis.setex(
      key,
      this.TTL.METADATA,
      JSON.stringify(audience)
    );

    // Also cache in organization index
    await this.redis.sadd(
      this.getOrgAudiencesKey(audience.organizationId),
      audience.id
    );
  }

  // Cache audience members with pagination
  async cacheMembers(
    audienceId: string,
    members: AudienceMember[],
    page: number,
    pageSize: number
  ): Promise<void> {
    const key = this.getMembersKey(audienceId, page, pageSize);
    
    // Use Redis sorted set for efficient pagination
    const pipeline = this.redis.pipeline();
    
    members.forEach((member, index) => {
      const score = (page - 1) * pageSize + index;
      pipeline.zadd(
        key,
        score,
        JSON.stringify(member)
      );
    });

    pipeline.expire(key, this.TTL.MEMBERS);
    await pipeline.exec();
  }

  // Get cached members
  async getCachedMembers(
    audienceId: string,
    page: number,
    pageSize: number
  ): Promise<AudienceMember[] | null> {
    const key = this.getMembersKey(audienceId, page, pageSize);
    
    const start = (page - 1) * pageSize;
    const end = start + pageSize - 1;
    
    const cached = await this.redis.zrange(key, start, end);
    
    if (!cached || cached.length === 0) {
      return null;
    }

    return cached.map(item => JSON.parse(item));
  }

  // Cache audience summary
  async cacheAudienceSummary(
    audienceId: string,
    summary: AudienceSummary
  ): Promise<void> {
    const key = this.getSummaryKey(audienceId);
    
    await this.redis.hset(key, {
      size: summary.size.toString(),
      uniqueIdentifiers: summary.uniqueIdentifiers.toString(),
      lastUpdated: summary.lastUpdated.toISOString(),
      topAttributes: JSON.stringify(summary.topAttributes),
      identifierBreakdown: JSON.stringify(summary.identifierBreakdown)
    });

    await this.redis.expire(key, this.TTL.SUMMARY);
  }

  // Invalidate cache
  async invalidateAudience(audienceId: string): Promise<void> {
    const pattern = `audience:${audienceId}:*`;
    const keys = await this.redis.keys(pattern);
    
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }

  // Warm cache for frequently accessed audiences
  async warmCache(audienceIds: string[]): Promise<void> {
    const warmupQueue = new PQueue({ concurrency: 5 });

    for (const audienceId of audienceIds) {
      warmupQueue.add(async () => {
        try {
          // Fetch and cache metadata
          const audience = await this.audienceRepo.findById(audienceId);
          if (audience) {
            await this.cacheAudienceMetadata(audience);
            
            // Cache first page of members
            const members = await this.audienceRepo.getMembers(
              audienceId,
              { limit: 100, offset: 0 }
            );
            
            if (members.data.length > 0) {
              await this.cacheMembers(audienceId, members.data, 1, 100);
            }

            // Cache summary
            const summary = await this.calculateSummary(audienceId);
            await this.cacheAudienceSummary(audienceId, summary);
          }
        } catch (error) {
          logger.error(`Failed to warm cache for audience ${audienceId}`, error);
        }
      });
    }

    await warmupQueue.onIdle();
  }

  // Cache key generators
  private getMetadataKey(audienceId: string): string {
    return `audience:${audienceId}:metadata`;
  }

  private getMembersKey(audienceId: string, page: number, pageSize: number): string {
    return `audience:${audienceId}:members:${page}:${pageSize}`;
  }

  private getSummaryKey(audienceId: string): string {
    return `audience:${audienceId}:summary`;
  }

  private getOrgAudiencesKey(organizationId: string): string {
    return `org:${organizationId}:audiences`;
  }
}

// Cache-aside pattern implementation
export class CachedAudienceRepository implements IAudienceRepository {
  constructor(
    private baseRepo: IAudienceRepository,
    private cache: AudienceCacheService
  ) {}

  async findById(id: string): Promise<Audience | null> {
    // Try cache first
    const cached = await this.cache.getAudienceMetadata(id);
    if (cached) {
      return cached;
    }

    // Load from database
    const audience = await this.baseRepo.findById(id);
    
    if (audience) {
      // Cache for next time
      await this.cache.cacheAudienceMetadata(audience);
    }

    return audience;
  }

  async getMembers(
    audienceId: string,
    options?: FindOptions
  ): Promise<PaginatedResult<AudienceMember>> {
    const page = options?.page || 1;
    const pageSize = options?.limit || 100;

    // Try cache first
    const cachedMembers = await this.cache.getCachedMembers(
      audienceId,
      page,
      pageSize
    );

    if (cachedMembers) {
      return {
        data: cachedMembers,
        page,
        pageSize,
        total: await this.baseRepo.getMemberCount(audienceId)
      };
    }

    // Load from database
    const result = await this.baseRepo.getMembers(audienceId, options);

    // Cache for next time
    if (result.data.length > 0) {
      await this.cache.cacheMembers(
        audienceId,
        result.data,
        page,
        pageSize
      );
    }

    return result;
  }

  async update(id: string, updates: UpdateAudienceDto): Promise<Audience> {
    // Update in database
    const audience = await this.baseRepo.update(id, updates);

    // Invalidate cache
    await this.cache.invalidateAudience(id);

    // Cache new version
    await this.cache.cacheAudienceMetadata(audience);

    return audience;
  }
}
```

## 5. Data Partitioning

### Time-based Partitioning

```sql
-- Create partitioned table for audience members
CREATE TABLE audience_members_partitioned (
    id UUID DEFAULT gen_random_uuid(),
    audience_id UUID NOT NULL,
    identifier_type VARCHAR(50) NOT NULL,
    identifier_value VARCHAR(500) NOT NULL,
    attributes JSONB DEFAULT '{}',
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    PRIMARY KEY (id, added_at)
) PARTITION BY RANGE (added_at);

-- Create monthly partitions
CREATE TABLE audience_members_2024_01 PARTITION OF audience_members_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE audience_members_2024_02 PARTITION OF audience_members_partitioned
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Automated partition management
CREATE OR REPLACE FUNCTION create_monthly_partition()
RETURNS void AS $$
DECLARE
    start_date date;
    end_date date;
    partition_name text;
BEGIN
    start_date := date_trunc('month', CURRENT_DATE + interval '1 month');
    end_date := start_date + interval '1 month';
    partition_name := 'audience_members_' || to_char(start_date, 'YYYY_MM');
    
    -- Check if partition exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_class 
        WHERE relname = partition_name
    ) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF audience_members_partitioned 
            FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date
        );
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Schedule partition creation
SELECT cron.schedule(
    'create-audience-partitions',
    '0 0 25 * *',  -- Run on 25th of each month
    'SELECT create_monthly_partition()'
);
```

### Hash-based Partitioning for Large Audiences

```typescript
// Hash partitioning service
export class AudiencePartitionService {
  private readonly PARTITION_COUNT = 16;

  constructor(
    private config: PartitionConfig,
    private db: Database
  ) {}

  // Get partition for a member
  getPartition(identifierValue: string): number {
    const hash = crypto
      .createHash('md5')
      .update(identifierValue)
      .digest();
    
    return hash[0] % this.PARTITION_COUNT;
  }

  // Create partitioned storage
  async createPartitionedAudience(
    audienceId: string
  ): Promise<void> {
    const baseTableName = `audience_${audienceId.replace(/-/g, '_')}`;

    // Create base partitioned table
    await this.db.execute(`
      CREATE TABLE ${baseTableName} (
        identifier_type VARCHAR(50) NOT NULL,
        identifier_value VARCHAR(500) NOT NULL,
        attributes JSONB DEFAULT '{}',
        added_at TIMESTAMPTZ DEFAULT NOW(),
        partition_key INT NOT NULL,
        PRIMARY KEY (partition_key, identifier_value)
      ) PARTITION BY LIST (partition_key)
    `);

    // Create partitions
    for (let i = 0; i < this.PARTITION_COUNT; i++) {
      await this.db.execute(`
        CREATE TABLE ${baseTableName}_p${i} 
        PARTITION OF ${baseTableName}
        FOR VALUES IN (${i})
      `);
    }

    // Create indexes on each partition
    for (let i = 0; i < this.PARTITION_COUNT; i++) {
      await this.db.execute(`
        CREATE INDEX idx_${baseTableName}_p${i}_identifier 
        ON ${baseTableName}_p${i}(identifier_value)
      `);
    }
  }

  // Bulk insert with partitioning
  async bulkInsertPartitioned(
    audienceId: string,
    members: AudienceMember[]
  ): Promise<void> {
    const baseTableName = `audience_${audienceId.replace(/-/g, '_')}`;
    
    // Group members by partition
    const partitionedMembers = new Map<number, AudienceMember[]>();
    
    for (const member of members) {
      const partition = this.getPartition(member.identifierValue);
      
      if (!partitionedMembers.has(partition)) {
        partitionedMembers.set(partition, []);
      }
      
      partitionedMembers.get(partition)!.push(member);
    }

    // Insert into each partition in parallel
    const insertQueue = new PQueue({ concurrency: 4 });

    for (const [partition, partitionMembers] of partitionedMembers) {
      insertQueue.add(async () => {
        await this.insertIntoPartition(
          baseTableName,
          partition,
          partitionMembers
        );
      });
    }

    await insertQueue.onIdle();
  }

  private async insertIntoPartition(
    baseTableName: string,
    partition: number,
    members: AudienceMember[]
  ): Promise<void> {
    const values = members.map(member => [
      member.identifierType,
      member.identifierValue,
      JSON.stringify(member.attributes),
      partition
    ]);

    await this.db.execute(`
      INSERT INTO ${baseTableName}_p${partition} 
      (identifier_type, identifier_value, attributes, partition_key)
      VALUES ?
      ON CONFLICT (partition_key, identifier_value) 
      DO UPDATE SET
        attributes = EXCLUDED.attributes,
        added_at = NOW()
    `, [values]);
  }

  // Parallel query across partitions
  async queryPartitioned(
    audienceId: string,
    filter: QueryFilter
  ): Promise<AudienceMember[]> {
    const baseTableName = `audience_${audienceId.replace(/-/g, '_')}`;
    const results: AudienceMember[] = [];
    
    // If we have identifier value, query specific partition
    if (filter.identifierValue) {
      const partition = this.getPartition(filter.identifierValue);
      
      const rows = await this.db.query(`
        SELECT * FROM ${baseTableName}_p${partition}
        WHERE identifier_value = ?
      `, [filter.identifierValue]);
      
      return this.mapRows(rows);
    }

    // Otherwise, query all partitions in parallel
    const queryQueue = new PQueue({ concurrency: 4 });
    const partitionResults: AudienceMember[][] = [];

    for (let i = 0; i < this.PARTITION_COUNT; i++) {
      queryQueue.add(async () => {
        const rows = await this.queryPartition(
          baseTableName,
          i,
          filter
        );
        partitionResults[i] = this.mapRows(rows);
      });
    }

    await queryQueue.onIdle();

    // Merge results
    return partitionResults.flat();
  }
}
```

## 6. Audience Versioning

### Version Control System

```typescript
// Audience version management
export class AudienceVersionManager {
  constructor(
    private db: Database,
    private storage: IStorageStrategy
  ) {}

  // Create a new version
  async createVersion(
    audienceId: string,
    userId: string,
    description: string
  ): Promise<AudienceVersion> {
    // Get current audience state
    const audience = await this.getAudience(audienceId);
    const currentVersion = await this.getCurrentVersion(audienceId);
    
    // Create snapshot
    const snapshot = await this.createSnapshot(audience);
    
    // Store version
    const version = await this.db.audienceVersion.create({
      data: {
        audienceId,
        version: (currentVersion?.version || 0) + 1,
        changeType: this.detectChangeType(currentVersion?.snapshot, snapshot),
        changeDescription: description,
        previousState: currentVersion?.snapshot,
        newState: snapshot,
        changedBy: userId,
        changedAt: new Date()
      }
    });

    // If major change, backup member data
    if (this.isMajorChange(version.changeType)) {
      await this.backupMemberData(audienceId, version.version);
    }

    return version;
  }

  // Restore to a specific version
  async restoreVersion(
    audienceId: string,
    targetVersion: number,
    userId: string
  ): Promise<void> {
    const version = await this.getVersion(audienceId, targetVersion);
    
    if (!version) {
      throw new Error(`Version ${targetVersion} not found`);
    }

    // Create restore point
    await this.createVersion(
      audienceId,
      userId,
      `Restored to version ${targetVersion}`
    );

    // Restore audience metadata
    await this.restoreMetadata(audienceId, version.newState);

    // Restore member data if backed up
    if (await this.hasBackup(audienceId, targetVersion)) {
      await this.restoreMemberData(audienceId, targetVersion);
    }
  }

  // Compare versions
  async compareVersions(
    audienceId: string,
    version1: number,
    version2: number
  ): Promise<VersionDiff> {
    const v1 = await this.getVersion(audienceId, version1);
    const v2 = await this.getVersion(audienceId, version2);

    if (!v1 || !v2) {
      throw new Error('Version not found');
    }

    return {
      metadata: this.diffMetadata(v1.newState, v2.newState),
      rules: this.diffRules(v1.newState.rules, v2.newState.rules),
      size: {
        before: v1.newState.size,
        after: v2.newState.size,
        change: v2.newState.size - v1.newState.size
      },
      timeline: await this.getTimeline(audienceId, version1, version2)
    };
  }

  // Create snapshot of current state
  private async createSnapshot(audience: Audience): Promise<AudienceSnapshot> {
    const memberSample = await this.storage.retrieve(
      audience.id,
      { limit: 100 }
    );

    return {
      id: audience.id,
      name: audience.name,
      description: audience.description,
      type: audience.type,
      subtype: audience.subtype,
      status: audience.status,
      size: audience.size,
      rules: audience.rules,
      metadata: audience.metadata,
      memberSample: memberSample.map(m => ({
        identifierType: m.identifierType,
        sampleValue: this.anonymize(m.identifierValue)
      }))
    };
  }

  // Backup member data for major versions
  private async backupMemberData(
    audienceId: string,
    version: number
  ): Promise<void> {
    const backupKey = `backups/${audienceId}/v${version}/members.ndjson.gz`;
    
    // Stream members to backup
    const stream = new PassThrough();
    const gzip = zlib.createGzip();
    
    const uploadPromise = this.s3Client.upload({
      Bucket: this.config.backupBucket,
      Key: backupKey,
      Body: stream.pipe(gzip),
      ContentType: 'application/x-ndjson',
      ContentEncoding: 'gzip',
      StorageClass: 'GLACIER'
    }).promise();

    // Stream all members
    let offset = 0;
    const batchSize = 10000;
    
    while (true) {
      const members = await this.storage.retrieve(audienceId, {
        limit: batchSize,
        offset
      });

      if (members.length === 0) break;

      for (const member of members) {
        stream.write(JSON.stringify(member) + '\n');
      }

      offset += batchSize;
    }

    stream.end();
    await uploadPromise;
  }

  // Detect type of change
  private detectChangeType(
    previous: AudienceSnapshot | null,
    current: AudienceSnapshot
  ): ChangeType {
    if (!previous) return ChangeType.CREATED;

    const changes: string[] = [];

    if (previous.name !== current.name) changes.push('name');
    if (previous.type !== current.type) changes.push('type');
    if (!this.rulesEqual(previous.rules, current.rules)) changes.push('rules');
    
    const sizeChange = Math.abs(current.size - previous.size) / previous.size;
    if (sizeChange > 0.1) changes.push('size');

    if (changes.length === 0) return ChangeType.METADATA_UPDATE;
    if (changes.includes('rules')) return ChangeType.RULES_CHANGED;
    if (changes.includes('size') && sizeChange > 0.5) return ChangeType.MAJOR_UPDATE;
    
    return ChangeType.MINOR_UPDATE;
  }
}

// Version diff interface
export interface VersionDiff {
  metadata: {
    field: string;
    before: any;
    after: any;
  }[];
  rules: {
    added: AudienceRule[];
    removed: AudienceRule[];
    modified: {
      before: AudienceRule;
      after: AudienceRule;
    }[];
  };
  size: {
    before: number;
    after: number;
    change: number;
  };
  timeline: VersionEvent[];
}
```

## 7. Data Retention Policies

### Automated Data Lifecycle Management

```typescript
// Data retention service
export class AudienceRetentionService {
  private retentionPolicies: Map<string, RetentionPolicy>;

  constructor(
    private config: RetentionConfig,
    private scheduler: JobScheduler
  ) {
    this.setupDefaultPolicies();
    this.scheduleRetentionJobs();
  }

  private setupDefaultPolicies(): void {
    this.retentionPolicies = new Map([
      ['active', {
        retentionDays: 365,
        archiveAfterDays: 180,
        compressionAfterDays: 30
      }],
      ['inactive', {
        retentionDays: 90,
        archiveAfterDays: 30,
        deleteAfterDays: 90
      }],
      ['expired', {
        retentionDays: 30,
        deleteAfterDays: 30
      }],
      ['test', {
        retentionDays: 7,
        deleteAfterDays: 7
      }]
    ]);
  }

  // Schedule retention jobs
  private scheduleRetentionJobs(): void {
    // Daily retention check
    this.scheduler.schedule('0 2 * * *', async () => {
      await this.processRetention();
    });

    // Weekly archive job
    this.scheduler.schedule('0 3 * * 0', async () => {
      await this.processArchival();
    });

    // Monthly cleanup
    this.scheduler.schedule('0 4 1 * *', async () => {
      await this.processCleanup();
    });
  }

  // Process retention policies
  async processRetention(): Promise<RetentionReport> {
    const report: RetentionReport = {
      processed: 0,
      archived: 0,
      deleted: 0,
      errors: []
    };

    try {
      // Get all audiences
      const audiences = await this.getAudiencesForRetention();

      for (const audience of audiences) {
        try {
          const policy = this.getPolicy(audience);
          await this.applyRetentionPolicy(audience, policy, report);
          report.processed++;
        } catch (error) {
          report.errors.push({
            audienceId: audience.id,
            error: error.message
          });
        }
      }

      // Send report
      await this.sendRetentionReport(report);
    } catch (error) {
      logger.error('Retention processing failed', error);
      throw error;
    }

    return report;
  }

  // Apply retention policy to audience
  private async applyRetentionPolicy(
    audience: Audience,
    policy: RetentionPolicy,
    report: RetentionReport
  ): Promise<void> {
    const age = this.getAudienceAge(audience);

    // Check for deletion
    if (policy.deleteAfterDays && age > policy.deleteAfterDays) {
      await this.deleteAudience(audience);
      report.deleted++;
      return;
    }

    // Check for archival
    if (policy.archiveAfterDays && age > policy.archiveAfterDays) {
      if (!audience.metadata.archived) {
        await this.archiveAudience(audience);
        report.archived++;
      }
    }

    // Check for compression
    if (policy.compressionAfterDays && age > policy.compressionAfterDays) {
      if (!audience.storage.compression) {
        await this.compressAudience(audience);
      }
    }

    // Handle expired members
    await this.removeExpiredMembers(audience);
  }

  // Archive audience to cold storage
  private async archiveAudience(audience: Audience): Promise<void> {
    logger.info(`Archiving audience ${audience.id}`);

    // Move data to cold storage
    const archiveLocation = await this.moveToArchive(audience);

    // Update audience metadata
    await this.db.audience.update({
      where: { id: audience.id },
      data: {
        status: 'archived',
        metadata: {
          ...audience.metadata,
          archived: true,
          archivedAt: new Date(),
          archiveLocation
        }
      }
    });

    // Clear from cache
    await this.cache.invalidateAudience(audience.id);
  }

  // Move data to archive storage
  private async moveToArchive(
    audience: Audience
  ): Promise<string> {
    const archiveKey = `archive/${audience.organizationId}/${audience.id}/data.tar.gz`;

    // Create archive
    const archive = archiver('tar', {
      gzip: true,
      gzipOptions: { level: 9 }
    });

    const uploadStream = new PassThrough();
    
    const uploadPromise = this.s3Client.upload({
      Bucket: this.config.archiveBucket,
      Key: archiveKey,
      Body: uploadStream,
      StorageClass: 'GLACIER_IR'
    }).promise();

    archive.pipe(uploadStream);

    // Add audience metadata
    archive.append(
      JSON.stringify(audience, null, 2),
      { name: 'metadata.json' }
    );

    // Stream and add member data
    let offset = 0;
    const batchSize = 10000;
    let fileIndex = 0;

    while (true) {
      const members = await this.storage.retrieve(audience.id, {
        limit: batchSize,
        offset
      });

      if (members.length === 0) break;

      const ndjson = members
        .map(m => JSON.stringify(m))
        .join('\n');

      archive.append(ndjson, {
        name: `members/batch-${fileIndex}.ndjson`
      });

      offset += batchSize;
      fileIndex++;
    }

    await archive.finalize();
    const result = await uploadPromise;

    // Delete original data
    await this.storage.delete(audience.id);

    return result.Location;
  }

  // Remove expired members
  private async removeExpiredMembers(
    audience: Audience
  ): Promise<number> {
    const deleted = await this.db.audienceMember.deleteMany({
      where: {
        audienceId: audience.id,
        expiresAt: {
          lt: new Date()
        }
      }
    });

    if (deleted.count > 0) {
      // Update audience size
      await this.db.audience.update({
        where: { id: audience.id },
        data: {
          size: {
            decrement: deleted.count
          }
        }
      });

      // Log retention action
      await this.logRetentionAction({
        audienceId: audience.id,
        action: 'expired_members_removed',
        count: deleted.count,
        timestamp: new Date()
      });
    }

    return deleted.count;
  }

  // Get retention policy for audience
  private getPolicy(audience: Audience): RetentionPolicy {
    // Check for custom policy
    if (audience.metadata.retentionPolicy) {
      return audience.metadata.retentionPolicy;
    }

    // Determine by status
    if (audience.status === 'active') {
      return this.retentionPolicies.get('active')!;
    } else if (audience.status === 'archived') {
      return this.retentionPolicies.get('inactive')!;
    } else if (audience.metadata.isTest) {
      return this.retentionPolicies.get('test')!;
    }

    // Check if expired
    if (audience.metadata.expiresAt && audience.metadata.expiresAt < new Date()) {
      return this.retentionPolicies.get('expired')!;
    }

    // Default policy
    return this.retentionPolicies.get('active')!;
  }

  // Calculate audience age in days
  private getAudienceAge(audience: Audience): number {
    const createdAt = new Date(audience.createdAt);
    const now = new Date();
    return Math.floor((now.getTime() - createdAt.getTime()) / (1000 * 60 * 60 * 24));
  }
}

// Retention policy interface
export interface RetentionPolicy {
  retentionDays: number;
  archiveAfterDays?: number;
  compressionAfterDays?: number;
  deleteAfterDays?: number;
  customRules?: RetentionRule[];
}

export interface RetentionRule {
  condition: (audience: Audience) => boolean;
  action: 'archive' | 'compress' | 'delete' | 'notify';
  afterDays: number;
}

export interface RetentionReport {
  processed: number;
  archived: number;
  deleted: number;
  errors: {
    audienceId: string;
    error: string;
  }[];
}
```

## Summary

This section covered comprehensive audience storage and management strategies:

1. **Database Architecture**: Hybrid approach using PostgreSQL for structured data and MongoDB for flexible storage
2. **Storage Strategies**: Automatic selection based on audience size (database < 100k, segmented < 10M, external > 10M)
3. **Caching Layer**: Redis-based caching with TTL management and cache warming
4. **Data Partitioning**: Time-based and hash-based partitioning for scalability
5. **Versioning System**: Complete audit trail with snapshot and restore capabilities
6. **Retention Policies**: Automated lifecycle management with archival and cleanup

The implementation provides enterprise-grade data management with considerations for:
- Performance at scale
- Data integrity and consistency
- Cost optimization through tiered storage
- Compliance through retention policies
- Disaster recovery through versioning and backups