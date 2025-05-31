# Activation Manager - Implementation Guide (Part 3)

## Authentication and Authorization

### JWT-Based Authentication System

#### 1. Authentication Service Implementation
```typescript
// src/modules/auth/services/auth.service.ts
import { injectable, inject } from 'inversify';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { UserService } from '@/modules/user/services/user.service';
import { RefreshTokenService } from './refresh-token.service';
import { AuditService } from '@/modules/audit/services/audit.service';
import { 
  InvalidCredentialsException, 
  TokenExpiredException,
  InvalidRefreshTokenException 
} from '@/common/errors';

interface LoginDto {
  email: string;
  password: string;
  ipAddress?: string;
  userAgent?: string;
}

interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

@injectable()
export class AuthService {
  constructor(
    @inject(UserService) private userService: UserService,
    @inject(RefreshTokenService) private refreshTokenService: RefreshTokenService,
    @inject(AuditService) private auditService: AuditService
  ) {}

  async login(dto: LoginDto): Promise<AuthTokens> {
    // Find user by email
    const user = await this.userService.findByEmail(dto.email);
    
    if (!user) {
      await this.logFailedLogin(dto.email, dto.ipAddress);
      throw new InvalidCredentialsException();
    }

    // Verify password
    const isValidPassword = await bcrypt.compare(dto.password, user.passwordHash);
    
    if (!isValidPassword) {
      await this.logFailedLogin(dto.email, dto.ipAddress);
      throw new InvalidCredentialsException();
    }

    // Generate tokens
    const tokens = await this.generateTokens(user);

    // Log successful login
    await this.auditService.log({
      userId: user.id,
      action: 'LOGIN',
      entityType: 'USER',
      entityId: user.id,
      ipAddress: dto.ipAddress,
      userAgent: dto.userAgent,
    });

    return tokens;
  }

  async refresh(refreshToken: string): Promise<AuthTokens> {
    // Verify refresh token
    const tokenData = await this.refreshTokenService.verify(refreshToken);
    
    if (!tokenData) {
      throw new InvalidRefreshTokenException();
    }

    // Get user
    const user = await this.userService.findById(tokenData.userId);
    
    if (!user) {
      throw new InvalidRefreshTokenException();
    }

    // Revoke old refresh token
    await this.refreshTokenService.revoke(refreshToken);

    // Generate new tokens
    const tokens = await this.generateTokens(user);

    return tokens;
  }

  async logout(accessToken: string, refreshToken?: string): Promise<void> {
    // Decode access token to get user ID
    const decoded = jwt.decode(accessToken) as any;
    
    if (decoded && decoded.userId) {
      // Add access token to blacklist
      await this.blacklistAccessToken(accessToken, decoded.exp);
      
      // Revoke refresh token if provided
      if (refreshToken) {
        await this.refreshTokenService.revoke(refreshToken);
      }

      // Log logout
      await this.auditService.log({
        userId: decoded.userId,
        action: 'LOGOUT',
        entityType: 'USER',
        entityId: decoded.userId,
      });
    }
  }

  async validateAccessToken(token: string): Promise<any> {
    try {
      // Check if token is blacklisted
      const isBlacklisted = await this.isTokenBlacklisted(token);
      if (isBlacklisted) {
        throw new TokenExpiredException();
      }

      // Verify token
      const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any;
      
      return decoded;
    } catch (error) {
      if (error instanceof jwt.TokenExpiredError) {
        throw new TokenExpiredException();
      }
      throw error;
    }
  }

  private async generateTokens(user: any): Promise<AuthTokens> {
    // Generate access token
    const accessToken = jwt.sign(
      {
        userId: user.id,
        email: user.email,
        role: user.role,
      },
      process.env.JWT_SECRET!,
      {
        expiresIn: process.env.JWT_EXPIRES_IN || '15m',
        issuer: 'activation-manager',
        audience: 'activation-manager-api',
      }
    );

    // Generate refresh token
    const refreshToken = await this.refreshTokenService.create(user.id);

    return {
      accessToken,
      refreshToken,
      expiresIn: 900, // 15 minutes in seconds
    };
  }

  private async blacklistAccessToken(token: string, expiry: number): Promise<void> {
    const ttl = expiry - Math.floor(Date.now() / 1000);
    if (ttl > 0) {
      await this.refreshTokenService.blacklistToken(token, ttl);
    }
  }

  private async isTokenBlacklisted(token: string): Promise<boolean> {
    return this.refreshTokenService.isBlacklisted(token);
  }

  private async logFailedLogin(email: string, ipAddress?: string): Promise<void> {
    await this.auditService.log({
      action: 'LOGIN_FAILED',
      entityType: 'USER',
      entityId: email,
      ipAddress,
    });
  }
}
```

#### 2. Refresh Token Service
```typescript
// src/modules/auth/services/refresh-token.service.ts
import { injectable, inject } from 'inversify';
import crypto from 'crypto';
import { Redis } from 'ioredis';
import { PrismaClient } from '@prisma/client';

@injectable()
export class RefreshTokenService {
  private readonly TOKEN_LENGTH = 64;
  private readonly TOKEN_TTL = 30 * 24 * 60 * 60; // 30 days in seconds

  constructor(
    @inject('Redis') private redis: Redis,
    @inject('Prisma') private prisma: PrismaClient
  ) {}

  async create(userId: string): Promise<string> {
    // Generate secure random token
    const token = crypto.randomBytes(this.TOKEN_LENGTH).toString('hex');
    
    // Store in Redis with TTL
    const key = `refresh_token:${token}`;
    await this.redis.setex(key, this.TOKEN_TTL, JSON.stringify({
      userId,
      createdAt: new Date().toISOString(),
    }));

    // Also store in database for persistence
    await this.prisma.refreshToken.create({
      data: {
        token,
        userId,
        expiresAt: new Date(Date.now() + this.TOKEN_TTL * 1000),
      },
    });

    return token;
  }

  async verify(token: string): Promise<{ userId: string } | null> {
    // Check Redis first
    const key = `refresh_token:${token}`;
    const data = await this.redis.get(key);
    
    if (data) {
      return JSON.parse(data);
    }

    // Fallback to database
    const dbToken = await this.prisma.refreshToken.findUnique({
      where: { token },
      include: { user: true },
    });

    if (dbToken && dbToken.expiresAt > new Date() && !dbToken.revokedAt) {
      // Restore to Redis
      await this.redis.setex(key, this.TOKEN_TTL, JSON.stringify({
        userId: dbToken.userId,
      }));

      return { userId: dbToken.userId };
    }

    return null;
  }

  async revoke(token: string): Promise<void> {
    // Remove from Redis
    const key = `refresh_token:${token}`;
    await this.redis.del(key);

    // Mark as revoked in database
    await this.prisma.refreshToken.updateMany({
      where: { token },
      data: { revokedAt: new Date() },
    });
  }

  async blacklistToken(token: string, ttl: number): Promise<void> {
    const key = `blacklist:${token}`;
    await this.redis.setex(key, ttl, '1');
  }

  async isBlacklisted(token: string): Promise<boolean> {
    const key = `blacklist:${token}`;
    const exists = await this.redis.exists(key);
    return exists === 1;
  }

  async revokeAllUserTokens(userId: string): Promise<void> {
    // Get all user's refresh tokens from database
    const tokens = await this.prisma.refreshToken.findMany({
      where: {
        userId,
        revokedAt: null,
      },
    });

    // Revoke each token
    for (const token of tokens) {
      await this.revoke(token.token);
    }
  }
}
```

### Role-Based Access Control (RBAC)

#### 1. Permission System
```typescript
// src/modules/auth/rbac/permissions.ts
export enum Permission {
  // Audience permissions
  AUDIENCE_VIEW = 'audience:view',
  AUDIENCE_CREATE = 'audience:create',
  AUDIENCE_UPDATE = 'audience:update',
  AUDIENCE_DELETE = 'audience:delete',
  AUDIENCE_EXPORT = 'audience:export',
  
  // Platform permissions
  PLATFORM_VIEW = 'platform:view',
  PLATFORM_CONNECT = 'platform:connect',
  PLATFORM_MANAGE = 'platform:manage',
  
  // Distribution permissions
  DISTRIBUTION_VIEW = 'distribution:view',
  DISTRIBUTION_CREATE = 'distribution:create',
  DISTRIBUTION_CANCEL = 'distribution:cancel',
  
  // Analytics permissions
  ANALYTICS_VIEW = 'analytics:view',
  ANALYTICS_EXPORT = 'analytics:export',
  
  // Admin permissions
  USER_MANAGE = 'user:manage',
  SYSTEM_CONFIGURE = 'system:configure',
  AUDIT_VIEW = 'audit:view',
}

export const RolePermissions: Record<string, Permission[]> = {
  admin: Object.values(Permission), // All permissions
  
  manager: [
    Permission.AUDIENCE_VIEW,
    Permission.AUDIENCE_CREATE,
    Permission.AUDIENCE_UPDATE,
    Permission.AUDIENCE_DELETE,
    Permission.AUDIENCE_EXPORT,
    Permission.PLATFORM_VIEW,
    Permission.PLATFORM_CONNECT,
    Permission.PLATFORM_MANAGE,
    Permission.DISTRIBUTION_VIEW,
    Permission.DISTRIBUTION_CREATE,
    Permission.DISTRIBUTION_CANCEL,
    Permission.ANALYTICS_VIEW,
    Permission.ANALYTICS_EXPORT,
  ],
  
  analyst: [
    Permission.AUDIENCE_VIEW,
    Permission.AUDIENCE_CREATE,
    Permission.AUDIENCE_UPDATE,
    Permission.PLATFORM_VIEW,
    Permission.DISTRIBUTION_VIEW,
    Permission.ANALYTICS_VIEW,
  ],
  
  viewer: [
    Permission.AUDIENCE_VIEW,
    Permission.PLATFORM_VIEW,
    Permission.DISTRIBUTION_VIEW,
    Permission.ANALYTICS_VIEW,
  ],
};
```

#### 2. Authorization Guards
```typescript
// src/common/guards/auth.guards.ts
import { Request, Response, NextFunction } from 'express';
import { Permission, RolePermissions } from '@/modules/auth/rbac/permissions';
import { ForbiddenException, UnauthorizedException } from '@/common/errors';

interface AuthRequest extends Request {
  user?: {
    id: string;
    email: string;
    role: string;
  };
}

export function requireAuth() {
  return (target: any, propertyKey: string, descriptor: PropertyDescriptor) => {
    const originalMethod = descriptor.value;

    descriptor.value = async function (
      req: AuthRequest,
      res: Response,
      next: NextFunction
    ) {
      if (!req.user) {
        return next(new UnauthorizedException('Authentication required'));
      }

      return originalMethod.call(this, req, res, next);
    };

    return descriptor;
  };
}

export function requirePermission(permission: Permission) {
  return (target: any, propertyKey: string, descriptor: PropertyDescriptor) => {
    const originalMethod = descriptor.value;

    descriptor.value = async function (
      req: AuthRequest,
      res: Response,
      next: NextFunction
    ) {
      if (!req.user) {
        return next(new UnauthorizedException('Authentication required'));
      }

      const userPermissions = RolePermissions[req.user.role] || [];
      
      if (!userPermissions.includes(permission)) {
        return next(new ForbiddenException('Insufficient permissions'));
      }

      return originalMethod.call(this, req, res, next);
    };

    return descriptor;
  };
}

export function requireRole(roles: string | string[]) {
  return (target: any, propertyKey: string, descriptor: PropertyDescriptor) => {
    const originalMethod = descriptor.value;
    const allowedRoles = Array.isArray(roles) ? roles : [roles];

    descriptor.value = async function (
      req: AuthRequest,
      res: Response,
      next: NextFunction
    ) {
      if (!req.user) {
        return next(new UnauthorizedException('Authentication required'));
      }

      if (!allowedRoles.includes(req.user.role)) {
        return next(new ForbiddenException('Insufficient role privileges'));
      }

      return originalMethod.call(this, req, res, next);
    };

    return descriptor;
  };
}

// Resource-based authorization
export function requireOwnership(resourceGetter: (req: AuthRequest) => Promise<any>) {
  return (target: any, propertyKey: string, descriptor: PropertyDescriptor) => {
    const originalMethod = descriptor.value;

    descriptor.value = async function (
      req: AuthRequest,
      res: Response,
      next: NextFunction
    ) {
      if (!req.user) {
        return next(new UnauthorizedException('Authentication required'));
      }

      try {
        const resource = await resourceGetter(req);
        
        if (!resource) {
          return next(new ForbiddenException('Resource not found'));
        }

        // Check if user owns the resource or is admin
        if (resource.createdBy !== req.user.id && req.user.role !== 'admin') {
          return next(new ForbiddenException('Access denied to this resource'));
        }

        // Attach resource to request for reuse
        (req as any).resource = resource;

        return originalMethod.call(this, req, res, next);
      } catch (error) {
        return next(error);
      }
    };

    return descriptor;
  };
}
```

### OAuth2 Integration

#### 1. OAuth2 Strategy Implementation
```typescript
// src/modules/auth/strategies/google.strategy.ts
import { injectable } from 'inversify';
import { OAuth2Strategy } from 'passport-google-oauth';
import { UserService } from '@/modules/user/services/user.service';

@injectable()
export class GoogleOAuth2Strategy {
  constructor(private userService: UserService) {}

  getStrategy() {
    return new OAuth2Strategy(
      {
        clientID: process.env.GOOGLE_CLIENT_ID!,
        clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
        callbackURL: '/api/v1/auth/google/callback',
      },
      async (accessToken, refreshToken, profile, done) => {
        try {
          // Find or create user
          let user = await this.userService.findByEmail(profile.emails![0].value);
          
          if (!user) {
            user = await this.userService.createOAuthUser({
              email: profile.emails![0].value,
              name: profile.displayName,
              provider: 'google',
              providerId: profile.id,
              avatar: profile.photos![0].value,
            });
          }

          return done(null, user);
        } catch (error) {
          return done(error, null);
        }
      }
    );
  }
}

// OAuth routes
router.get('/auth/google', passport.authenticate('google', { 
  scope: ['profile', 'email'] 
}));

router.get('/auth/google/callback',
  passport.authenticate('google', { session: false }),
  async (req, res) => {
    // Generate JWT tokens
    const tokens = await authService.generateTokensForUser(req.user);
    
    // Redirect to frontend with tokens
    res.redirect(`${process.env.FRONTEND_URL}/auth/callback?token=${tokens.accessToken}`);
  }
);
```

---

## Core Data Models Implementation

### Audience Model Implementation

#### 1. Audience Entity
```typescript
// src/modules/audience/entities/audience.entity.ts
import { 
  AudienceType, 
  AudienceStatus, 
  AudienceCriteria 
} from '@shared/types';

export class Audience {
  id: string;
  name: string;
  description?: string;
  type: AudienceType;
  subtype: string;
  criteria: AudienceCriteria[];
  estimatedSize: number;
  status: AudienceStatus;
  metadata: Record<string, any>;
  tags: string[];
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;

  constructor(partial: Partial<Audience>) {
    Object.assign(this, partial);
  }

  // Business logic methods
  isActive(): boolean {
    return this.status === AudienceStatus.ACTIVE;
  }

  isDraft(): boolean {
    return this.status === AudienceStatus.DRAFT;
  }

  canBeDistributed(): boolean {
    return this.isActive() && this.criteria.length > 0 && this.estimatedSize > 0;
  }

  canBeEdited(): boolean {
    return this.status !== AudienceStatus.ARCHIVED;
  }

  validateCriteria(): string[] {
    const errors: string[] = [];

    if (this.criteria.length === 0) {
      errors.push('At least one criterion is required');
    }

    // Check for duplicate criteria
    const seen = new Set<string>();
    for (const criterion of this.criteria) {
      const key = `${criterion.variableId}-${criterion.operator}`;
      if (seen.has(key)) {
        errors.push(`Duplicate criterion for variable ${criterion.variableId}`);
      }
      seen.add(key);
    }

    return errors;
  }

  // Serialization methods
  toJSON(): any {
    return {
      id: this.id,
      name: this.name,
      description: this.description,
      type: this.type,
      subtype: this.subtype,
      criteria: this.criteria,
      estimatedSize: this.estimatedSize,
      status: this.status,
      metadata: this.metadata,
      tags: this.tags,
      createdBy: this.createdBy,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt,
    };
  }

  toPublicJSON(): any {
    const json = this.toJSON();
    delete json.metadata.internalNotes;
    return json;
  }
}
```

#### 2. Audience Repository
```typescript
// src/modules/audience/repositories/audience.repository.ts
import { injectable, inject } from 'inversify';
import { PrismaClient, Prisma } from '@prisma/client';
import { Audience } from '../entities/audience.entity';
import { PaginatedResult, QueryOptions } from '@/common/types';

@injectable()
export class AudienceRepository {
  constructor(@inject('Prisma') private prisma: PrismaClient) {}

  async findAll(options: QueryOptions): Promise<PaginatedResult<Audience>> {
    const {
      page = 1,
      pageSize = 20,
      filters = {},
      sort = { field: 'createdAt', order: 'desc' },
      userId,
    } = options;

    // Build where clause
    const where: Prisma.AudienceWhereInput = {
      status: { not: 'archived' },
    };

    // Apply filters
    if (filters.search) {
      where.OR = [
        { name: { contains: filters.search, mode: 'insensitive' } },
        { description: { contains: filters.search, mode: 'insensitive' } },
      ];
    }

    if (filters.type) {
      where.type = filters.type;
    }

    if (filters.status) {
      where.status = filters.status;
    }

    if (userId && filters.onlyMine) {
      where.createdBy = userId;
    }

    // Get total count
    const total = await this.prisma.audience.count({ where });

    // Get paginated results
    const audiences = await this.prisma.audience.findMany({
      where,
      include: {
        criteria: {
          include: {
            variable: true,
          },
          orderBy: {
            order: 'asc',
          },
        },
        creator: {
          select: {
            id: true,
            name: true,
            email: true,
          },
        },
        _count: {
          select: {
            distributions: true,
          },
        },
      },
      skip: (page - 1) * pageSize,
      take: pageSize,
      orderBy: {
        [sort.field]: sort.order,
      },
    });

    return {
      data: audiences.map(a => new Audience(a)),
      meta: {
        page,
        pageSize,
        total,
        totalPages: Math.ceil(total / pageSize),
        hasNext: page < Math.ceil(total / pageSize),
        hasPrevious: page > 1,
      },
    };
  }

  async findById(id: string): Promise<Audience | null> {
    const audience = await this.prisma.audience.findUnique({
      where: { id },
      include: {
        criteria: {
          include: {
            variable: true,
          },
          orderBy: {
            order: 'asc',
          },
        },
        creator: {
          select: {
            id: true,
            name: true,
            email: true,
          },
        },
        distributions: {
          take: 5,
          orderBy: {
            createdAt: 'desc',
          },
        },
      },
    });

    return audience ? new Audience(audience) : null;
  }

  async create(data: Prisma.AudienceCreateInput): Promise<Audience> {
    const audience = await this.prisma.audience.create({
      data: {
        ...data,
        criteria: {
          create: data.criteria as any,
        },
      },
      include: {
        criteria: {
          include: {
            variable: true,
          },
        },
      },
    });

    return new Audience(audience);
  }

  async update(id: string, data: Partial<Audience>): Promise<Audience> {
    // Handle criteria updates separately
    const { criteria, ...updateData } = data;

    const audience = await this.prisma.$transaction(async (tx) => {
      // Update audience data
      await tx.audience.update({
        where: { id },
        data: updateData as any,
      });

      // Update criteria if provided
      if (criteria) {
        // Delete existing criteria
        await tx.audienceCriteria.deleteMany({
          where: { audienceId: id },
        });

        // Create new criteria
        await tx.audienceCriteria.createMany({
          data: criteria.map((c, index) => ({
            ...c,
            audienceId: id,
            order: index,
          })),
        });
      }

      // Return updated audience
      return tx.audience.findUnique({
        where: { id },
        include: {
          criteria: {
            include: {
              variable: true,
            },
            orderBy: {
              order: 'asc',
            },
          },
        },
      });
    });

    return new Audience(audience!);
  }

  async delete(id: string): Promise<void> {
    await this.prisma.audience.update({
      where: { id },
      data: { status: 'archived' },
    });
  }

  async duplicate(id: string, newName: string, userId: string): Promise<Audience> {
    const original = await this.findById(id);
    
    if (!original) {
      throw new Error('Audience not found');
    }

    const duplicated = await this.create({
      name: newName,
      description: `Duplicated from "${original.name}"`,
      type: original.type,
      subtype: original.subtype,
      criteria: {
        create: original.criteria.map(c => ({
          variableId: c.variableId,
          operator: c.operator,
          value: c.value,
          logicalOperator: c.logicalOperator,
        })),
      },
      metadata: original.metadata,
      tags: original.tags,
      status: 'draft',
      createdBy: userId,
    } as any);

    return duplicated;
  }

  async getStatistics(userId?: string): Promise<any> {
    const where = userId ? { createdBy: userId } : {};

    const [
      totalCount,
      activeCount,
      totalReach,
      typeDistribution,
    ] = await Promise.all([
      this.prisma.audience.count({ where }),
      this.prisma.audience.count({ 
        where: { ...where, status: 'active' } 
      }),
      this.prisma.audience.aggregate({
        where,
        _sum: { estimatedSize: true },
      }),
      this.prisma.audience.groupBy({
        by: ['type'],
        where,
        _count: true,
      }),
    ]);

    return {
      total: totalCount,
      active: activeCount,
      totalReach: totalReach._sum.estimatedSize || 0,
      byType: typeDistribution.reduce((acc, curr) => {
        acc[curr.type] = curr._count;
        return acc;
      }, {} as Record<string, number>),
    };
  }
}
```

### Variable Metadata Implementation

#### 1. Variable Service
```typescript
// src/modules/variable/services/variable.service.ts
import { injectable, inject } from 'inversify';
import { VariableRepository } from '../repositories/variable.repository';
import { CacheService } from '@/common/cache/cache.service';
import { Variable, VariableCategory } from '@shared/types';

@injectable()
export class VariableService {
  private readonly CACHE_TTL = 3600; // 1 hour
  private readonly CACHE_KEY = 'variables:all';

  constructor(
    @inject(VariableRepository) private variableRepo: VariableRepository,
    @inject(CacheService) private cache: CacheService
  ) {}

  async findAll(): Promise<Variable[]> {
    // Try cache first
    const cached = await this.cache.get<Variable[]>(this.CACHE_KEY);
    if (cached) return cached;

    // Get from database
    const variables = await this.variableRepo.findAll({
      where: { isActive: true },
      orderBy: [
        { category: 'asc' },
        { sortOrder: 'asc' },
      ],
    });

    // Cache the result
    await this.cache.set(this.CACHE_KEY, variables, this.CACHE_TTL);

    return variables;
  }

  async findById(id: string): Promise<Variable | null> {
    const cacheKey = `variable:${id}`;
    
    // Try cache
    const cached = await this.cache.get<Variable>(cacheKey);
    if (cached) return cached;

    // Get from database
    const variable = await this.variableRepo.findById(id);
    
    if (variable) {
      await this.cache.set(cacheKey, variable, this.CACHE_TTL);
    }

    return variable;
  }

  async findByCategory(category: VariableCategory): Promise<Variable[]> {
    const allVariables = await this.findAll();
    return allVariables.filter(v => v.category === category);
  }

  async getCategories(): Promise<VariableCategory[]> {
    const cacheKey = 'variable:categories';
    
    // Try cache
    const cached = await this.cache.get<VariableCategory[]>(cacheKey);
    if (cached) return cached;

    // Get unique categories
    const variables = await this.findAll();
    const categories = [...new Set(variables.map(v => v.category))];

    // Cache the result
    await this.cache.set(cacheKey, categories, this.CACHE_TTL);

    return categories as VariableCategory[];
  }

  async search(query: string): Promise<Variable[]> {
    const allVariables = await this.findAll();
    const lowerQuery = query.toLowerCase();

    return allVariables.filter(v => 
      v.name.toLowerCase().includes(lowerQuery) ||
      v.description?.toLowerCase().includes(lowerQuery) ||
      v.code.toLowerCase().includes(lowerQuery)
    );
  }

  async validateValue(
    variableId: string, 
    operator: string, 
    value: any
  ): Promise<{ valid: boolean; errors: string[] }> {
    const variable = await this.findById(variableId);
    
    if (!variable) {
      return { valid: false, errors: ['Variable not found'] };
    }

    const errors: string[] = [];

    // Check operator is valid for variable
    if (!variable.operators.includes(operator)) {
      errors.push(`Operator '${operator}' not allowed for variable '${variable.name}'`);
    }

    // Validate value based on data type
    switch (variable.dataType) {
      case 'number':
        if (operator === 'between') {
          if (!Array.isArray(value) || value.length !== 2) {
            errors.push('Between operator requires array of two numbers');
          } else if (typeof value[0] !== 'number' || typeof value[1] !== 'number') {
            errors.push('Values must be numbers');
          } else if (value[0] >= value[1]) {
            errors.push('First value must be less than second value');
          }
        } else if (operator === 'in' || operator === 'not_in') {
          if (!Array.isArray(value)) {
            errors.push('In/Not In operators require an array');
          } else if (!value.every(v => typeof v === 'number')) {
            errors.push('All values must be numbers');
          }
        } else {
          if (typeof value !== 'number') {
            errors.push('Value must be a number');
          }
        }
        break;

      case 'string':
        if (operator === 'in' || operator === 'not_in') {
          if (!Array.isArray(value)) {
            errors.push('In/Not In operators require an array');
          } else if (!value.every(v => typeof v === 'string')) {
            errors.push('All values must be strings');
          }
        } else {
          if (typeof value !== 'string') {
            errors.push('Value must be a string');
          }
        }
        break;

      case 'date':
        if (operator === 'between') {
          if (!Array.isArray(value) || value.length !== 2) {
            errors.push('Between operator requires array of two dates');
          } else {
            const date1 = new Date(value[0]);
            const date2 = new Date(value[1]);
            if (isNaN(date1.getTime()) || isNaN(date2.getTime())) {
              errors.push('Invalid date format');
            } else if (date1 >= date2) {
              errors.push('First date must be before second date');
            }
          }
        } else {
          const date = new Date(value);
          if (isNaN(date.getTime())) {
            errors.push('Invalid date format');
          }
        }
        break;

      case 'boolean':
        if (typeof value !== 'boolean') {
          errors.push('Value must be true or false');
        }
        break;

      case 'enum':
        if (variable.validationRules?.allowedValues) {
          if (!variable.validationRules.allowedValues.includes(value)) {
            errors.push(`Value must be one of: ${variable.validationRules.allowedValues.join(', ')}`);
          }
        }
        break;
    }

    // Apply custom validation rules
    if (variable.validationRules) {
      if (variable.validationRules.min !== undefined && value < variable.validationRules.min) {
        errors.push(`Value must be at least ${variable.validationRules.min}`);
      }
      if (variable.validationRules.max !== undefined && value > variable.validationRules.max) {
        errors.push(`Value must be at most ${variable.validationRules.max}`);
      }
      if (variable.validationRules.pattern) {
        const regex = new RegExp(variable.validationRules.pattern);
        if (!regex.test(value)) {
          errors.push(`Value does not match required format`);
        }
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  async seedVariables(): Promise<void> {
    const variables = getDefaultVariables(); // Implementation in separate file
    
    for (const variable of variables) {
      await this.variableRepo.upsert({
        where: { code: variable.code },
        update: variable,
        create: variable,
      });
    }

    // Clear cache
    await this.cache.invalidate('variables:*');
  }
}
```

#### 2. Default Variables Data
```typescript
// src/modules/variable/data/default-variables.ts
import { Variable, VariableCategory } from '@shared/types';

export function getDefaultVariables(): Partial<Variable>[] {
  return [
    // Demographics
    {
      code: 'age',
      name: 'Age',
      category: VariableCategory.DEMOGRAPHICS,
      dataType: 'number',
      operators: ['equals', 'greater_than', 'less_than', 'between'],
      description: 'User age in years',
      examples: ['25', '18-34', '65+'],
      validationRules: {
        min: 0,
        max: 120,
      },
      sortOrder: 1,
      isActive: true,
    },
    {
      code: 'gender',
      name: 'Gender',
      category: VariableCategory.DEMOGRAPHICS,
      dataType: 'enum',
      operators: ['equals', 'not_equals', 'in'],
      description: 'User gender',
      examples: ['male', 'female', 'other'],
      validationRules: {
        allowedValues: ['male', 'female', 'other', 'prefer_not_to_say'],
      },
      sortOrder: 2,
      isActive: true,
    },
    {
      code: 'household_income',
      name: 'Household Income',
      category: VariableCategory.DEMOGRAPHICS,
      dataType: 'number',
      operators: ['greater_than', 'less_than', 'between'],
      description: 'Annual household income in USD',
      examples: ['50000', '75000-100000'],
      validationRules: {
        min: 0,
        max: 10000000,
      },
      sortOrder: 3,
      isActive: true,
    },

    // Behavioral
    {
      code: 'purchase_frequency',
      name: 'Purchase Frequency',
      category: VariableCategory.BEHAVIORAL,
      dataType: 'number',
      operators: ['equals', 'greater_than', 'less_than', 'between'],
      description: 'Number of purchases in last 30 days',
      examples: ['5', '10+', '1-3'],
      validationRules: {
        min: 0,
      },
      sortOrder: 1,
      isActive: true,
    },
    {
      code: 'last_activity_days',
      name: 'Days Since Last Activity',
      category: VariableCategory.BEHAVIORAL,
      dataType: 'number',
      operators: ['equals', 'greater_than', 'less_than', 'between'],
      description: 'Number of days since last platform activity',
      examples: ['7', '30', '90+'],
      validationRules: {
        min: 0,
      },
      sortOrder: 2,
      isActive: true,
    },
    {
      code: 'engagement_score',
      name: 'Engagement Score',
      category: VariableCategory.BEHAVIORAL,
      dataType: 'number',
      operators: ['greater_than', 'less_than', 'between'],
      description: 'Calculated engagement score (0-100)',
      examples: ['80', '50-75'],
      validationRules: {
        min: 0,
        max: 100,
      },
      sortOrder: 3,
      isActive: true,
    },

    // Geographic
    {
      code: 'country',
      name: 'Country',
      category: VariableCategory.GEOGRAPHIC,
      dataType: 'string',
      operators: ['equals', 'not_equals', 'in', 'not_in'],
      description: 'Country code (ISO 3166-1 alpha-2)',
      examples: ['US', 'CA', 'GB'],
      validationRules: {
        pattern: '^[A-Z]{2}$',
      },
      sortOrder: 1,
      isActive: true,
    },
    {
      code: 'state',
      name: 'State/Province',
      category: VariableCategory.GEOGRAPHIC,
      dataType: 'string',
      operators: ['equals', 'not_equals', 'in', 'not_in'],
      description: 'State or province code',
      examples: ['CA', 'NY', 'TX'],
      sortOrder: 2,
      isActive: true,
    },
    {
      code: 'city',
      name: 'City',
      category: VariableCategory.GEOGRAPHIC,
      dataType: 'string',
      operators: ['equals', 'not_equals', 'in', 'not_in', 'contains'],
      description: 'City name',
      examples: ['New York', 'Los Angeles', 'Chicago'],
      sortOrder: 3,
      isActive: true,
    },
    {
      code: 'postal_code',
      name: 'Postal Code',
      category: VariableCategory.GEOGRAPHIC,
      dataType: 'string',
      operators: ['equals', 'in', 'not_in', 'contains'],
      description: 'Postal or ZIP code',
      examples: ['10001', '90210', 'M5V*'],
      sortOrder: 4,
      isActive: true,
    },

    // Technographic
    {
      code: 'device_type',
      name: 'Device Type',
      category: VariableCategory.TECHNOGRAPHIC,
      dataType: 'enum',
      operators: ['equals', 'not_equals', 'in'],
      description: 'Primary device type',
      examples: ['desktop', 'mobile', 'tablet'],
      validationRules: {
        allowedValues: ['desktop', 'mobile', 'tablet', 'smart_tv', 'other'],
      },
      sortOrder: 1,
      isActive: true,
    },
    {
      code: 'operating_system',
      name: 'Operating System',
      category: VariableCategory.TECHNOGRAPHIC,
      dataType: 'string',
      operators: ['equals', 'not_equals', 'in', 'contains'],
      description: 'Device operating system',
      examples: ['iOS', 'Android', 'Windows'],
      sortOrder: 2,
      isActive: true,
    },
    {
      code: 'browser',
      name: 'Browser',
      category: VariableCategory.TECHNOGRAPHIC,
      dataType: 'string',
      operators: ['equals', 'not_equals', 'in', 'contains'],
      description: 'Web browser',
      examples: ['Chrome', 'Safari', 'Firefox'],
      sortOrder: 3,
      isActive: true,
    },

    // Transactional
    {
      code: 'lifetime_value',
      name: 'Lifetime Value',
      category: VariableCategory.TRANSACTIONAL,
      dataType: 'number',
      operators: ['greater_than', 'less_than', 'between'],
      description: 'Total customer lifetime value in USD',
      examples: ['1000', '5000+', '100-500'],
      validationRules: {
        min: 0,
      },
      sortOrder: 1,
      isActive: true,
    },
    {
      code: 'average_order_value',
      name: 'Average Order Value',
      category: VariableCategory.TRANSACTIONAL,
      dataType: 'number',
      operators: ['greater_than', 'less_than', 'between'],
      description: 'Average transaction amount in USD',
      examples: ['50', '100-200', '500+'],
      validationRules: {
        min: 0,
      },
      sortOrder: 2,
      isActive: true,
    },
    {
      code: 'total_orders',
      name: 'Total Orders',
      category: VariableCategory.TRANSACTIONAL,
      dataType: 'number',
      operators: ['equals', 'greater_than', 'less_than', 'between'],
      description: 'Total number of orders placed',
      examples: ['1', '5+', '10-20'],
      validationRules: {
        min: 0,
      },
      sortOrder: 3,
      isActive: true,
    },

    // Add more variables for other categories...
  ];
}
```

This completes Part 3 of the implementation guide, covering authentication, authorization, and core data model implementations. The guide continues with specific feature implementations.