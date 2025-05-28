# DNS Configuration for tobermory.ai

## Required DNS Records in Cloudflare

### 1. Delete ALL existing A records for tobermory.ai

### 2. Add these A records (for the root domain):
| Type | Name | Content | Proxy Status |
|------|------|---------|--------------|
| A | @ | 216.239.32.21 | DNS only (gray cloud) |
| A | @ | 216.239.34.21 | DNS only (gray cloud) |
| A | @ | 216.239.36.21 | DNS only (gray cloud) |
| A | @ | 216.239.38.21 | DNS only (gray cloud) |

### 3. Add these AAAA records (for IPv6):
| Type | Name | Content | Proxy Status |
|------|------|---------|--------------|
| AAAA | @ | 2001:4860:4802:32::15 | DNS only (gray cloud) |
| AAAA | @ | 2001:4860:4802:34::15 | DNS only (gray cloud) |
| AAAA | @ | 2001:4860:4802:36::15 | DNS only (gray cloud) |
| AAAA | @ | 2001:4860:4802:38::15 | DNS only (gray cloud) |

### 4. Add CNAME for API subdomain:
| Type | Name | Content | Proxy Status |
|------|------|---------|--------------|
| CNAME | api | ghs.googlehosted.com | DNS only (gray cloud) |

## Important Notes:
- **ALL records must have Cloudflare proxy DISABLED** (gray cloud icon)
- Delete any existing A records pointing to 104.21.x.x
- The @ symbol means the root domain (tobermory.ai)

## After Making Changes:
1. Wait 5-10 minutes for DNS propagation
2. Run: `./force-ssl-check.sh`
3. Monitor with: `./monitor-deployment.sh`