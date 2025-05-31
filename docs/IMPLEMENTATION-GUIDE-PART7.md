# Activation Manager Implementation Guide - Part 7: Distribution Engine and Job Queue

## Table of Contents
1. [Distribution Engine Architecture](#distribution-engine-architecture)
2. [Job Queue Implementation](#job-queue-implementation)
3. [Platform Distribution Workers](#platform-distribution-workers)
4. [Batch Processing System](#batch-processing-system)
5. [Error Handling and Retry Logic](#error-handling-retry-logic)
6. [Progress Tracking and Monitoring](#progress-tracking-monitoring)
7. [Rate Limiting and Throttling](#rate-limiting-throttling)

## 1. Distribution Engine Architecture

### Core Distribution System

```typescript
// Distribution engine interface
export interface IDistributionEngine {
  distribute(
    audienceId: string,
    platformIds: string[],
    options?: DistributionOptions
  ): Promise<DistributionJob>;
  
  getJobStatus(jobId: string): Promise<JobStatus>;
  cancelJob(jobId: string): Promise<void>;
  retryJob(jobId: string): Promise<void>;
  getJobHistory(audienceId: string): Promise<DistributionJob[]>;
}

// Distribution options
export interface DistributionOptions {
  priority?: JobPriority;
  scheduledAt?: Date;
  expiresAt?: Date;
  batchSize?: number;
  parallelism?: number;
  dryRun?: boolean;
  metadata?: Record<string, any>;
}

export enum JobPriority {
  LOW = 1,
  NORMAL = 5,
  HIGH = 10,
  CRITICAL = 20
}

// Main distribution engine
export class DistributionEngine implements IDistributionEngine {
  constructor(
    private jobQueue: IJobQueue,
    private platformManager: IPlatformManager,
    private audienceRepo: IAudienceRepository,
    private eventBus: IEventBus,
    private config: DistributionConfig
  ) {}

  async distribute(
    audienceId: string,
    platformIds: string[],
    options: DistributionOptions = {}
  ): Promise<DistributionJob> {
    // Validate audience
    const audience = await this.audienceRepo.findById(audienceId);
    if (!audience) {
      throw new Error('Audience not found');
    }

    if (audience.status !== 'active') {
      throw new Error(`Audience is not active: ${audience.status}`);
    }

    // Validate platforms
    const platforms = await this.validatePlatforms(platformIds);

    // Create distribution job
    const job: DistributionJob = {
      id: generateId(),
      audienceId,
      audienceName: audience.name,
      audienceSize: audience.size,
      platforms: platforms.map(p => ({
        platformId: p.id,
        platformName: p.name,
        status: 'pending',
        progress: 0
      })),
      priority: options.priority || JobPriority.NORMAL,
      status: 'pending',
      createdAt: new Date(),
      scheduledAt: options.scheduledAt || new Date(),
      options: {
        batchSize: options.batchSize || this.config.defaultBatchSize,
        parallelism: options.parallelism || this.config.defaultParallelism,
        dryRun: options.dryRun || false,
        metadata: options.metadata || {}
      }
    };

    // Save job to database
    await this.saveJob(job);

    // Queue the job
    await this.jobQueue.enqueue({
      type: 'audience-distribution',
      jobId: job.id,
      priority: job.priority,
      scheduledAt: job.scheduledAt,
      payload: {
        audienceId,
        platformIds,
        options
      }
    });

    // Emit event
    await this.eventBus.emit('distribution.started', {
      jobId: job.id,
      audienceId,
      platforms: platformIds
    });

    return job;
  }

  async processDistributionJob(job: QueuedJob): Promise<void> {
    const distributionJob = await this.getJob(job.jobId);
    if (!distributionJob) {
      throw new Error(`Job not found: ${job.jobId}`);
    }

    try {
      // Update job status
      await this.updateJobStatus(job.jobId, 'processing');

      // Get audience data
      const audience = await this.audienceRepo.findById(
        distributionJob.audienceId
      );
      if (!audience) {
        throw new Error('Audience not found');
      }

      // Process each platform in parallel
      const platformTasks = distributionJob.platforms.map(platform =>
        this.distributeToPlatform(
          distributionJob,
          audience,
          platform.platformId
        )
      );

      // Wait for all platforms with controlled parallelism
      const results = await this.runWithParallelism(
        platformTasks,
        distributionJob.options.parallelism
      );

      // Check overall status
      const hasErrors = results.some(r => r.status === 'error');
      const finalStatus = hasErrors ? 'completed_with_errors' : 'completed';

      await this.updateJobStatus(job.jobId, finalStatus);

      // Emit completion event
      await this.eventBus.emit('distribution.completed', {
        jobId: job.jobId,
        status: finalStatus,
        results
      });
    } catch (error) {
      await this.handleJobError(job.jobId, error);
      throw error;
    }
  }

  private async distributeToPlatform(
    job: DistributionJob,
    audience: Audience,
    platformId: string
  ): Promise<PlatformDistributionResult> {
    const startTime = Date.now();
    
    try {
      // Update platform status
      await this.updatePlatformStatus(job.id, platformId, 'processing');

      // Get platform adapter
      const adapter = await this.platformManager.getAdapter(platformId);
      if (!adapter) {
        throw new Error(`No adapter found for platform: ${platformId}`);
      }

      // Check if dry run
      if (job.options.dryRun) {
        return await this.performDryRun(job, audience, platformId, adapter);
      }

      // Create distribution context
      const context: DistributionContext = {
        jobId: job.id,
        audienceId: audience.id,
        platformId,
        batchSize: job.options.batchSize,
        onProgress: async (progress) => {
          await this.updatePlatformProgress(job.id, platformId, progress);
        }
      };

      // Execute distribution
      const result = await adapter.distributeAudience(audience, context);

      // Update platform status
      await this.updatePlatformStatus(
        job.id,
        platformId,
        'completed',
        result
      );

      return {
        platformId,
        status: 'success',
        duration: Date.now() - startTime,
        recordsProcessed: result.recordsProcessed,
        recordsFailed: result.recordsFailed,
        platformResponse: result.platformResponse
      };
    } catch (error) {
      await this.updatePlatformStatus(
        job.id,
        platformId,
        'error',
        { error: error.message }
      );

      return {
        platformId,
        status: 'error',
        duration: Date.now() - startTime,
        error: error.message
      };
    }
  }

  private async runWithParallelism<T>(
    tasks: Promise<T>[],
    parallelism: number
  ): Promise<T[]> {
    const results: T[] = [];
    const executing: Promise<void>[] = [];

    for (const task of tasks) {
      const promise = task.then(result => {
        results.push(result);
      });

      executing.push(promise);

      if (executing.length >= parallelism) {
        await Promise.race(executing);
        executing.splice(
          executing.findIndex(p => p === promise),
          1
        );
      }
    }

    await Promise.all(executing);
    return results;
  }
}
```

### Distribution Job Schema

```typescript
// Database schema for distribution jobs
export const distributionJobSchema = new Schema({
  id: { type: String, required: true, unique: true },
  audienceId: { type: String, required: true, index: true },
  audienceName: String,
  audienceSize: Number,
  platforms: [{
    platformId: String,
    platformName: String,
    status: {
      type: String,
      enum: ['pending', 'processing', 'completed', 'error', 'cancelled']
    },
    progress: { type: Number, default: 0 },
    startedAt: Date,
    completedAt: Date,
    result: Schema.Types.Mixed,
    error: String
  }],
  priority: { type: Number, default: 5 },
  status: {
    type: String,
    enum: [
      'pending',
      'processing',
      'completed',
      'completed_with_errors',
      'failed',
      'cancelled'
    ]
  },
  createdAt: { type: Date, default: Date.now },
  scheduledAt: Date,
  startedAt: Date,
  completedAt: Date,
  options: {
    batchSize: Number,
    parallelism: Number,
    dryRun: Boolean,
    metadata: Schema.Types.Mixed
  },
  metrics: {
    totalRecords: Number,
    processedRecords: Number,
    failedRecords: Number,
    duration: Number,
    avgRecordsPerSecond: Number
  },
  retryCount: { type: Number, default: 0 },
  lastError: String
});

// Indexes for performance
distributionJobSchema.index({ status: 1, scheduledAt: 1 });
distributionJobSchema.index({ audienceId: 1, createdAt: -1 });
distributionJobSchema.index({ 'platforms.platformId': 1, status: 1 });
```

## 2. Job Queue Implementation

### Redis-based Queue with Bull

```typescript
import Bull from 'bull';
import { Redis } from 'ioredis';

// Job queue implementation
export class DistributionJobQueue implements IJobQueue {
  private queues: Map<string, Bull.Queue>;
  private workers: Map<string, Bull.Worker>;

  constructor(
    private redis: Redis,
    private config: QueueConfig
  ) {
    this.queues = new Map();
    this.workers = new Map();
    this.initializeQueues();
  }

  private initializeQueues(): void {
    // Create queues for different job types
    const queueTypes = [
      'distribution-high',
      'distribution-normal',
      'distribution-low',
      'distribution-retry',
      'distribution-scheduled'
    ];

    for (const queueType of queueTypes) {
      const queue = new Bull(queueType, {
        redis: this.redis,
        defaultJobOptions: {
          removeOnComplete: false,
          removeOnFail: false,
          attempts: this.config.maxRetries,
          backoff: {
            type: 'exponential',
            delay: 2000
          }
        }
      });

      this.queues.set(queueType, queue);
    }
  }

  async enqueue(job: QueueJob): Promise<string> {
    const queueName = this.getQueueName(job.priority);
    const queue = this.queues.get(queueName);
    
    if (!queue) {
      throw new Error(`Queue not found: ${queueName}`);
    }

    const options: Bull.JobOptions = {
      priority: job.priority,
      delay: job.scheduledAt
        ? job.scheduledAt.getTime() - Date.now()
        : 0,
      attempts: job.maxRetries || this.config.maxRetries
    };

    const bullJob = await queue.add(job.type, job, options);
    return bullJob.id;
  }

  async setupWorkers(handlers: JobHandlers): Promise<void> {
    for (const [queueName, queue] of this.queues) {
      const worker = new Bull.Worker(
        queueName,
        async (job: Bull.Job) => {
          const handler = handlers[job.data.type];
          if (!handler) {
            throw new Error(`No handler for job type: ${job.data.type}`);
          }

          // Add job context
          const context: JobContext = {
            jobId: job.id,
            attemptNumber: job.attemptsMade + 1,
            maxAttempts: job.opts.attempts || 1,
            progress: (percent: number) => job.progress(percent),
            log: (message: string) => job.log(message)
          };

          return await handler(job.data, context);
        },
        {
          concurrency: this.getConcurrency(queueName),
          redis: this.redis
        }
      );

      // Event handlers
      worker.on('completed', async (job, result) => {
        await this.onJobCompleted(job, result);
      });

      worker.on('failed', async (job, error) => {
        await this.onJobFailed(job, error);
      });

      worker.on('progress', async (job, progress) => {
        await this.onJobProgress(job, progress);
      });

      this.workers.set(queueName, worker);
    }
  }

  private getQueueName(priority: JobPriority): string {
    if (priority >= JobPriority.HIGH) return 'distribution-high';
    if (priority >= JobPriority.NORMAL) return 'distribution-normal';
    return 'distribution-low';
  }

  private getConcurrency(queueName: string): number {
    const concurrencyMap = {
      'distribution-high': 10,
      'distribution-normal': 5,
      'distribution-low': 2,
      'distribution-retry': 3,
      'distribution-scheduled': 5
    };
    return concurrencyMap[queueName] || 5;
  }

  async getJobStatus(jobId: string): Promise<JobStatus | null> {
    for (const [, queue] of this.queues) {
      const job = await queue.getJob(jobId);
      if (job) {
        return {
          id: job.id,
          type: job.data.type,
          status: await job.getState(),
          progress: job.progress(),
          createdAt: new Date(job.timestamp),
          processedAt: job.processedOn ? new Date(job.processedOn) : undefined,
          completedAt: job.finishedOn ? new Date(job.finishedOn) : undefined,
          failedReason: job.failedReason,
          attemptsMade: job.attemptsMade,
          data: job.data
        };
      }
    }
    return null;
  }

  async cancelJob(jobId: string): Promise<void> {
    for (const [, queue] of this.queues) {
      const job = await queue.getJob(jobId);
      if (job) {
        await job.remove();
        return;
      }
    }
    throw new Error(`Job not found: ${jobId}`);
  }

  async retryJob(jobId: string): Promise<void> {
    for (const [, queue] of this.queues) {
      const job = await queue.getJob(jobId);
      if (job) {
        await job.retry();
        return;
      }
    }
    throw new Error(`Job not found: ${jobId}`);
  }

  // Dead letter queue handling
  async setupDeadLetterQueue(): Promise<void> {
    const dlq = new Bull('distribution-dlq', {
      redis: this.redis
    });

    // Process failed jobs that exceeded retry limit
    for (const [, queue] of this.queues) {
      queue.on('failed', async (job, error) => {
        if (job.attemptsMade >= (job.opts.attempts || 1)) {
          await dlq.add('dead-letter', {
            originalJob: job.data,
            failedAt: new Date(),
            error: error.message,
            stack: error.stack,
            attemptsMade: job.attemptsMade
          });
        }
      });
    }

    this.queues.set('distribution-dlq', dlq);
  }
}

// Priority queue implementation for complex scheduling
export class PriorityDistributionQueue {
  private heap: PriorityHeap<ScheduledJob>;
  private processing: Set<string>;

  constructor(private config: QueueConfig) {
    this.heap = new PriorityHeap(
      (a, b) => this.comparePriority(a, b)
    );
    this.processing = new Set();
  }

  private comparePriority(a: ScheduledJob, b: ScheduledJob): number {
    // First by scheduled time
    const timeDiff = a.scheduledAt.getTime() - b.scheduledAt.getTime();
    if (timeDiff !== 0) return timeDiff;

    // Then by priority
    return b.priority - a.priority;
  }

  async enqueue(job: ScheduledJob): Promise<void> {
    // Check for duplicates
    if (this.processing.has(job.id)) {
      throw new Error(`Job already processing: ${job.id}`);
    }

    this.heap.push(job);
    await this.persistQueue();
  }

  async dequeue(): Promise<ScheduledJob | null> {
    while (!this.heap.isEmpty()) {
      const job = this.heap.peek();
      
      // Check if job is ready
      if (job.scheduledAt > new Date()) {
        return null;
      }

      // Remove and mark as processing
      this.heap.pop();
      this.processing.add(job.id);
      
      await this.persistQueue();
      return job;
    }

    return null;
  }

  async complete(jobId: string): Promise<void> {
    this.processing.delete(jobId);
  }

  async requeue(job: ScheduledJob): Promise<void> {
    this.processing.delete(job.id);
    await this.enqueue(job);
  }

  private async persistQueue(): Promise<void> {
    // Persist queue state to Redis for recovery
    const state = {
      heap: this.heap.toArray(),
      processing: Array.from(this.processing)
    };

    await this.redis.set(
      'distribution:queue:state',
      JSON.stringify(state),
      'EX',
      86400 // 24 hours
    );
  }

  async recover(): Promise<void> {
    const stateStr = await this.redis.get('distribution:queue:state');
    if (!stateStr) return;

    const state = JSON.parse(stateStr);
    
    // Rebuild heap
    for (const job of state.heap) {
      this.heap.push({
        ...job,
        scheduledAt: new Date(job.scheduledAt)
      });
    }

    // Rebuild processing set
    this.processing = new Set(state.processing);
  }
}
```

## 3. Platform Distribution Workers

### Platform-specific Workers

```typescript
// Base platform worker
export abstract class PlatformDistributionWorker {
  constructor(
    protected platform: Platform,
    protected config: WorkerConfig
  ) {}

  abstract processAudience(
    audience: Audience,
    context: DistributionContext
  ): Promise<DistributionResult>;

  protected async processBatch(
    members: AudienceMember[],
    context: DistributionContext
  ): Promise<BatchResult> {
    const results: ProcessedMember[] = [];
    const errors: ProcessingError[] = [];

    // Process in chunks
    const chunks = this.chunkArray(members, this.config.chunkSize);
    
    for (let i = 0; i < chunks.length; i++) {
      try {
        const chunkResults = await this.processChunk(chunks[i]);
        results.push(...chunkResults.success);
        errors.push(...chunkResults.errors);

        // Update progress
        const progress = Math.round(((i + 1) / chunks.length) * 100);
        await context.onProgress(progress);
      } catch (error) {
        // Log chunk error but continue
        errors.push({
          memberIds: chunks[i].map(m => m.id),
          error: error.message,
          timestamp: new Date()
        });
      }
    }

    return {
      success: results,
      errors,
      totalProcessed: members.length,
      successCount: results.length,
      errorCount: errors.length
    };
  }

  protected abstract processChunk(
    members: AudienceMember[]
  ): Promise<ChunkResult>;

  protected chunkArray<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }
}

// Meta platform worker
export class MetaDistributionWorker extends PlatformDistributionWorker {
  private metaClient: MetaAdsAPI;

  constructor(platform: Platform, config: WorkerConfig) {
    super(platform, config);
    this.metaClient = new MetaAdsAPI({
      accessToken: platform.credentials.accessToken,
      apiVersion: 'v18.0'
    });
  }

  async processAudience(
    audience: Audience,
    context: DistributionContext
  ): Promise<DistributionResult> {
    try {
      // Create custom audience
      const customAudience = await this.createCustomAudience(audience);

      // Process members in batches
      let offset = 0;
      const batchSize = context.batchSize;
      let totalProcessed = 0;
      let totalErrors = 0;

      while (offset < audience.size) {
        // Get batch of members
        const members = await this.getAudienceMembers(
          audience.id,
          offset,
          batchSize
        );

        if (members.length === 0) break;

        // Hash identifiers as required by Meta
        const hashedMembers = await this.hashMembers(members);

        // Upload batch
        const batchResult = await this.uploadBatch(
          customAudience.id,
          hashedMembers,
          context
        );

        totalProcessed += batchResult.successCount;
        totalErrors += batchResult.errorCount;
        offset += batchSize;

        // Progress update
        const progress = Math.round((offset / audience.size) * 100);
        await context.onProgress(progress);
      }

      return {
        platformId: this.platform.id,
        audienceId: audience.id,
        status: 'success',
        recordsProcessed: totalProcessed,
        recordsFailed: totalErrors,
        platformResponse: {
          customAudienceId: customAudience.id,
          estimatedSize: customAudience.approximate_count
        }
      };
    } catch (error) {
      return {
        platformId: this.platform.id,
        audienceId: audience.id,
        status: 'error',
        error: error.message,
        recordsProcessed: 0,
        recordsFailed: audience.size
      };
    }
  }

  private async createCustomAudience(
    audience: Audience
  ): Promise<MetaCustomAudience> {
    const params = {
      name: audience.name,
      description: audience.description,
      subtype: this.mapAudienceSubtype(audience.subtype),
      customer_file_source: 'USER_PROVIDED_ONLY',
      retention_days: 180
    };

    const response = await this.metaClient.post(
      `/${this.platform.credentials.adAccountId}/customaudiences`,
      params
    );

    return response.data;
  }

  private async hashMembers(
    members: AudienceMember[]
  ): Promise<HashedMember[]> {
    return members.map(member => {
      const normalized = this.normalizeIdentifier(
        member.identifierType,
        member.identifierValue
      );

      const hashed = crypto
        .createHash('sha256')
        .update(normalized)
        .digest('hex');

      return {
        id: member.id,
        [member.identifierType]: hashed,
        ...this.hashAdditionalFields(member.attributes)
      };
    });
  }

  private normalizeIdentifier(
    type: string,
    value: string
  ): string {
    switch (type) {
      case 'email':
        return value.toLowerCase().trim();
      case 'phone':
        // Remove all non-numeric characters
        return value.replace(/\D/g, '');
      default:
        return value.trim();
    }
  }

  private async uploadBatch(
    customAudienceId: string,
    members: HashedMember[],
    context: DistributionContext
  ): Promise<BatchResult> {
    const schema = this.getUploadSchema(members);
    const data = members.map(m => this.formatMemberData(m, schema));

    try {
      const response = await this.metaClient.post(
        `/${customAudienceId}/users`,
        {
          payload: {
            schema,
            data
          }
        }
      );

      return {
        success: members.map(m => ({ id: m.id, status: 'uploaded' })),
        errors: [],
        totalProcessed: members.length,
        successCount: members.length,
        errorCount: 0
      };
    } catch (error) {
      if (error.response?.data?.error?.error_subcode === 2056001) {
        // Partial failure - parse response
        return this.handlePartialFailure(members, error.response.data);
      }
      throw error;
    }
  }

  protected async processChunk(
    members: AudienceMember[]
  ): Promise<ChunkResult> {
    const hashedMembers = await this.hashMembers(members);
    // Implementation specific to Meta's API requirements
    return {
      success: hashedMembers.map(m => ({
        id: m.id,
        status: 'processed',
        platformData: m
      })),
      errors: []
    };
  }
}

// Google Ads platform worker
export class GoogleAdsDistributionWorker extends PlatformDistributionWorker {
  private googleAdsClient: GoogleAdsApi;

  constructor(platform: Platform, config: WorkerConfig) {
    super(platform, config);
    this.googleAdsClient = new GoogleAdsApi({
      client_id: platform.credentials.clientId,
      client_secret: platform.credentials.clientSecret,
      refresh_token: platform.credentials.refreshToken,
      developer_token: platform.credentials.developerToken
    });
  }

  async processAudience(
    audience: Audience,
    context: DistributionContext
  ): Promise<DistributionResult> {
    const customer = this.googleAdsClient.Customer({
      customer_id: this.platform.credentials.customerId
    });

    try {
      // Create user list
      const userList = await this.createUserList(customer, audience);

      // Process in batches with Google's OfflineUserDataJob
      const job = await this.createDataJob(customer, userList.id);
      
      let offset = 0;
      const batchSize = Math.min(context.batchSize, 100000); // Google's limit

      while (offset < audience.size) {
        const members = await this.getAudienceMembers(
          audience.id,
          offset,
          batchSize
        );

        if (members.length === 0) break;

        // Add operations to job
        await this.addOperationsToJob(job, members);
        
        offset += batchSize;
        const progress = Math.round((offset / audience.size) * 100);
        await context.onProgress(progress);
      }

      // Run the job
      const result = await this.runJob(job);

      return {
        platformId: this.platform.id,
        audienceId: audience.id,
        status: 'success',
        recordsProcessed: result.totalOperations,
        recordsFailed: result.failedOperations,
        platformResponse: {
          userListId: userList.id,
          jobId: job.resourceName
        }
      };
    } catch (error) {
      return {
        platformId: this.platform.id,
        audienceId: audience.id,
        status: 'error',
        error: error.message,
        recordsProcessed: 0,
        recordsFailed: audience.size
      };
    }
  }

  private async createUserList(
    customer: GoogleAdsCustomer,
    audience: Audience
  ): Promise<GoogleUserList> {
    const userListService = customer.userLists();

    const userList = {
      name: audience.name,
      description: audience.description,
      membershipLifeSpan: 540, // 18 months
      membershipStatus: 'OPEN',
      type: this.mapAudienceType(audience.type),
      crmBasedUserList: {
        uploadKeyType: 'CONTACT_INFO',
        dataSourceType: 'FIRST_PARTY'
      }
    };

    const operation = userListService.create(userList);
    const response = await customer.mutate([operation]);

    return response.results[0].userList;
  }

  private async createDataJob(
    customer: GoogleAdsCustomer,
    userListId: string
  ): Promise<OfflineUserDataJob> {
    const jobService = customer.offlineUserDataJobService();

    const job = await jobService.create({
      type: 'CUSTOMER_MATCH_USER_LIST',
      customerMatchUserListMetadata: {
        userList: userListId
      }
    });

    return job;
  }

  private async addOperationsToJob(
    job: OfflineUserDataJob,
    members: AudienceMember[]
  ): Promise<void> {
    const operations = members.map(member => ({
      create: {
        userIdentifiers: this.createUserIdentifiers(member)
      }
    }));

    // Google allows max 100k operations per request
    const chunks = this.chunkArray(operations, 50000);

    for (const chunk of chunks) {
      await job.addOperations(chunk);
    }
  }

  private createUserIdentifiers(
    member: AudienceMember
  ): UserIdentifier[] {
    const identifiers: UserIdentifier[] = [];

    switch (member.identifierType) {
      case 'email':
        identifiers.push({
          hashedEmail: this.hashSHA256(
            member.identifierValue.toLowerCase().trim()
          )
        });
        break;

      case 'phone':
        identifiers.push({
          hashedPhoneNumber: this.hashSHA256(
            this.normalizePhoneNumber(member.identifierValue)
          )
        });
        break;

      case 'maid':
        identifiers.push({
          mobileId: member.identifierValue
        });
        break;
    }

    // Add additional identifiers from attributes
    if (member.attributes.firstName && member.attributes.lastName) {
      identifiers.push({
        addressInfo: {
          hashedFirstName: this.hashSHA256(
            member.attributes.firstName.toLowerCase()
          ),
          hashedLastName: this.hashSHA256(
            member.attributes.lastName.toLowerCase()
          ),
          countryCode: member.attributes.countryCode || 'US'
        }
      });
    }

    return identifiers;
  }

  private hashSHA256(value: string): string {
    return crypto
      .createHash('sha256')
      .update(value)
      .digest('hex');
  }

  protected async processChunk(
    members: AudienceMember[]
  ): Promise<ChunkResult> {
    // Google Ads specific processing
    const identifiers = members.map(m => ({
      id: m.id,
      userIdentifiers: this.createUserIdentifiers(m)
    }));

    return {
      success: identifiers.map(i => ({
        id: i.id,
        status: 'processed',
        platformData: i.userIdentifiers
      })),
      errors: []
    };
  }
}
```

## 4. Batch Processing System

### Efficient Batch Processing

```typescript
// Batch processor for large audiences
export class BatchProcessor {
  private activeJobs: Map<string, BatchJob>;
  private batchQueue: Queue<Batch>;

  constructor(
    private config: BatchConfig,
    private storage: IAudienceStorage
  ) {
    this.activeJobs = new Map();
    this.batchQueue = new Queue();
  }

  async processBatchJob(
    job: BatchJob,
    processor: IBatchProcessor
  ): Promise<BatchJobResult> {
    this.activeJobs.set(job.id, job);

    try {
      // Initialize job metrics
      const metrics: BatchMetrics = {
        startTime: Date.now(),
        totalBatches: Math.ceil(job.totalRecords / job.batchSize),
        processedBatches: 0,
        processedRecords: 0,
        failedRecords: 0,
        errors: []
      };

      // Create batches
      const batches = await this.createBatches(job);
      
      // Process batches with parallelism control
      const results = await this.processBatchesInParallel(
        batches,
        processor,
        job.parallelism
      );

      // Aggregate results
      for (const result of results) {
        metrics.processedRecords += result.processedCount;
        metrics.failedRecords += result.failedCount;
        metrics.processedBatches++;
        
        if (result.errors.length > 0) {
          metrics.errors.push(...result.errors);
        }

        // Update job progress
        await this.updateJobProgress(job.id, metrics);
      }

      metrics.endTime = Date.now();
      metrics.duration = metrics.endTime - metrics.startTime;
      metrics.throughput = metrics.processedRecords / (metrics.duration / 1000);

      return {
        jobId: job.id,
        status: metrics.failedRecords > 0 ? 'partial_success' : 'success',
        metrics
      };
    } catch (error) {
      return {
        jobId: job.id,
        status: 'failed',
        error: error.message
      };
    } finally {
      this.activeJobs.delete(job.id);
    }
  }

  private async createBatches(job: BatchJob): Promise<Batch[]> {
    const batches: Batch[] = [];
    let offset = 0;
    let batchNumber = 0;

    while (offset < job.totalRecords) {
      const size = Math.min(job.batchSize, job.totalRecords - offset);
      
      batches.push({
        id: `${job.id}-batch-${batchNumber}`,
        jobId: job.id,
        batchNumber,
        offset,
        size,
        status: 'pending'
      });

      offset += size;
      batchNumber++;
    }

    return batches;
  }

  private async processBatchesInParallel(
    batches: Batch[],
    processor: IBatchProcessor,
    parallelism: number
  ): Promise<BatchResult[]> {
    const results: BatchResult[] = [];
    const semaphore = new Semaphore(parallelism);

    const promises = batches.map(async (batch) => {
      await semaphore.acquire();
      
      try {
        const result = await this.processSingleBatch(batch, processor);
        results.push(result);
        return result;
      } finally {
        semaphore.release();
      }
    });

    await Promise.all(promises);
    return results;
  }

  private async processSingleBatch(
    batch: Batch,
    processor: IBatchProcessor
  ): Promise<BatchResult> {
    const startTime = Date.now();
    
    try {
      // Update batch status
      batch.status = 'processing';
      
      // Fetch batch data
      const data = await this.storage.getBatch(
        batch.jobId,
        batch.offset,
        batch.size
      );

      // Process batch
      const processResult = await processor.process(data, batch);

      // Update batch status
      batch.status = 'completed';
      
      return {
        batchId: batch.id,
        processedCount: processResult.success.length,
        failedCount: processResult.failed.length,
        duration: Date.now() - startTime,
        errors: processResult.errors || []
      };
    } catch (error) {
      batch.status = 'failed';
      
      return {
        batchId: batch.id,
        processedCount: 0,
        failedCount: batch.size,
        duration: Date.now() - startTime,
        errors: [{
          message: error.message,
          stack: error.stack
        }]
      };
    }
  }

  // Stream processing for very large audiences
  async streamProcess(
    audienceId: string,
    processor: IStreamProcessor,
    options: StreamOptions = {}
  ): Promise<StreamResult> {
    const { 
      batchSize = 1000,
      highWaterMark = 16,
      parallelism = 4 
    } = options;

    const readStream = this.storage.createReadStream(audienceId, {
      batchSize,
      highWaterMark
    });

    const transformStream = new Transform({
      objectMode: true,
      highWaterMark,
      async transform(chunk: AudienceMember[], encoding, callback) {
        try {
          const result = await processor.processChunk(chunk);
          callback(null, result);
        } catch (error) {
          callback(error);
        }
      }
    });

    const writeStream = new Writable({
      objectMode: true,
      highWaterMark,
      async write(result: ProcessResult, encoding, callback) {
        try {
          await processor.handleResult(result);
          callback();
        } catch (error) {
          callback(error);
        }
      }
    });

    // Set up pipeline with error handling
    const pipeline = readStream
      .pipe(transformStream)
      .pipe(writeStream);

    return new Promise((resolve, reject) => {
      let processedCount = 0;
      let errorCount = 0;

      transformStream.on('data', (result: ProcessResult) => {
        processedCount += result.success.length;
        errorCount += result.failed.length;
      });

      pipeline.on('finish', () => {
        resolve({
          processedCount,
          errorCount,
          status: 'completed'
        });
      });

      pipeline.on('error', (error) => {
        reject(error);
      });
    });
  }
}

// Batch checkpoint system for recovery
export class BatchCheckpointManager {
  constructor(
    private redis: Redis,
    private config: CheckpointConfig
  ) {}

  async saveCheckpoint(
    jobId: string,
    checkpoint: BatchCheckpoint
  ): Promise<void> {
    const key = `checkpoint:${jobId}`;
    
    await this.redis.hmset(key, {
      lastProcessedBatch: checkpoint.lastProcessedBatch,
      lastProcessedOffset: checkpoint.lastProcessedOffset,
      processedCount: checkpoint.processedCount,
      failedCount: checkpoint.failedCount,
      timestamp: checkpoint.timestamp.toISOString()
    });

    // Set expiration
    await this.redis.expire(key, this.config.ttl);
  }

  async getCheckpoint(jobId: string): Promise<BatchCheckpoint | null> {
    const key = `checkpoint:${jobId}`;
    const data = await this.redis.hgetall(key);

    if (!data || Object.keys(data).length === 0) {
      return null;
    }

    return {
      lastProcessedBatch: parseInt(data.lastProcessedBatch),
      lastProcessedOffset: parseInt(data.lastProcessedOffset),
      processedCount: parseInt(data.processedCount),
      failedCount: parseInt(data.failedCount),
      timestamp: new Date(data.timestamp)
    };
  }

  async removeCheckpoint(jobId: string): Promise<void> {
    await this.redis.del(`checkpoint:${jobId}`);
  }

  // Automatic checkpointing during batch processing
  createCheckpointer(jobId: string): ICheckpointer {
    let lastCheckpoint = Date.now();
    
    return {
      checkpoint: async (data: BatchCheckpoint) => {
        const now = Date.now();
        
        // Checkpoint based on time or batch count
        if (
          now - lastCheckpoint > this.config.intervalMs ||
          data.lastProcessedBatch % this.config.batchInterval === 0
        ) {
          await this.saveCheckpoint(jobId, data);
          lastCheckpoint = now;
        }
      }
    };
  }
}
```

## 5. Error Handling and Retry Logic

### Comprehensive Error Management

```typescript
// Error handler with retry strategies
export class DistributionErrorHandler {
  private retryStrategies: Map<ErrorType, IRetryStrategy>;

  constructor(
    private config: ErrorConfig,
    private alertService: IAlertService
  ) {
    this.initializeStrategies();
  }

  private initializeStrategies(): void {
    this.retryStrategies = new Map([
      [ErrorType.RATE_LIMIT, new ExponentialBackoffStrategy({
        initialDelay: 60000, // 1 minute
        maxDelay: 3600000,   // 1 hour
        factor: 2
      })],
      [ErrorType.NETWORK, new LinearBackoffStrategy({
        delay: 5000,         // 5 seconds
        maxAttempts: 5
      })],
      [ErrorType.AUTHENTICATION, new FixedDelayStrategy({
        delay: 10000,        // 10 seconds
        maxAttempts: 3
      })],
      [ErrorType.PLATFORM_ERROR, new ExponentialBackoffStrategy({
        initialDelay: 30000, // 30 seconds
        maxDelay: 600000,    // 10 minutes
        factor: 1.5
      })]
    ]);
  }

  async handleError(
    error: DistributionError,
    context: ErrorContext
  ): Promise<ErrorResolution> {
    // Classify error
    const errorType = this.classifyError(error);
    
    // Log error with context
    logger.error('Distribution error', {
      errorType,
      jobId: context.jobId,
      platformId: context.platformId,
      attempt: context.attemptNumber,
      error: error.message,
      stack: error.stack
    });

    // Get retry strategy
    const strategy = this.retryStrategies.get(errorType);
    
    if (!strategy) {
      return {
        action: 'fail',
        reason: 'No retry strategy for error type'
      };
    }

    // Check if we should retry
    const shouldRetry = await strategy.shouldRetry(context);
    
    if (!shouldRetry) {
      // Max retries exceeded
      await this.handleMaxRetriesExceeded(error, context);
      return {
        action: 'fail',
        reason: 'Max retries exceeded'
      };
    }

    // Calculate delay
    const delay = await strategy.getDelay(context);

    // Check for critical errors
    if (this.isCriticalError(error, context)) {
      await this.handleCriticalError(error, context);
    }

    return {
      action: 'retry',
      delay,
      strategy: errorType
    };
  }

  private classifyError(error: DistributionError): ErrorType {
    // Rate limit errors
    if (
      error.code === 'RATE_LIMIT_EXCEEDED' ||
      error.message.includes('rate limit') ||
      error.statusCode === 429
    ) {
      return ErrorType.RATE_LIMIT;
    }

    // Network errors
    if (
      error.code === 'ECONNREFUSED' ||
      error.code === 'ETIMEDOUT' ||
      error.code === 'ENOTFOUND'
    ) {
      return ErrorType.NETWORK;
    }

    // Authentication errors
    if (
      error.statusCode === 401 ||
      error.statusCode === 403 ||
      error.message.includes('authentication') ||
      error.message.includes('unauthorized')
    ) {
      return ErrorType.AUTHENTICATION;
    }

    // Platform-specific errors
    if (error.statusCode >= 500) {
      return ErrorType.PLATFORM_ERROR;
    }

    // Default to platform error
    return ErrorType.PLATFORM_ERROR;
  }

  private isCriticalError(
    error: DistributionError,
    context: ErrorContext
  ): boolean {
    // Authentication failures on first attempt
    if (
      this.classifyError(error) === ErrorType.AUTHENTICATION &&
      context.attemptNumber === 1
    ) {
      return true;
    }

    // Consistent failures across multiple jobs
    if (context.recentFailures > this.config.criticalFailureThreshold) {
      return true;
    }

    // Platform account issues
    if (error.message.includes('account suspended') ||
        error.message.includes('account disabled')) {
      return true;
    }

    return false;
  }

  private async handleCriticalError(
    error: DistributionError,
    context: ErrorContext
  ): Promise<void> {
    // Send immediate alert
    await this.alertService.sendAlert({
      severity: 'critical',
      type: 'distribution_failure',
      title: 'Critical Distribution Error',
      message: `Distribution to ${context.platformId} failing: ${error.message}`,
      context: {
        jobId: context.jobId,
        platformId: context.platformId,
        errorType: this.classifyError(error),
        attempts: context.attemptNumber
      }
    });

    // Disable platform if authentication fails
    if (this.classifyError(error) === ErrorType.AUTHENTICATION) {
      await this.disablePlatform(context.platformId, error);
    }
  }

  private async handleMaxRetriesExceeded(
    error: DistributionError,
    context: ErrorContext
  ): Promise<void> {
    // Move to dead letter queue
    await this.moveToDeadLetterQueue({
      jobId: context.jobId,
      error: error.message,
      context,
      timestamp: new Date()
    });

    // Send alert for persistent failures
    await this.alertService.sendAlert({
      severity: 'warning',
      type: 'max_retries_exceeded',
      title: 'Distribution Job Failed',
      message: `Job ${context.jobId} failed after ${context.attemptNumber} attempts`,
      context
    });
  }
}

// Retry strategies
export class ExponentialBackoffStrategy implements IRetryStrategy {
  constructor(private config: ExponentialBackoffConfig) {}

  async shouldRetry(context: ErrorContext): Promise<boolean> {
    return context.attemptNumber < (this.config.maxAttempts || 10);
  }

  async getDelay(context: ErrorContext): Promise<number> {
    const delay = Math.min(
      this.config.initialDelay * Math.pow(this.config.factor, context.attemptNumber - 1),
      this.config.maxDelay
    );

    // Add jitter to prevent thundering herd
    const jitter = Math.random() * delay * 0.1;
    return Math.floor(delay + jitter);
  }
}

// Circuit breaker for platform failures
export class PlatformCircuitBreaker {
  private states: Map<string, CircuitState>;
  private failures: Map<string, number>;
  private lastFailureTime: Map<string, Date>;

  constructor(private config: CircuitBreakerConfig) {
    this.states = new Map();
    this.failures = new Map();
    this.lastFailureTime = new Map();
  }

  async execute<T>(
    platformId: string,
    operation: () => Promise<T>
  ): Promise<T> {
    const state = this.getState(platformId);

    if (state === CircuitState.OPEN) {
      if (this.shouldAttemptReset(platformId)) {
        this.setState(platformId, CircuitState.HALF_OPEN);
      } else {
        throw new Error(`Circuit breaker OPEN for platform ${platformId}`);
      }
    }

    try {
      const result = await operation();
      this.onSuccess(platformId);
      return result;
    } catch (error) {
      this.onFailure(platformId);
      throw error;
    }
  }

  private getState(platformId: string): CircuitState {
    return this.states.get(platformId) || CircuitState.CLOSED;
  }

  private setState(platformId: string, state: CircuitState): void {
    this.states.set(platformId, state);
    
    logger.info('Circuit breaker state change', {
      platformId,
      state,
      failures: this.failures.get(platformId) || 0
    });
  }

  private onSuccess(platformId: string): void {
    const state = this.getState(platformId);
    
    if (state === CircuitState.HALF_OPEN) {
      // Reset after successful operation
      this.setState(platformId, CircuitState.CLOSED);
      this.failures.set(platformId, 0);
    }
  }

  private onFailure(platformId: string): void {
    const failures = (this.failures.get(platformId) || 0) + 1;
    this.failures.set(platformId, failures);
    this.lastFailureTime.set(platformId, new Date());

    const state = this.getState(platformId);

    if (state === CircuitState.HALF_OPEN) {
      // Failed during recovery, open again
      this.setState(platformId, CircuitState.OPEN);
    } else if (
      state === CircuitState.CLOSED &&
      failures >= this.config.failureThreshold
    ) {
      // Too many failures, open circuit
      this.setState(platformId, CircuitState.OPEN);
    }
  }

  private shouldAttemptReset(platformId: string): boolean {
    const lastFailure = this.lastFailureTime.get(platformId);
    if (!lastFailure) return true;

    const timeSinceFailure = Date.now() - lastFailure.getTime();
    return timeSinceFailure >= this.config.resetTimeout;
  }
}
```

## 6. Progress Tracking and Monitoring

### Real-time Progress Tracking

```typescript
// Progress tracker for distribution jobs
export class DistributionProgressTracker {
  private progressCache: Map<string, JobProgress>;
  private subscribers: Map<string, Set<ProgressSubscriber>>;

  constructor(
    private redis: Redis,
    private eventBus: IEventBus
  ) {
    this.progressCache = new Map();
    this.subscribers = new Map();
    this.startProgressSync();
  }

  async updateProgress(
    jobId: string,
    update: ProgressUpdate
  ): Promise<void> {
    // Get current progress
    let progress = this.progressCache.get(jobId);
    
    if (!progress) {
      progress = await this.loadProgress(jobId);
    }

    // Update progress
    progress = {
      ...progress,
      ...update,
      lastUpdated: new Date()
    };

    // Calculate derived metrics
    if (update.processedRecords !== undefined) {
      progress.percentComplete = Math.round(
        (update.processedRecords / progress.totalRecords) * 100
      );
      
      const elapsed = Date.now() - progress.startTime.getTime();
      progress.estimatedTimeRemaining = this.estimateTimeRemaining(
        progress.processedRecords,
        progress.totalRecords,
        elapsed
      );
      
      progress.recordsPerSecond = Math.round(
        progress.processedRecords / (elapsed / 1000)
      );
    }

    // Save to cache and Redis
    this.progressCache.set(jobId, progress);
    await this.saveProgress(jobId, progress);

    // Notify subscribers
    await this.notifySubscribers(jobId, progress);

    // Emit event for significant milestones
    if (this.isMilestone(progress)) {
      await this.eventBus.emit('distribution.milestone', {
        jobId,
        milestone: progress.percentComplete,
        progress
      });
    }
  }

  async subscribeToProgress(
    jobId: string,
    subscriber: ProgressSubscriber
  ): Promise<() => void> {
    if (!this.subscribers.has(jobId)) {
      this.subscribers.set(jobId, new Set());
    }

    this.subscribers.get(jobId)!.add(subscriber);

    // Send current progress immediately
    const progress = await this.getProgress(jobId);
    if (progress) {
      subscriber.onProgress(progress);
    }

    // Return unsubscribe function
    return () => {
      const subs = this.subscribers.get(jobId);
      if (subs) {
        subs.delete(subscriber);
        if (subs.size === 0) {
          this.subscribers.delete(jobId);
        }
      }
    };
  }

  async getProgress(jobId: string): Promise<JobProgress | null> {
    // Check cache first
    const cached = this.progressCache.get(jobId);
    if (cached) return cached;

    // Load from Redis
    return await this.loadProgress(jobId);
  }

  private async loadProgress(jobId: string): Promise<JobProgress> {
    const key = `progress:${jobId}`;
    const data = await this.redis.hgetall(key);

    if (!data || Object.keys(data).length === 0) {
      // Initialize new progress
      return {
        jobId,
        status: 'pending',
        totalRecords: 0,
        processedRecords: 0,
        failedRecords: 0,
        percentComplete: 0,
        startTime: new Date(),
        lastUpdated: new Date(),
        platforms: {}
      };
    }

    return {
      jobId,
      status: data.status as JobStatus,
      totalRecords: parseInt(data.totalRecords),
      processedRecords: parseInt(data.processedRecords),
      failedRecords: parseInt(data.failedRecords),
      percentComplete: parseInt(data.percentComplete),
      startTime: new Date(data.startTime),
      lastUpdated: new Date(data.lastUpdated),
      endTime: data.endTime ? new Date(data.endTime) : undefined,
      estimatedTimeRemaining: data.estimatedTimeRemaining
        ? parseInt(data.estimatedTimeRemaining)
        : undefined,
      recordsPerSecond: data.recordsPerSecond
        ? parseInt(data.recordsPerSecond)
        : undefined,
      platforms: JSON.parse(data.platforms || '{}'),
      currentPhase: data.currentPhase,
      error: data.error
    };
  }

  private async saveProgress(
    jobId: string,
    progress: JobProgress
  ): Promise<void> {
    const key = `progress:${jobId}`;
    
    const data: Record<string, string> = {
      status: progress.status,
      totalRecords: progress.totalRecords.toString(),
      processedRecords: progress.processedRecords.toString(),
      failedRecords: progress.failedRecords.toString(),
      percentComplete: progress.percentComplete.toString(),
      startTime: progress.startTime.toISOString(),
      lastUpdated: progress.lastUpdated.toISOString(),
      platforms: JSON.stringify(progress.platforms)
    };

    if (progress.endTime) {
      data.endTime = progress.endTime.toISOString();
    }

    if (progress.estimatedTimeRemaining !== undefined) {
      data.estimatedTimeRemaining = progress.estimatedTimeRemaining.toString();
    }

    if (progress.recordsPerSecond !== undefined) {
      data.recordsPerSecond = progress.recordsPerSecond.toString();
    }

    if (progress.currentPhase) {
      data.currentPhase = progress.currentPhase;
    }

    if (progress.error) {
      data.error = progress.error;
    }

    await this.redis.hmset(key, data);
    await this.redis.expire(key, 86400); // 24 hours
  }

  private async notifySubscribers(
    jobId: string,
    progress: JobProgress
  ): Promise<void> {
    const subscribers = this.subscribers.get(jobId);
    if (!subscribers) return;

    const notifications = Array.from(subscribers).map(
      subscriber => subscriber.onProgress(progress)
    );

    await Promise.all(notifications);
  }

  private estimateTimeRemaining(
    processed: number,
    total: number,
    elapsedMs: number
  ): number | undefined {
    if (processed === 0) return undefined;

    const rate = processed / elapsedMs;
    const remaining = total - processed;
    return Math.round(remaining / rate);
  }

  private isMilestone(progress: JobProgress): boolean {
    const milestones = [25, 50, 75, 90, 95, 100];
    return milestones.includes(progress.percentComplete);
  }

  // WebSocket support for real-time updates
  createWebSocketHandler(): WebSocketHandler {
    return {
      handleConnection: async (ws: WebSocket, jobId: string) => {
        const unsubscribe = await this.subscribeToProgress(jobId, {
          onProgress: async (progress) => {
            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({
                type: 'progress',
                data: progress
              }));
            }
          }
        });

        ws.on('close', () => {
          unsubscribe();
        });
      }
    };
  }
}

// Monitoring service for all distribution jobs
export class DistributionMonitor {
  private metricsCollector: MetricsCollector;

  constructor(
    private jobQueue: IJobQueue,
    private progressTracker: DistributionProgressTracker,
    private alertService: IAlertService
  ) {
    this.metricsCollector = new MetricsCollector();
    this.startMonitoring();
  }

  private startMonitoring(): void {
    // Monitor queue health
    setInterval(() => this.checkQueueHealth(), 30000); // 30 seconds

    // Monitor job performance
    setInterval(() => this.checkJobPerformance(), 60000); // 1 minute

    // Monitor platform health
    setInterval(() => this.checkPlatformHealth(), 300000); // 5 minutes
  }

  private async checkQueueHealth(): Promise<void> {
    const metrics = await this.jobQueue.getQueueMetrics();

    // Check for queue backlog
    if (metrics.waiting > this.config.queueBacklogThreshold) {
      await this.alertService.sendAlert({
        severity: 'warning',
        type: 'queue_backlog',
        title: 'Distribution Queue Backlog',
        message: `${metrics.waiting} jobs waiting in queue`,
        metrics
      });
    }

    // Check for stalled jobs
    if (metrics.stalled > 0) {
      await this.alertService.sendAlert({
        severity: 'error',
        type: 'stalled_jobs',
        title: 'Stalled Distribution Jobs',
        message: `${metrics.stalled} jobs are stalled`,
        metrics
      });
    }

    // Collect metrics
    this.metricsCollector.gauge('distribution.queue.waiting', metrics.waiting);
    this.metricsCollector.gauge('distribution.queue.active', metrics.active);
    this.metricsCollector.gauge('distribution.queue.completed', metrics.completed);
    this.metricsCollector.gauge('distribution.queue.failed', metrics.failed);
  }

  private async checkJobPerformance(): Promise<void> {
    const activeJobs = await this.getActiveJobs();

    for (const job of activeJobs) {
      const progress = await this.progressTracker.getProgress(job.id);
      
      if (!progress) continue;

      // Check for slow jobs
      if (this.isJobSlow(progress)) {
        await this.alertService.sendAlert({
          severity: 'info',
          type: 'slow_job',
          title: 'Slow Distribution Job',
          message: `Job ${job.id} is processing slowly`,
          context: {
            jobId: job.id,
            recordsPerSecond: progress.recordsPerSecond,
            percentComplete: progress.percentComplete
          }
        });
      }

      // Collect performance metrics
      this.metricsCollector.histogram(
        'distribution.job.records_per_second',
        progress.recordsPerSecond || 0,
        { platform: job.platformId }
      );
    }
  }

  private async checkPlatformHealth(): Promise<void> {
    const platformMetrics = await this.getPlatformMetrics();

    for (const [platformId, metrics] of platformMetrics) {
      // Check error rate
      const errorRate = metrics.errors / metrics.total;
      
      if (errorRate > this.config.errorRateThreshold) {
        await this.alertService.sendAlert({
          severity: 'error',
          type: 'high_error_rate',
          title: 'High Platform Error Rate',
          message: `Platform ${platformId} has ${Math.round(errorRate * 100)}% error rate`,
          context: {
            platformId,
            metrics
          }
        });
      }

      // Collect platform metrics
      this.metricsCollector.gauge(
        'distribution.platform.success_rate',
        1 - errorRate,
        { platform: platformId }
      );
      
      this.metricsCollector.gauge(
        'distribution.platform.avg_duration',
        metrics.avgDuration,
        { platform: platformId }
      );
    }
  }

  private isJobSlow(progress: JobProgress): boolean {
    if (!progress.recordsPerSecond) return false;

    const expectedRate = this.config.expectedRecordsPerSecond[progress.platformId] || 1000;
    return progress.recordsPerSecond < expectedRate * 0.5; // 50% of expected
  }
}
```

## 7. Rate Limiting and Throttling

### Advanced Rate Limiting System

```typescript
// Token bucket rate limiter
export class TokenBucketRateLimiter implements IRateLimiter {
  private buckets: Map<string, TokenBucket>;

  constructor(private config: RateLimiterConfig) {
    this.buckets = new Map();
  }

  async acquire(
    key: string,
    tokens: number = 1
  ): Promise<RateLimitResult> {
    const bucket = this.getBucket(key);
    const now = Date.now();

    // Refill tokens
    bucket.refill(now);

    if (bucket.tokens >= tokens) {
      bucket.tokens -= tokens;
      return {
        allowed: true,
        remainingTokens: Math.floor(bucket.tokens),
        resetAt: new Date(now + bucket.refillInterval)
      };
    }

    // Calculate wait time
    const tokensNeeded = tokens - bucket.tokens;
    const waitTime = Math.ceil(
      (tokensNeeded / bucket.refillRate) * bucket.refillInterval
    );

    return {
      allowed: false,
      remainingTokens: Math.floor(bucket.tokens),
      retryAfter: waitTime,
      resetAt: new Date(now + waitTime)
    };
  }

  private getBucket(key: string): TokenBucket {
    if (!this.buckets.has(key)) {
      const config = this.getConfigForKey(key);
      this.buckets.set(key, new TokenBucket(config));
    }
    return this.buckets.get(key)!;
  }

  private getConfigForKey(key: string): BucketConfig {
    // Platform-specific configurations
    const platformConfigs: Record<string, BucketConfig> = {
      'meta': {
        capacity: 1000,
        refillRate: 100,
        refillInterval: 1000 // 100 requests per second
      },
      'google': {
        capacity: 500,
        refillRate: 50,
        refillInterval: 1000 // 50 requests per second
      },
      'linkedin': {
        capacity: 100,
        refillRate: 10,
        refillInterval: 1000 // 10 requests per second
      }
    };

    const platform = key.split(':')[0];
    return platformConfigs[platform] || this.config.default;
  }
}

class TokenBucket {
  tokens: number;
  lastRefill: number;

  constructor(private config: BucketConfig) {
    this.tokens = config.capacity;
    this.lastRefill = Date.now();
  }

  refill(now: number): void {
    const timePassed = now - this.lastRefill;
    const intervalsP assed = timePassed / this.config.refillInterval;
    const tokensToAdd = intervalsP assed * this.config.refillRate;

    this.tokens = Math.min(
      this.config.capacity,
      this.tokens + tokensToAdd
    );
    this.lastRefill = now;
  }
}

// Adaptive rate limiter
export class AdaptiveRateLimiter implements IRateLimiter {
  private limiter: TokenBucketRateLimiter;
  private metrics: Map<string, RateLimitMetrics>;
  private adjustmentInterval: NodeJS.Timer;

  constructor(
    private config: AdaptiveRateLimiterConfig,
    private platformMonitor: IPlatformMonitor
  ) {
    this.limiter = new TokenBucketRateLimiter(config.base);
    this.metrics = new Map();
    this.startAdaptation();
  }

  async acquire(
    key: string,
    tokens: number = 1
  ): Promise<RateLimitResult> {
    const result = await this.limiter.acquire(key, tokens);
    
    // Track metrics
    this.updateMetrics(key, result);

    return result;
  }

  private startAdaptation(): void {
    this.adjustmentInterval = setInterval(
      () => this.adjustRateLimits(),
      this.config.adjustmentIntervalMs
    );
  }

  private async adjustRateLimits(): Promise<void> {
    const platforms = await this.platformMonitor.getPlatforms();

    for (const platform of platforms) {
      const metrics = this.metrics.get(platform.id);
      if (!metrics) continue;

      const health = await this.platformMonitor.getHealth(platform.id);
      
      // Adjust based on platform health
      if (health.errorRate > this.config.errorThreshold) {
        // Reduce rate when errors are high
        await this.reduceRate(platform.id, 0.8);
      } else if (
        health.errorRate < this.config.errorThreshold * 0.5 &&
        metrics.throttleRate < 0.01
      ) {
        // Increase rate when platform is healthy
        await this.increaseRate(platform.id, 1.1);
      }

      // Reset metrics
      this.metrics.set(platform.id, {
        requests: 0,
        throttled: 0,
        errors: 0,
        throttleRate: 0
      });
    }
  }

  private updateMetrics(key: string, result: RateLimitResult): void {
    const platformId = key.split(':')[0];
    const metrics = this.metrics.get(platformId) || {
      requests: 0,
      throttled: 0,
      errors: 0,
      throttleRate: 0
    };

    metrics.requests++;
    if (!result.allowed) {
      metrics.throttled++;
    }
    
    metrics.throttleRate = metrics.throttled / metrics.requests;
    this.metrics.set(platformId, metrics);
  }
}

// Distributed rate limiter using Redis
export class DistributedRateLimiter implements IRateLimiter {
  constructor(
    private redis: Redis,
    private config: DistributedRateLimiterConfig
  ) {}

  async acquire(
    key: string,
    tokens: number = 1
  ): Promise<RateLimitResult> {
    const now = Date.now();
    const window = Math.floor(now / this.config.windowMs);
    const windowKey = `ratelimit:${key}:${window}`;

    // Use Redis pipeline for atomic operations
    const pipeline = this.redis.pipeline();
    
    // Increment counter
    pipeline.incrby(windowKey, tokens);
    
    // Set expiration on first use
    pipeline.expire(windowKey, Math.ceil(this.config.windowMs / 1000) + 1);
    
    // Get current count
    pipeline.get(windowKey);

    const results = await pipeline.exec();
    const currentCount = parseInt(results[2][1] as string);

    if (currentCount <= this.config.limit) {
      return {
        allowed: true,
        remainingTokens: this.config.limit - currentCount,
        resetAt: new Date((window + 1) * this.config.windowMs)
      };
    }

    // Over limit, rollback
    await this.redis.decrby(windowKey, tokens);

    return {
      allowed: false,
      remainingTokens: 0,
      retryAfter: this.config.windowMs - (now % this.config.windowMs),
      resetAt: new Date((window + 1) * this.config.windowMs)
    };
  }

  // Sliding window implementation for more accurate rate limiting
  async acquireSliding(
    key: string,
    tokens: number = 1
  ): Promise<RateLimitResult> {
    const now = Date.now();
    const windowStart = now - this.config.windowMs;
    const member = `${now}:${tokens}`;

    // Lua script for atomic sliding window
    const luaScript = `
      local key = KEYS[1]
      local now = tonumber(ARGV[1])
      local window_start = tonumber(ARGV[2])
      local limit = tonumber(ARGV[3])
      local member = ARGV[4]
      local tokens = tonumber(ARGV[5])

      -- Remove old entries
      redis.call('ZREMRANGEBYSCORE', key, 0, window_start)

      -- Count current tokens
      local current = 0
      local members = redis.call('ZRANGE', key, 0, -1, 'WITHSCORES')
      for i = 1, #members, 2 do
        local value = members[i]
        local count = tonumber(string.match(value, ':(%d+)$'))
        current = current + count
      end

      -- Check if we can add new tokens
      if current + tokens <= limit then
        redis.call('ZADD', key, now, member)
        redis.call('EXPIRE', key, math.ceil(ARGV[6]))
        return {1, limit - current - tokens}
      else
        return {0, limit - current}
      end
    `;

    const result = await this.redis.eval(
      luaScript,
      1,
      key,
      now,
      windowStart,
      this.config.limit,
      member,
      tokens,
      this.config.windowMs / 1000
    ) as [number, number];

    if (result[0] === 1) {
      return {
        allowed: true,
        remainingTokens: result[1],
        resetAt: new Date(now + this.config.windowMs)
      };
    }

    return {
      allowed: false,
      remainingTokens: result[1],
      retryAfter: this.config.windowMs,
      resetAt: new Date(now + this.config.windowMs)
    };
  }
}

// Throttling middleware for distribution workers
export class DistributionThrottler {
  private rateLimiters: Map<string, IRateLimiter>;

  constructor(
    private config: ThrottlerConfig,
    private redis: Redis
  ) {
    this.rateLimiters = new Map();
    this.initializeRateLimiters();
  }

  private initializeRateLimiters(): void {
    // Create rate limiters for each platform
    for (const [platform, limits] of Object.entries(this.config.platforms)) {
      this.rateLimiters.set(
        platform,
        new DistributedRateLimiter(this.redis, {
          limit: limits.requestsPerSecond,
          windowMs: 1000
        })
      );
    }
  }

  async throttle<T>(
    platformId: string,
    operation: () => Promise<T>,
    options: ThrottleOptions = {}
  ): Promise<T> {
    const rateLimiter = this.rateLimiters.get(platformId);
    if (!rateLimiter) {
      // No rate limiting configured
      return await operation();
    }

    const tokens = options.tokens || 1;
    let attempts = 0;
    const maxAttempts = options.maxAttempts || 10;

    while (attempts < maxAttempts) {
      const result = await rateLimiter.acquire(platformId, tokens);

      if (result.allowed) {
        try {
          return await operation();
        } catch (error) {
          // Check if error is rate limit related
          if (this.isRateLimitError(error)) {
            // Platform rate limited us despite our tracking
            await this.handlePlatformRateLimit(platformId, error);
          }
          throw error;
        }
      }

      // Wait before retrying
      const waitTime = result.retryAfter || 1000;
      await this.delay(waitTime);
      attempts++;
    }

    throw new Error(
      `Rate limit exceeded for ${platformId} after ${maxAttempts} attempts`
    );
  }

  private isRateLimitError(error: any): boolean {
    return (
      error.statusCode === 429 ||
      error.code === 'RATE_LIMIT_EXCEEDED' ||
      error.message?.toLowerCase().includes('rate limit')
    );
  }

  private async handlePlatformRateLimit(
    platformId: string,
    error: any
  ): Promise<void> {
    logger.warn('Platform rate limit detected', {
      platformId,
      error: error.message
    });

    // Reduce our rate limit to match platform's actual limit
    const currentLimiter = this.rateLimiters.get(platformId);
    if (currentLimiter instanceof AdaptiveRateLimiter) {
      await currentLimiter.reduceRate(platformId, 0.5);
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

## Summary

This section covered the complete distribution engine implementation including:

1. **Distribution Engine Architecture**: Core system for managing audience distribution across platforms
2. **Job Queue Implementation**: Redis-based queue with priority handling and dead letter queues
3. **Platform Workers**: Specialized workers for Meta, Google Ads, and other platforms
4. **Batch Processing**: Efficient processing of large audiences with checkpointing
5. **Error Handling**: Comprehensive retry strategies and circuit breakers
6. **Progress Tracking**: Real-time monitoring with WebSocket support
7. **Rate Limiting**: Adaptive throttling to respect platform limits

The implementation provides enterprise-grade distribution capabilities with:
- Fault tolerance through retry mechanisms
- Scalability through parallel processing
- Reliability through checkpointing and recovery
- Observability through comprehensive monitoring
- Performance through intelligent batching and rate limiting