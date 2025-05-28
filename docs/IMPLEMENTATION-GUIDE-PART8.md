# Activation Manager Implementation Guide - Part 8: Analytics and Reporting System

## Table of Contents
1. [Analytics Architecture](#analytics-architecture)
2. [Data Collection Pipeline](#data-collection-pipeline)
3. [Real-time Analytics Engine](#real-time-analytics-engine)
4. [Reporting Dashboard](#reporting-dashboard)
5. [Performance Metrics](#performance-metrics)
6. [Data Visualization](#data-visualization)
7. [Export and Integration](#export-and-integration)

## 1. Analytics Architecture

### Core Analytics System Design

```typescript
// Analytics service interface
export interface IAnalyticsService {
  // Event tracking
  trackEvent(event: AnalyticsEvent): Promise<void>;
  trackBatch(events: AnalyticsEvent[]): Promise<void>;
  
  // Metrics
  recordMetric(metric: Metric): Promise<void>;
  getMetrics(query: MetricsQuery): Promise<MetricsResult>;
  
  // Reporting
  generateReport(params: ReportParams): Promise<Report>;
  scheduleReport(schedule: ReportSchedule): Promise<string>;
  
  // Real-time analytics
  getRealtimeStats(query: RealtimeQuery): Promise<RealtimeStats>;
  subscribeToMetrics(query: MetricsQuery, callback: MetricsCallback): Unsubscribe;
}

// Event types
export interface AnalyticsEvent {
  eventId: string;
  eventType: EventType;
  timestamp: Date;
  userId?: string;
  organizationId: string;
  sessionId?: string;
  properties: Record<string, any>;
  context: EventContext;
}

export enum EventType {
  // Audience events
  AUDIENCE_CREATED = 'audience.created',
  AUDIENCE_UPDATED = 'audience.updated',
  AUDIENCE_DELETED = 'audience.deleted',
  AUDIENCE_ACTIVATED = 'audience.activated',
  
  // Distribution events
  DISTRIBUTION_STARTED = 'distribution.started',
  DISTRIBUTION_PROGRESS = 'distribution.progress',
  DISTRIBUTION_COMPLETED = 'distribution.completed',
  DISTRIBUTION_FAILED = 'distribution.failed',
  
  // Platform events
  PLATFORM_CONNECTED = 'platform.connected',
  PLATFORM_DISCONNECTED = 'platform.disconnected',
  PLATFORM_ERROR = 'platform.error',
  
  // User events
  USER_LOGIN = 'user.login',
  USER_ACTION = 'user.action',
  USER_ERROR = 'user.error'
}

// Time-series database schema (InfluxDB)
export const analyticsSchema = `
-- Measurements for different event types
CREATE DATABASE activation_analytics;

-- Audience metrics
audience_metrics,org_id=UUID,audience_id=UUID size=i,rules=i,status="active" timestamp

-- Distribution metrics  
distribution_metrics,org_id=UUID,platform_id=UUID,job_id=UUID 
  records_processed=i,
  records_failed=i,
  duration_ms=i,
  status="completed" timestamp

-- Platform metrics
platform_metrics,org_id=UUID,platform_id=UUID 
  api_calls=i,
  error_count=i,
  response_time_ms=i,
  rate_limit_hits=i timestamp

-- User activity metrics
user_activity,org_id=UUID,user_id=UUID,action=STRING 
  duration_ms=i,
  success=b timestamp

-- System metrics
system_metrics,service=STRING,instance=STRING 
  cpu_usage=f,
  memory_usage=f,
  queue_size=i,
  active_jobs=i timestamp
`;

// Analytics implementation
export class AnalyticsService implements IAnalyticsService {
  private eventQueue: Queue<AnalyticsEvent>;
  private metricsBuffer: MetricsBuffer;
  
  constructor(
    private influxDB: InfluxDB,
    private clickhouse: ClickHouse,
    private redis: Redis,
    private config: AnalyticsConfig
  ) {
    this.eventQueue = new Queue();
    this.metricsBuffer = new MetricsBuffer(config.bufferSize);
    this.startProcessing();
  }

  async trackEvent(event: AnalyticsEvent): Promise<void> {
    // Validate event
    this.validateEvent(event);
    
    // Enrich event
    const enrichedEvent = await this.enrichEvent(event);
    
    // Add to queue for batch processing
    await this.eventQueue.enqueue(enrichedEvent);
    
    // Real-time processing for critical events
    if (this.isCriticalEvent(event)) {
      await this.processEventRealtime(enrichedEvent);
    }
  }

  async trackBatch(events: AnalyticsEvent[]): Promise<void> {
    // Validate all events
    events.forEach(event => this.validateEvent(event));
    
    // Enrich events in parallel
    const enrichedEvents = await Promise.all(
      events.map(event => this.enrichEvent(event))
    );
    
    // Batch insert
    await this.batchInsertEvents(enrichedEvents);
  }

  private async enrichEvent(event: AnalyticsEvent): Promise<AnalyticsEvent> {
    // Add server-side timestamp
    event.timestamp = event.timestamp || new Date();
    
    // Add geographic data
    if (event.context.ipAddress) {
      const geoData = await this.getGeoData(event.context.ipAddress);
      event.context.geo = geoData;
    }
    
    // Add user agent parsing
    if (event.context.userAgent) {
      event.context.device = this.parseUserAgent(event.context.userAgent);
    }
    
    // Add organization metadata
    const orgMetadata = await this.getOrgMetadata(event.organizationId);
    event.context.organization = orgMetadata;
    
    return event;
  }

  private async processEventRealtime(event: AnalyticsEvent): Promise<void> {
    // Update real-time counters
    const key = `realtime:${event.eventType}:${event.organizationId}`;
    await this.redis.hincrby(key, 'count', 1);
    await this.redis.expire(key, 3600); // 1 hour TTL
    
    // Publish to subscribers
    await this.redis.publish(
      `analytics:${event.organizationId}`,
      JSON.stringify(event)
    );
  }

  private startProcessing(): void {
    // Batch processing interval
    setInterval(async () => {
      await this.processBatch();
    }, this.config.batchIntervalMs);
    
    // Metrics aggregation interval
    setInterval(async () => {
      await this.aggregateMetrics();
    }, this.config.aggregationIntervalMs);
  }

  private async processBatch(): Promise<void> {
    const events = await this.eventQueue.dequeueMany(
      this.config.batchSize
    );
    
    if (events.length === 0) return;
    
    try {
      // Write to time-series database
      await this.writeToInflux(events);
      
      // Write to analytical database
      await this.writeToClickHouse(events);
      
      // Update aggregations
      await this.updateAggregations(events);
    } catch (error) {
      logger.error('Failed to process analytics batch', error);
      // Re-queue events
      await Promise.all(
        events.map(event => this.eventQueue.enqueue(event))
      );
    }
  }

  private async writeToInflux(events: AnalyticsEvent[]): Promise<void> {
    const points = events.map(event => this.eventToInfluxPoint(event));
    
    await this.influxDB.writePoints(points, {
      database: 'activation_analytics',
      precision: 'ms'
    });
  }

  private eventToInfluxPoint(event: AnalyticsEvent): IPoint {
    const measurement = this.getEventMeasurement(event.eventType);
    const tags = this.getEventTags(event);
    const fields = this.getEventFields(event);
    
    return {
      measurement,
      tags,
      fields,
      timestamp: event.timestamp
    };
  }
}
```

### Analytics Data Models

```typescript
// Metrics and reporting models
export interface Metric {
  name: string;
  value: number;
  type: MetricType;
  tags: Record<string, string>;
  timestamp: Date;
}

export enum MetricType {
  COUNTER = 'counter',
  GAUGE = 'gauge',
  HISTOGRAM = 'histogram',
  SUMMARY = 'summary'
}

export interface MetricsQuery {
  metrics: string[];
  timeRange: TimeRange;
  groupBy?: string[];
  filters?: MetricFilter[];
  aggregation?: AggregationType;
  interval?: string; // e.g., '1h', '1d'
}

export interface TimeRange {
  start: Date;
  end: Date;
}

export enum AggregationType {
  SUM = 'sum',
  AVG = 'avg',
  MIN = 'min',
  MAX = 'max',
  COUNT = 'count',
  P50 = 'p50',
  P95 = 'p95',
  P99 = 'p99'
}

// Report models
export interface Report {
  id: string;
  name: string;
  type: ReportType;
  organizationId: string;
  createdAt: Date;
  parameters: ReportParameters;
  data: ReportData;
  format: ReportFormat;
}

export enum ReportType {
  AUDIENCE_PERFORMANCE = 'audience_performance',
  DISTRIBUTION_SUMMARY = 'distribution_summary',
  PLATFORM_USAGE = 'platform_usage',
  COST_ANALYSIS = 'cost_analysis',
  ERROR_REPORT = 'error_report',
  CUSTOM = 'custom'
}

export interface ReportParameters {
  timeRange: TimeRange;
  audiences?: string[];
  platforms?: string[];
  metrics?: string[];
  dimensions?: string[];
  filters?: ReportFilter[];
}

export interface ReportData {
  summary: ReportSummary;
  timeSeries: TimeSeriesData[];
  breakdown: BreakdownData[];
  insights: Insight[];
}
```

## 2. Data Collection Pipeline

### Event Collection System

```typescript
// Event collector with batching and reliability
export class EventCollector {
  private buffer: EventBuffer;
  private retryQueue: Queue<AnalyticsEvent>;
  
  constructor(
    private analyticsService: IAnalyticsService,
    private config: CollectorConfig
  ) {
    this.buffer = new EventBuffer(config.bufferSize);
    this.retryQueue = new Queue();
    this.startCollector();
  }

  async collect(event: AnalyticsEvent): Promise<void> {
    // Add to buffer
    this.buffer.add(event);
    
    // Flush if buffer is full
    if (this.buffer.isFull()) {
      await this.flush();
    }
  }

  private async flush(): Promise<void> {
    const events = this.buffer.drain();
    
    if (events.length === 0) return;
    
    try {
      await this.analyticsService.trackBatch(events);
    } catch (error) {
      logger.error('Failed to flush events', error);
      // Add to retry queue
      await Promise.all(
        events.map(event => this.retryQueue.enqueue(event))
      );
    }
  }

  private startCollector(): void {
    // Periodic flush
    setInterval(() => this.flush(), this.config.flushIntervalMs);
    
    // Retry failed events
    setInterval(() => this.retryFailedEvents(), this.config.retryIntervalMs);
  }

  private async retryFailedEvents(): Promise<void> {
    const events = await this.retryQueue.dequeueMany(
      this.config.retryBatchSize
    );
    
    if (events.length > 0) {
      try {
        await this.analyticsService.trackBatch(events);
      } catch (error) {
        // Re-queue with exponential backoff
        await this.requeueWithBackoff(events);
      }
    }
  }
}

// Metrics collector with aggregation
export class MetricsCollector {
  private counters: Map<string, number>;
  private gauges: Map<string, number>;
  private histograms: Map<string, Histogram>;
  
  constructor(
    private metricsStore: IMetricsStore,
    private config: MetricsConfig
  ) {
    this.counters = new Map();
    this.gauges = new Map();
    this.histograms = new Map();
    this.startAggregation();
  }

  increment(name: string, tags?: Record<string, string>): void {
    const key = this.getMetricKey(name, tags);
    const current = this.counters.get(key) || 0;
    this.counters.set(key, current + 1);
  }

  gauge(name: string, value: number, tags?: Record<string, string>): void {
    const key = this.getMetricKey(name, tags);
    this.gauges.set(key, value);
  }

  histogram(name: string, value: number, tags?: Record<string, string>): void {
    const key = this.getMetricKey(name, tags);
    
    if (!this.histograms.has(key)) {
      this.histograms.set(key, new Histogram());
    }
    
    this.histograms.get(key)!.record(value);
  }

  private startAggregation(): void {
    setInterval(async () => {
      await this.flushMetrics();
    }, this.config.flushIntervalMs);
  }

  private async flushMetrics(): Promise<void> {
    const timestamp = new Date();
    const metrics: Metric[] = [];
    
    // Flush counters
    for (const [key, value] of this.counters) {
      const { name, tags } = this.parseMetricKey(key);
      metrics.push({
        name,
        value,
        type: MetricType.COUNTER,
        tags,
        timestamp
      });
    }
    this.counters.clear();
    
    // Flush gauges
    for (const [key, value] of this.gauges) {
      const { name, tags } = this.parseMetricKey(key);
      metrics.push({
        name,
        value,
        type: MetricType.GAUGE,
        tags,
        timestamp
      });
    }
    
    // Flush histograms
    for (const [key, histogram] of this.histograms) {
      const { name, tags } = this.parseMetricKey(key);
      const summary = histogram.summarize();
      
      // Record percentiles
      metrics.push({
        name: `${name}.p50`,
        value: summary.p50,
        type: MetricType.SUMMARY,
        tags,
        timestamp
      });
      
      metrics.push({
        name: `${name}.p95`,
        value: summary.p95,
        type: MetricType.SUMMARY,
        tags,
        timestamp
      });
      
      metrics.push({
        name: `${name}.p99`,
        value: summary.p99,
        type: MetricType.SUMMARY,
        tags,
        timestamp
      });
    }
    this.histograms.clear();
    
    // Store metrics
    if (metrics.length > 0) {
      await this.metricsStore.store(metrics);
    }
  }
}

// Distributed tracing integration
export class TracingCollector {
  private tracer: Tracer;
  
  constructor(
    private config: TracingConfig,
    private analyticsService: IAnalyticsService
  ) {
    this.tracer = new Tracer({
      serviceName: 'activation-manager',
      sampler: new ProbabilisticSampler(config.samplingRate),
      reporter: new CompositeReporter([
        new LoggingReporter(),
        new RemoteReporter({
          endpoint: config.jaegerEndpoint
        })
      ])
    });
  }

  startSpan(
    operation: string,
    parent?: SpanContext
  ): Span {
    const span = this.tracer.startSpan(operation, {
      childOf: parent
    });
    
    // Track span start
    this.trackSpanEvent(span, 'start');
    
    return span;
  }

  finishSpan(span: Span): void {
    span.finish();
    
    // Track span completion
    this.trackSpanEvent(span, 'finish');
    
    // Extract metrics from span
    const duration = span.finishTime - span.startTime;
    const tags = span.tags();
    
    // Record duration metric
    metricsCollector.histogram(
      `operation.duration`,
      duration,
      {
        operation: span.operationName,
        ...tags
      }
    );
  }

  private trackSpanEvent(span: Span, eventType: string): void {
    const event: AnalyticsEvent = {
      eventId: generateId(),
      eventType: EventType.USER_ACTION,
      timestamp: new Date(),
      organizationId: span.getTag('organization_id') as string,
      properties: {
        spanId: span.context().toSpanId(),
        traceId: span.context().toTraceId(),
        operation: span.operationName,
        eventType,
        tags: span.tags()
      },
      context: {
        service: 'activation-manager',
        version: process.env.APP_VERSION
      }
    };
    
    this.analyticsService.trackEvent(event).catch(error => {
      logger.error('Failed to track span event', error);
    });
  }
}
```

## 3. Real-time Analytics Engine

### Stream Processing System

```typescript
// Real-time analytics processor
export class RealtimeAnalyticsEngine {
  private kafkaConsumer: KafkaConsumer;
  private processors: Map<string, IStreamProcessor>;
  private stateStore: IStateStore;
  
  constructor(
    private config: RealtimeConfig,
    private redis: Redis,
    private websocket: WebSocketServer
  ) {
    this.processors = new Map();
    this.stateStore = new RedisStateStore(redis);
    this.initializeProcessors();
    this.startConsumer();
  }

  private initializeProcessors(): void {
    // Audience activity processor
    this.processors.set('audience_activity', new AudienceActivityProcessor());
    
    // Distribution performance processor
    this.processors.set('distribution_performance', new DistributionPerformanceProcessor());
    
    // Platform health processor
    this.processors.set('platform_health', new PlatformHealthProcessor());
    
    // Anomaly detection processor
    this.processors.set('anomaly_detection', new AnomalyDetectionProcessor());
  }

  private async startConsumer(): Promise<void> {
    this.kafkaConsumer = new KafkaConsumer({
      brokers: this.config.kafkaBrokers,
      groupId: 'realtime-analytics',
      topics: ['analytics-events']
    });

    await this.kafkaConsumer.connect();
    
    await this.kafkaConsumer.run({
      eachMessage: async ({ topic, partition, message }) => {
        await this.processMessage(message);
      }
    });
  }

  private async processMessage(message: KafkaMessage): Promise<void> {
    try {
      const event = JSON.parse(message.value.toString());
      
      // Process through relevant processors
      for (const [name, processor] of this.processors) {
        if (processor.canProcess(event)) {
          const result = await processor.process(event, this.stateStore);
          
          // Broadcast updates
          if (result.broadcast) {
            await this.broadcastUpdate(result);
          }
        }
      }
    } catch (error) {
      logger.error('Failed to process realtime event', error);
    }
  }

  private async broadcastUpdate(result: ProcessingResult): Promise<void> {
    const update = {
      type: 'realtime_update',
      metric: result.metric,
      value: result.value,
      timestamp: result.timestamp,
      metadata: result.metadata
    };

    // Broadcast to WebSocket clients
    this.websocket.broadcast(
      JSON.stringify(update),
      client => client.subscribedMetrics.includes(result.metric)
    );

    // Update Redis for API queries
    await this.redis.setex(
      `realtime:${result.metric}`,
      60, // 1 minute TTL
      JSON.stringify(update)
    );
  }
}

// Stream processor implementations
export class AudienceActivityProcessor implements IStreamProcessor {
  canProcess(event: AnalyticsEvent): boolean {
    return event.eventType.startsWith('audience.');
  }

  async process(
    event: AnalyticsEvent,
    stateStore: IStateStore
  ): Promise<ProcessingResult> {
    const key = `audience_activity:${event.organizationId}`;
    
    // Update counters
    await stateStore.increment(`${key}:total`);
    await stateStore.increment(`${key}:${event.eventType}`);
    
    // Update time-based metrics
    const hourKey = `${key}:${getHourBucket()}`;
    await stateStore.increment(hourKey);
    await stateStore.expire(hourKey, 86400); // 24 hour retention
    
    // Calculate rate
    const count = await stateStore.get(`${key}:total`);
    const rate = await this.calculateRate(key, count);
    
    return {
      metric: 'audience_activity_rate',
      value: rate,
      timestamp: new Date(),
      broadcast: true,
      metadata: {
        organizationId: event.organizationId,
        eventType: event.eventType
      }
    };
  }

  private async calculateRate(
    key: string,
    currentCount: number
  ): Promise<number> {
    // Get count from 1 minute ago
    const previousKey = `${key}:previous`;
    const previousCount = await stateStore.get(previousKey) || 0;
    
    // Update previous count
    await stateStore.set(previousKey, currentCount);
    
    // Calculate rate (events per minute)
    return currentCount - previousCount;
  }
}

// Anomaly detection processor
export class AnomalyDetectionProcessor implements IStreamProcessor {
  private detectors: Map<string, IAnomalyDetector>;

  constructor() {
    this.detectors = new Map([
      ['distribution_failure_rate', new ThresholdDetector({
        threshold: 0.1, // 10% failure rate
        windowSize: 300000 // 5 minutes
      })],
      ['api_response_time', new StatisticalDetector({
        method: 'zscore',
        threshold: 3, // 3 standard deviations
        baselineWindow: 3600000 // 1 hour
      })],
      ['audience_size_spike', new PercentageChangeDetector({
        threshold: 5, // 500% increase
        windowSize: 3600000 // 1 hour
      })]
    ]);
  }

  canProcess(event: AnalyticsEvent): boolean {
    return true; // Process all events for anomaly detection
  }

  async process(
    event: AnalyticsEvent,
    stateStore: IStateStore
  ): Promise<ProcessingResult> {
    const anomalies: Anomaly[] = [];

    for (const [metric, detector] of this.detectors) {
      const value = this.extractMetricValue(event, metric);
      
      if (value !== null) {
        const anomaly = await detector.detect(metric, value, stateStore);
        
        if (anomaly) {
          anomalies.push(anomaly);
          await this.handleAnomaly(anomaly, event);
        }
      }
    }

    if (anomalies.length > 0) {
      return {
        metric: 'anomalies_detected',
        value: anomalies.length,
        timestamp: new Date(),
        broadcast: true,
        metadata: {
          anomalies: anomalies.map(a => ({
            metric: a.metric,
            severity: a.severity,
            message: a.message
          }))
        }
      };
    }

    return {
      metric: 'anomaly_check',
      value: 0,
      timestamp: new Date(),
      broadcast: false
    };
  }

  private async handleAnomaly(
    anomaly: Anomaly,
    event: AnalyticsEvent
  ): Promise<void> {
    // Log anomaly
    logger.warn('Anomaly detected', {
      anomaly,
      event
    });

    // Send alert for high severity
    if (anomaly.severity === 'high') {
      await alertService.sendAlert({
        type: 'anomaly',
        severity: 'warning',
        title: `Anomaly detected: ${anomaly.metric}`,
        message: anomaly.message,
        context: {
          value: anomaly.value,
          threshold: anomaly.threshold,
          organizationId: event.organizationId
        }
      });
    }

    // Store anomaly for historical analysis
    await this.storeAnomaly(anomaly, event);
  }
}

// WebSocket handler for real-time updates
export class RealtimeWebSocketHandler {
  private clients: Map<string, WebSocketClient>;
  
  constructor(
    private analyticsEngine: RealtimeAnalyticsEngine,
    private config: WebSocketConfig
  ) {
    this.clients = new Map();
  }

  handleConnection(ws: WebSocket, request: IncomingMessage): void {
    const clientId = generateId();
    const client: WebSocketClient = {
      id: clientId,
      socket: ws,
      subscribedMetrics: [],
      organizationId: this.extractOrgId(request)
    };

    this.clients.set(clientId, client);

    ws.on('message', (data) => this.handleMessage(clientId, data));
    ws.on('close', () => this.handleDisconnect(clientId));
    ws.on('error', (error) => this.handleError(clientId, error));

    // Send initial data
    this.sendInitialData(client);
  }

  private async handleMessage(
    clientId: string,
    data: WebSocket.Data
  ): Promise<void> {
    const client = this.clients.get(clientId);
    if (!client) return;

    try {
      const message = JSON.parse(data.toString());

      switch (message.type) {
        case 'subscribe':
          await this.handleSubscribe(client, message.metrics);
          break;
          
        case 'unsubscribe':
          await this.handleUnsubscribe(client, message.metrics);
          break;
          
        case 'query':
          await this.handleQuery(client, message.query);
          break;
      }
    } catch (error) {
      logger.error('WebSocket message error', error);
      this.sendError(client, 'Invalid message format');
    }
  }

  private async handleSubscribe(
    client: WebSocketClient,
    metrics: string[]
  ): Promise<void> {
    // Validate metrics
    const validMetrics = metrics.filter(m => 
      this.isValidMetric(m) && this.hasAccess(client, m)
    );

    // Update subscriptions
    client.subscribedMetrics = [
      ...new Set([...client.subscribedMetrics, ...validMetrics])
    ];

    // Send current values
    for (const metric of validMetrics) {
      const value = await this.getCurrentValue(metric);
      if (value) {
        this.sendUpdate(client, {
          type: 'metric_update',
          metric,
          value
        });
      }
    }

    // Confirm subscription
    this.sendMessage(client, {
      type: 'subscribed',
      metrics: validMetrics
    });
  }
}
```

## 4. Reporting Dashboard

### Dashboard Components

```typescript
// Dashboard API
export class DashboardAPI {
  constructor(
    private analyticsService: IAnalyticsService,
    private cache: ICache
  ) {}

  // Get dashboard overview
  async getOverview(
    organizationId: string,
    timeRange: TimeRange
  ): Promise<DashboardOverview> {
    const cacheKey = `dashboard:overview:${organizationId}:${timeRange.start.getTime()}`;
    
    // Check cache
    const cached = await this.cache.get(cacheKey);
    if (cached) return cached;

    // Fetch metrics in parallel
    const [
      audienceStats,
      distributionStats,
      platformStats,
      errorStats
    ] = await Promise.all([
      this.getAudienceStats(organizationId, timeRange),
      this.getDistributionStats(organizationId, timeRange),
      this.getPlatformStats(organizationId, timeRange),
      this.getErrorStats(organizationId, timeRange)
    ]);

    const overview: DashboardOverview = {
      audienceStats,
      distributionStats,
      platformStats,
      errorStats,
      insights: await this.generateInsights({
        audienceStats,
        distributionStats,
        platformStats,
        errorStats
      })
    };

    // Cache for 5 minutes
    await this.cache.set(cacheKey, overview, 300);

    return overview;
  }

  private async getAudienceStats(
    organizationId: string,
    timeRange: TimeRange
  ): Promise<AudienceStats> {
    const query: MetricsQuery = {
      metrics: [
        'audience.created.count',
        'audience.size.sum',
        'audience.activated.count'
      ],
      timeRange,
      filters: [{ field: 'org_id', value: organizationId }],
      groupBy: ['status'],
      interval: '1d'
    };

    const result = await this.analyticsService.getMetrics(query);

    return {
      totalAudiences: result.data['audience.created.count'].total,
      totalMembers: result.data['audience.size.sum'].total,
      activeAudiences: result.data['audience.activated.count'].total,
      growth: this.calculateGrowth(result.data['audience.created.count'].series),
      distribution: result.data['audience.created.count'].breakdown
    };
  }

  private async getDistributionStats(
    organizationId: string,
    timeRange: TimeRange
  ): Promise<DistributionStats> {
    const query: MetricsQuery = {
      metrics: [
        'distribution.completed.count',
        'distribution.records_processed.sum',
        'distribution.duration.avg',
        'distribution.failed.count'
      ],
      timeRange,
      filters: [{ field: 'org_id', value: organizationId }],
      groupBy: ['platform_id'],
      interval: '1h'
    };

    const result = await this.analyticsService.getMetrics(query);

    return {
      totalDistributions: result.data['distribution.completed.count'].total,
      recordsDistributed: result.data['distribution.records_processed.sum'].total,
      avgDuration: result.data['distribution.duration.avg'].value,
      successRate: this.calculateSuccessRate(
        result.data['distribution.completed.count'].total,
        result.data['distribution.failed.count'].total
      ),
      platformBreakdown: this.aggregatePlatformStats(result.data)
    };
  }

  private async generateInsights(
    stats: DashboardStats
  ): Promise<Insight[]> {
    const insights: Insight[] = [];

    // Audience growth insight
    if (stats.audienceStats.growth > 20) {
      insights.push({
        type: 'positive',
        category: 'audience',
        title: 'Strong Audience Growth',
        message: `Audience creation increased by ${stats.audienceStats.growth}% compared to the previous period`,
        impact: 'high',
        recommendations: [
          'Consider increasing distribution frequency to leverage growing audiences',
          'Review audience quality metrics to ensure growth maintains standards'
        ]
      });
    }

    // Distribution performance insight
    if (stats.distributionStats.successRate < 0.95) {
      insights.push({
        type: 'warning',
        category: 'distribution',
        title: 'Distribution Success Rate Below Target',
        message: `Current success rate is ${(stats.distributionStats.successRate * 100).toFixed(1)}%`,
        impact: 'medium',
        recommendations: [
          'Review error logs for common failure patterns',
          'Check platform API limits and adjust batch sizes',
          'Consider implementing retry logic for failed distributions'
        ]
      });
    }

    // Platform-specific insights
    for (const [platform, platformStats] of Object.entries(stats.platformStats)) {
      if (platformStats.errorRate > 0.05) {
        insights.push({
          type: 'error',
          category: 'platform',
          title: `High Error Rate on ${platform}`,
          message: `${platform} is experiencing ${(platformStats.errorRate * 100).toFixed(1)}% error rate`,
          impact: 'high',
          recommendations: [
            `Verify ${platform} API credentials are valid`,
            'Check for platform-specific rate limits',
            'Review recent platform API changes'
          ]
        });
      }
    }

    return insights;
  }
}

// Dashboard UI components (React)
export const DashboardComponent: React.FC = () => {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>({
    start: subDays(new Date(), 7),
    end: new Date()
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, [timeRange]);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const data = await dashboardAPI.getOverview(
        currentOrganization.id,
        timeRange
      );
      setOverview(data);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <DashboardSkeleton />;
  if (!overview) return <EmptyState />;

  return (
    <div className="dashboard">
      <DashboardHeader 
        timeRange={timeRange}
        onTimeRangeChange={setTimeRange}
      />
      
      <div className="dashboard-grid">
        <MetricCard
          title="Total Audiences"
          value={overview.audienceStats.totalAudiences}
          change={overview.audienceStats.growth}
          icon={<AudienceIcon />}
        />
        
        <MetricCard
          title="Records Distributed"
          value={overview.distributionStats.recordsDistributed}
          format="number"
          icon={<DistributionIcon />}
        />
        
        <MetricCard
          title="Success Rate"
          value={overview.distributionStats.successRate}
          format="percentage"
          target={0.95}
          icon={<SuccessIcon />}
        />
        
        <MetricCard
          title="Active Platforms"
          value={Object.keys(overview.platformStats).length}
          icon={<PlatformIcon />}
        />
      </div>

      <div className="dashboard-charts">
        <ChartContainer title="Audience Growth">
          <LineChart
            data={overview.audienceStats.timeSeries}
            xAxis="date"
            yAxis="count"
            series={[
              { key: 'created', name: 'Created', color: '#10B981' },
              { key: 'activated', name: 'Activated', color: '#3B82F6' }
            ]}
          />
        </ChartContainer>

        <ChartContainer title="Distribution Performance">
          <AreaChart
            data={overview.distributionStats.timeSeries}
            xAxis="hour"
            yAxis="records"
            series={[
              { key: 'processed', name: 'Processed', color: '#8B5CF6' },
              { key: 'failed', name: 'Failed', color: '#EF4444' }
            ]}
            stacked
          />
        </ChartContainer>

        <ChartContainer title="Platform Usage">
          <BarChart
            data={overview.platformStats}
            xAxis="platform"
            yAxis="distributions"
            color="#F59E0B"
          />
        </ChartContainer>
      </div>

      <InsightsPanel insights={overview.insights} />
    </div>
  );
};

// Real-time dashboard updates
export const RealtimeDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<RealtimeMetrics>({});
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    connectWebSocket();
    return () => disconnectWebSocket();
  }, []);

  const connectWebSocket = () => {
    const ws = new WebSocket(WS_ENDPOINT);
    
    ws.onopen = () => {
      // Subscribe to metrics
      ws.send(JSON.stringify({
        type: 'subscribe',
        metrics: [
          'audience_activity_rate',
          'distribution_throughput',
          'platform_response_time',
          'error_rate'
        ]
      }));
    };

    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      if (update.type === 'metric_update') {
        setMetrics(prev => ({
          ...prev,
          [update.metric]: update.value
        }));
      }
    };

    wsRef.current = ws;
  };

  return (
    <div className="realtime-dashboard">
      <RealtimeMetric
        label="Audience Activity"
        value={metrics.audience_activity_rate || 0}
        unit="events/min"
        sparkline
      />
      
      <RealtimeMetric
        label="Distribution Throughput"
        value={metrics.distribution_throughput || 0}
        unit="records/sec"
        sparkline
      />
      
      <RealtimeMetric
        label="API Response Time"
        value={metrics.platform_response_time || 0}
        unit="ms"
        threshold={500}
      />
      
      <RealtimeMetric
        label="Error Rate"
        value={metrics.error_rate || 0}
        unit="%"
        threshold={5}
        inverse
      />
    </div>
  );
};
```

## 5. Performance Metrics

### Performance Monitoring System

```typescript
// Performance metrics collector
export class PerformanceMonitor {
  private metrics: Map<string, PerformanceMetric>;
  private observers: Map<string, PerformanceObserver>;
  
  constructor(
    private metricsStore: IMetricsStore,
    private config: PerformanceConfig
  ) {
    this.metrics = new Map();
    this.observers = new Map();
    this.initializeMonitoring();
  }

  private initializeMonitoring(): void {
    // API performance monitoring
    this.monitorAPIPerformance();
    
    // Database performance monitoring
    this.monitorDatabasePerformance();
    
    // Queue performance monitoring
    this.monitorQueuePerformance();
    
    // System resource monitoring
    this.monitorSystemResources();
  }

  private monitorAPIPerformance(): void {
    // Express middleware for API monitoring
    app.use((req, res, next) => {
      const start = process.hrtime.bigint();
      const method = req.method;
      const route = req.route?.path || req.path;

      res.on('finish', () => {
        const duration = Number(process.hrtime.bigint() - start) / 1e6; // Convert to ms
        
        // Record metrics
        this.recordAPIMetric({
          endpoint: `${method} ${route}`,
          duration,
          statusCode: res.statusCode,
          organizationId: req.user?.organizationId
        });
      });

      next();
    });
  }

  private recordAPIMetric(metric: APIMetric): void {
    // Update histogram
    metricsCollector.histogram(
      'api.request.duration',
      metric.duration,
      {
        method: metric.endpoint.split(' ')[0],
        endpoint: metric.endpoint,
        status: metric.statusCode.toString()
      }
    );

    // Count requests
    metricsCollector.increment('api.request.count', {
      endpoint: metric.endpoint,
      status: metric.statusCode.toString()
    });

    // Track errors
    if (metric.statusCode >= 400) {
      metricsCollector.increment('api.request.errors', {
        endpoint: metric.endpoint,
        status: metric.statusCode.toString()
      });
    }

    // Organization-specific metrics
    if (metric.organizationId) {
      metricsCollector.increment(`org.${metric.organizationId}.api.requests`);
    }
  }

  private monitorDatabasePerformance(): void {
    // Prisma query event monitoring
    prisma.$on('query', (event) => {
      metricsCollector.histogram(
        'database.query.duration',
        event.duration,
        {
          model: event.model,
          action: event.action
        }
      );

      // Slow query detection
      if (event.duration > this.config.slowQueryThreshold) {
        logger.warn('Slow database query detected', {
          query: event.query,
          duration: event.duration,
          params: event.params
        });

        metricsCollector.increment('database.slow_queries', {
          model: event.model,
          action: event.action
        });
      }
    });

    // Connection pool monitoring
    setInterval(() => {
      const poolStats = prisma.$pool.stats();
      
      metricsCollector.gauge('database.pool.size', poolStats.size);
      metricsCollector.gauge('database.pool.available', poolStats.available);
      metricsCollector.gauge('database.pool.waiting', poolStats.waiting);
    }, 10000); // Every 10 seconds
  }

  private monitorQueuePerformance(): void {
    // Bull queue event monitoring
    queues.forEach((queue, name) => {
      queue.on('completed', (job, result) => {
        const duration = job.finishedOn - job.processedOn;
        
        metricsCollector.histogram(
          'queue.job.duration',
          duration,
          {
            queue: name,
            jobType: job.name
          }
        );

        metricsCollector.increment('queue.job.completed', {
          queue: name,
          jobType: job.name
        });
      });

      queue.on('failed', (job, error) => {
        metricsCollector.increment('queue.job.failed', {
          queue: name,
          jobType: job.name,
          error: error.name
        });
      });

      // Queue depth monitoring
      setInterval(async () => {
        const counts = await queue.getJobCounts();
        
        metricsCollector.gauge('queue.depth.waiting', counts.waiting, { queue: name });
        metricsCollector.gauge('queue.depth.active', counts.active, { queue: name });
        metricsCollector.gauge('queue.depth.delayed', counts.delayed, { queue: name });
        metricsCollector.gauge('queue.depth.failed', counts.failed, { queue: name });
      }, 30000); // Every 30 seconds
    });
  }

  private monitorSystemResources(): void {
    setInterval(() => {
      // CPU usage
      const cpuUsage = process.cpuUsage();
      metricsCollector.gauge(
        'system.cpu.usage',
        (cpuUsage.user + cpuUsage.system) / 1000
      );

      // Memory usage
      const memUsage = process.memoryUsage();
      metricsCollector.gauge('system.memory.heap_used', memUsage.heapUsed);
      metricsCollector.gauge('system.memory.heap_total', memUsage.heapTotal);
      metricsCollector.gauge('system.memory.rss', memUsage.rss);
      metricsCollector.gauge('system.memory.external', memUsage.external);

      // Event loop lag
      const start = process.hrtime.bigint();
      setImmediate(() => {
        const lag = Number(process.hrtime.bigint() - start) / 1e6;
        metricsCollector.gauge('system.eventloop.lag', lag);
      });

      // Active handles and requests
      metricsCollector.gauge(
        'system.handles.active',
        process._getActiveHandles().length
      );
      metricsCollector.gauge(
        'system.requests.active',
        process._getActiveRequests().length
      );
    }, 5000); // Every 5 seconds
  }

  // Custom performance marks
  startMeasurement(name: string): PerformanceMeasurement {
    const id = generateId();
    const start = process.hrtime.bigint();

    return {
      id,
      name,
      end: () => {
        const duration = Number(process.hrtime.bigint() - start) / 1e6;
        
        metricsCollector.histogram(
          `performance.${name}`,
          duration
        );

        return duration;
      }
    };
  }
}

// Application performance index (Apdex) calculation
export class ApdexCalculator {
  constructor(
    private config: ApdexConfig,
    private metricsStore: IMetricsStore
  ) {}

  async calculateApdex(
    metric: string,
    timeRange: TimeRange,
    threshold: number = 500 // ms
  ): Promise<ApdexScore> {
    const toleratedThreshold = threshold * 4;

    const query: MetricsQuery = {
      metrics: [metric],
      timeRange,
      aggregation: AggregationType.COUNT,
      groupBy: ['bucket']
    };

    const results = await this.metricsStore.query(query);
    
    let satisfied = 0;
    let tolerated = 0;
    let frustrated = 0;

    for (const dataPoint of results.data) {
      if (dataPoint.value <= threshold) {
        satisfied += dataPoint.count;
      } else if (dataPoint.value <= toleratedThreshold) {
        tolerated += dataPoint.count;
      } else {
        frustrated += dataPoint.count;
      }
    }

    const total = satisfied + tolerated + frustrated;
    const score = (satisfied + (tolerated / 2)) / total;

    return {
      score,
      level: this.getApdexLevel(score),
      satisfied,
      tolerated,
      frustrated,
      total,
      threshold
    };
  }

  private getApdexLevel(score: number): ApdexLevel {
    if (score >= 0.94) return 'excellent';
    if (score >= 0.85) return 'good';
    if (score >= 0.70) return 'fair';
    if (score >= 0.50) return 'poor';
    return 'unacceptable';
  }
}
```

## 6. Data Visualization

### Chart Components and Visualizations

```typescript
// Chart configuration factory
export class ChartFactory {
  static createLineChart(
    data: TimeSeriesData[],
    config: LineChartConfig
  ): ChartConfiguration {
    return {
      type: 'line',
      data: {
        labels: data.map(d => d.timestamp),
        datasets: config.series.map(series => ({
          label: series.name,
          data: data.map(d => d[series.key]),
          borderColor: series.color,
          backgroundColor: `${series.color}20`,
          tension: 0.4,
          fill: config.fill || false
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: config.showLegend !== false
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          x: {
            type: 'time',
            time: {
              unit: config.timeUnit || 'hour'
            }
          },
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => this.formatValue(value, config.format)
            }
          }
        }
      }
    };
  }

  static createHeatmap(
    data: HeatmapData,
    config: HeatmapConfig
  ): ChartConfiguration {
    const chartData = this.processHeatmapData(data);

    return {
      type: 'matrix',
      data: chartData,
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              title: (context) => {
                const dataPoint = context[0].raw;
                return `${dataPoint.x} - ${dataPoint.y}`;
              },
              label: (context) => {
                return `Value: ${context.raw.v}`;
              }
            }
          }
        },
        scales: {
          x: {
            type: 'category',
            labels: config.xLabels,
            offset: true
          },
          y: {
            type: 'category',
            labels: config.yLabels,
            offset: true
          }
        },
        elements: {
          rectangle: {
            borderWidth: 1,
            borderColor: 'rgba(0,0,0,0.1)'
          }
        }
      }
    };
  }

  static createSankeyDiagram(
    data: SankeyData,
    config: SankeyConfig
  ): D3Configuration {
    return {
      type: 'sankey',
      data: {
        nodes: data.nodes.map(node => ({
          id: node.id,
          name: node.name,
          color: node.color || config.defaultColor
        })),
        links: data.links.map(link => ({
          source: link.source,
          target: link.target,
          value: link.value,
          color: link.color || config.linkColor
        }))
      },
      options: {
        nodeWidth: config.nodeWidth || 15,
        nodePadding: config.nodePadding || 10,
        iterations: config.iterations || 32,
        extent: [[1, 1], [config.width - 1, config.height - 5]]
      }
    };
  }

  private static formatValue(value: number, format?: string): string {
    switch (format) {
      case 'percentage':
        return `${(value * 100).toFixed(1)}%`;
      case 'bytes':
        return this.formatBytes(value);
      case 'duration':
        return this.formatDuration(value);
      case 'number':
        return value.toLocaleString();
      default:
        return value.toString();
    }
  }
}

// Custom D3.js visualizations
export class CustomVisualizations {
  // Audience flow visualization
  static createAudienceFlow(
    container: HTMLElement,
    data: AudienceFlowData
  ): void {
    const width = container.clientWidth;
    const height = 600;

    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links).id(d => d.id))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => d.radius + 5));

    // Create links
    const link = svg.append('g')
      .selectAll('line')
      .data(data.links)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', d => Math.sqrt(d.value));

    // Create nodes
    const node = svg.append('g')
      .selectAll('circle')
      .data(data.nodes)
      .enter().append('circle')
      .attr('r', d => d.radius)
      .attr('fill', d => d.color)
      .call(this.drag(simulation));

    // Add labels
    const label = svg.append('g')
      .selectAll('text')
      .data(data.nodes)
      .enter().append('text')
      .text(d => d.name)
      .attr('font-size', 12)
      .attr('text-anchor', 'middle');

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);

      label
        .attr('x', d => d.x)
        .attr('y', d => d.y + 4);
    });
  }

  // Platform performance radar chart
  static createPerformanceRadar(
    container: HTMLElement,
    data: RadarData
  ): void {
    const width = 500;
    const height = 500;
    const margin = 80;
    const radius = Math.min(width, height) / 2 - margin;

    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${width/2},${height/2})`);

    // Scales
    const angleScale = d3.scaleLinear()
      .domain([0, data.axes.length])
      .range([0, 2 * Math.PI]);

    const radiusScale = d3.scaleLinear()
      .domain([0, 100])
      .range([0, radius]);

    // Draw axes
    const axes = g.selectAll('.axis')
      .data(data.axes)
      .enter().append('g')
      .attr('class', 'axis');

    axes.append('line')
      .attr('x1', 0)
      .attr('y1', 0)
      .attr('x2', (d, i) => radiusScale(100) * Math.cos(angleScale(i) - Math.PI/2))
      .attr('y2', (d, i) => radiusScale(100) * Math.sin(angleScale(i) - Math.PI/2))
      .attr('stroke', '#ddd');

    axes.append('text')
      .attr('x', (d, i) => (radiusScale(100) + 20) * Math.cos(angleScale(i) - Math.PI/2))
      .attr('y', (d, i) => (radiusScale(100) + 20) * Math.sin(angleScale(i) - Math.PI/2))
      .attr('text-anchor', 'middle')
      .text(d => d);

    // Draw data
    data.series.forEach((series, seriesIndex) => {
      const lineGenerator = d3.lineRadial()
        .angle((d, i) => angleScale(i))
        .radius(d => radiusScale(d))
        .curve(d3.curveLinearClosed);

      g.append('path')
        .datum(series.values)
        .attr('d', lineGenerator)
        .attr('fill', series.color)
        .attr('fill-opacity', 0.3)
        .attr('stroke', series.color)
        .attr('stroke-width', 2);

      // Add points
      g.selectAll(`.point-${seriesIndex}`)
        .data(series.values)
        .enter().append('circle')
        .attr('cx', (d, i) => radiusScale(d) * Math.cos(angleScale(i) - Math.PI/2))
        .attr('cy', (d, i) => radiusScale(d) * Math.sin(angleScale(i) - Math.PI/2))
        .attr('r', 4)
        .attr('fill', series.color);
    });
  }
}

// React components for interactive visualizations
export const InteractiveChart: React.FC<InteractiveChartProps> = ({
  type,
  data,
  config,
  onDataPointClick,
  onRangeSelect
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [selectedRange, setSelectedRange] = useState<TimeRange | null>(null);
  const [hoveredPoint, setHoveredPoint] = useState<DataPoint | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    const chart = createChart(chartRef.current, {
      type,
      data,
      config,
      interactive: true
    });

    // Add interaction handlers
    chart.on('click', (event: ChartEvent) => {
      if (onDataPointClick && event.dataPoint) {
        onDataPointClick(event.dataPoint);
      }
    });

    chart.on('brush', (event: BrushEvent) => {
      if (onRangeSelect && event.range) {
        setSelectedRange(event.range);
        onRangeSelect(event.range);
      }
    });

    chart.on('hover', (event: HoverEvent) => {
      setHoveredPoint(event.dataPoint);
    });

    return () => chart.destroy();
  }, [type, data, config]);

  return (
    <div className="interactive-chart">
      <div ref={chartRef} className="chart-container" />
      
      {hoveredPoint && (
        <Tooltip point={hoveredPoint} />
      )}
      
      {selectedRange && (
        <RangeDisplay range={selectedRange} />
      )}
    </div>
  );
};
```

## 7. Export and Integration

### Report Export System

```typescript
// Report exporter with multiple formats
export class ReportExporter {
  constructor(
    private templateEngine: ITemplateEngine,
    private pdfGenerator: IPDFGenerator,
    private config: ExportConfig
  ) {}

  async exportReport(
    report: Report,
    format: ExportFormat,
    options: ExportOptions = {}
  ): Promise<ExportResult> {
    switch (format) {
      case 'pdf':
        return await this.exportPDF(report, options);
      case 'excel':
        return await this.exportExcel(report, options);
      case 'csv':
        return await this.exportCSV(report, options);
      case 'json':
        return await this.exportJSON(report, options);
      case 'html':
        return await this.exportHTML(report, options);
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
  }

  private async exportPDF(
    report: Report,
    options: ExportOptions
  ): Promise<ExportResult> {
    // Generate HTML from template
    const html = await this.templateEngine.render('report-pdf', {
      report,
      options,
      charts: await this.renderChartsAsImages(report.data.charts)
    });

    // Generate PDF
    const pdf = await this.pdfGenerator.generate(html, {
      format: 'A4',
      margin: {
        top: '20mm',
        right: '20mm',
        bottom: '20mm',
        left: '20mm'
      },
      displayHeaderFooter: true,
      headerTemplate: this.getHeaderTemplate(report),
      footerTemplate: this.getFooterTemplate()
    });

    return {
      format: 'pdf',
      data: pdf,
      filename: `${report.name}-${Date.now()}.pdf`,
      mimeType: 'application/pdf'
    };
  }

  private async exportExcel(
    report: Report,
    options: ExportOptions
  ): Promise<ExportResult> {
    const workbook = new ExcelJS.Workbook();
    
    // Add metadata
    workbook.creator = 'Activation Manager';
    workbook.created = new Date();
    workbook.modified = new Date();

    // Summary sheet
    const summarySheet = workbook.addWorksheet('Summary');
    this.addSummaryData(summarySheet, report.data.summary);

    // Time series sheet
    if (report.data.timeSeries.length > 0) {
      const timeSeriesSheet = workbook.addWorksheet('Time Series');
      this.addTimeSeriesData(timeSeriesSheet, report.data.timeSeries);
    }

    // Breakdown sheets
    report.data.breakdown.forEach((breakdown, index) => {
      const sheet = workbook.addWorksheet(breakdown.name || `Breakdown ${index + 1}`);
      this.addBreakdownData(sheet, breakdown);
    });

    // Charts sheet with images
    if (report.data.charts && options.includeCharts) {
      const chartsSheet = workbook.addWorksheet('Charts');
      await this.addChartImages(chartsSheet, report.data.charts);
    }

    // Generate buffer
    const buffer = await workbook.xlsx.writeBuffer();

    return {
      format: 'excel',
      data: buffer,
      filename: `${report.name}-${Date.now()}.xlsx`,
      mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    };
  }

  private async renderChartsAsImages(
    charts: ChartData[]
  ): Promise<string[]> {
    const images: string[] = [];

    for (const chart of charts) {
      // Create headless chart instance
      const canvas = createCanvas(800, 400);
      const ctx = canvas.getContext('2d');
      
      // Render chart
      const chartInstance = new Chart(ctx, chart.config);
      
      // Convert to base64
      const image = canvas.toDataURL('image/png');
      images.push(image);
      
      // Cleanup
      chartInstance.destroy();
    }

    return images;
  }
}

// API integration for external systems
export class AnalyticsAPIIntegration {
  constructor(
    private analyticsService: IAnalyticsService,
    private authService: IAuthService
  ) {}

  // Webhook integration
  async setupWebhook(config: WebhookConfig): Promise<void> {
    const webhook = await this.createWebhook(config);

    // Subscribe to events
    eventBus.on(config.events, async (event) => {
      if (this.shouldSendWebhook(event, config)) {
        await this.sendWebhook(webhook, event);
      }
    });
  }

  private async sendWebhook(
    webhook: Webhook,
    event: AnalyticsEvent
  ): Promise<void> {
    const payload = {
      id: generateId(),
      timestamp: new Date(),
      event,
      metadata: {
        source: 'activation-manager',
        version: process.env.APP_VERSION
      }
    };

    // Sign payload
    const signature = this.signPayload(payload, webhook.secret);

    try {
      const response = await axios.post(webhook.url, payload, {
        headers: {
          'X-Webhook-Signature': signature,
          'X-Webhook-ID': webhook.id,
          'Content-Type': 'application/json'
        },
        timeout: 5000
      });

      // Log success
      await this.logWebhookDelivery(webhook.id, {
        status: 'success',
        statusCode: response.status,
        timestamp: new Date()
      });
    } catch (error) {
      // Log failure and retry
      await this.handleWebhookError(webhook, error);
    }
  }

  // Grafana integration
  async setupGrafanaDataSource(): Promise<void> {
    const datasource = {
      name: 'Activation Manager Analytics',
      type: 'prometheus',
      url: `${process.env.API_URL}/api/analytics/prometheus`,
      access: 'proxy',
      basicAuth: false,
      isDefault: false,
      jsonData: {
        httpMethod: 'POST',
        customQueryParameters: `org_id=${this.currentOrg.id}`
      }
    };

    // Register with Grafana
    await this.grafanaClient.createDataSource(datasource);

    // Import default dashboards
    await this.importGrafanaDashboards();
  }

  // Datadog integration
  async setupDatadogIntegration(apiKey: string): Promise<void> {
    const ddClient = new DatadogClient({ apiKey });

    // Create custom metrics
    const metrics = [
      {
        metric: 'activation_manager.audience.count',
        type: 'gauge',
        unit: 'audience',
        description: 'Number of audiences by status'
      },
      {
        metric: 'activation_manager.distribution.throughput',
        type: 'rate',
        unit: 'record',
        description: 'Distribution throughput in records per second'
      },
      {
        metric: 'activation_manager.platform.error_rate',
        type: 'gauge',
        unit: 'percent',
        description: 'Platform error rate percentage'
      }
    ];

    for (const metric of metrics) {
      await ddClient.createMetric(metric);
    }

    // Setup metric forwarding
    metricsCollector.on('flush', async (metrics) => {
      await this.forwardToDatadog(ddClient, metrics);
    });
  }

  // Slack integration for alerts
  async setupSlackIntegration(webhookUrl: string): Promise<void> {
    alertService.addChannel({
      name: 'slack',
      handler: async (alert) => {
        const message = this.formatSlackMessage(alert);
        
        await axios.post(webhookUrl, message);
      }
    });
  }

  private formatSlackMessage(alert: Alert): SlackMessage {
    const color = {
      'critical': '#FF0000',
      'warning': '#FFA500',
      'info': '#0000FF'
    }[alert.severity];

    return {
      attachments: [{
        color,
        title: alert.title,
        text: alert.message,
        fields: Object.entries(alert.context || {}).map(([key, value]) => ({
          title: key,
          value: String(value),
          short: true
        })),
        footer: 'Activation Manager',
        ts: Math.floor(Date.now() / 1000)
      }]
    };
  }
}

// Public API for analytics data
export class AnalyticsPublicAPI {
  constructor(
    private analyticsService: IAnalyticsService,
    private rateLimiter: IRateLimiter
  ) {}

  // RESTful endpoints
  setupRoutes(router: Router): void {
    // Get metrics
    router.get('/metrics', 
      this.authenticate,
      this.rateLimit,
      async (req, res) => {
        const query: MetricsQuery = {
          metrics: req.query.metrics?.split(',') || [],
          timeRange: {
            start: new Date(req.query.start),
            end: new Date(req.query.end || Date.now())
          },
          filters: this.parseFilters(req.query.filters),
          groupBy: req.query.groupBy?.split(','),
          interval: req.query.interval
        };

        const result = await this.analyticsService.getMetrics(query);
        res.json(result);
      }
    );

    // Get reports
    router.get('/reports/:id',
      this.authenticate,
      this.rateLimit,
      async (req, res) => {
        const report = await this.analyticsService.getReport(req.params.id);
        
        if (!report) {
          return res.status(404).json({ error: 'Report not found' });
        }

        res.json(report);
      }
    );

    // Export report
    router.get('/reports/:id/export',
      this.authenticate,
      this.rateLimit,
      async (req, res) => {
        const format = req.query.format as ExportFormat || 'pdf';
        const report = await this.analyticsService.getReport(req.params.id);
        
        if (!report) {
          return res.status(404).json({ error: 'Report not found' });
        }

        const exported = await reportExporter.exportReport(report, format);
        
        res.setHeader('Content-Type', exported.mimeType);
        res.setHeader('Content-Disposition', `attachment; filename="${exported.filename}"`);
        res.send(exported.data);
      }
    );

    // GraphQL endpoint
    router.use('/graphql',
      this.authenticate,
      graphqlHTTP({
        schema: analyticsSchema,
        rootValue: analyticsResolvers,
        graphiql: process.env.NODE_ENV === 'development'
      })
    );
  }

  // Prometheus metrics endpoint
  async prometheusMetrics(req: Request, res: Response): Promise<void> {
    const registry = new PrometheusRegistry();

    // Register custom metrics
    const audienceGauge = new Gauge({
      name: 'activation_manager_audiences_total',
      help: 'Total number of audiences',
      labelNames: ['organization', 'status']
    });

    const distributionCounter = new Counter({
      name: 'activation_manager_distributions_total',
      help: 'Total number of distributions',
      labelNames: ['organization', 'platform', 'status']
    });

    registry.registerMetric(audienceGauge);
    registry.registerMetric(distributionCounter);

    // Populate metrics
    const metrics = await this.getPrometheusMetrics(req.query.org_id);
    
    metrics.audiences.forEach(m => {
      audienceGauge.labels(m.organization, m.status).set(m.value);
    });

    metrics.distributions.forEach(m => {
      distributionCounter.labels(m.organization, m.platform, m.status).inc(m.value);
    });

    // Return in Prometheus format
    res.set('Content-Type', registry.contentType);
    res.send(registry.metrics());
  }
}
```

## Summary

This section covered the complete analytics and reporting system including:

1. **Analytics Architecture**: Event-driven system with time-series and analytical databases
2. **Data Collection Pipeline**: Reliable event collection with batching and retry mechanisms
3. **Real-time Analytics**: Stream processing with WebSocket broadcasting
4. **Reporting Dashboard**: Interactive dashboards with real-time updates
5. **Performance Metrics**: Comprehensive monitoring of API, database, and system performance
6. **Data Visualization**: Rich visualizations using Chart.js and D3.js
7. **Export and Integration**: Multi-format export and integrations with external systems

The implementation provides enterprise-grade analytics capabilities with:
- Scalable data collection and processing
- Real-time insights and anomaly detection
- Rich visualization options
- Flexible export formats
- External system integrations
- Performance monitoring and optimization