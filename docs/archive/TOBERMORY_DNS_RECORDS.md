# DNS Configuration for tobermory.ai

## Required DNS Records

Please add the following DNS records to your domain registrar for tobermory.ai:

### A Records (IPv4)
- Type: A
- Name: @ (or blank for root domain)
- Value: 216.239.32.21
- TTL: 3600 (or default)

- Type: A  
- Name: @ (or blank for root domain)
- Value: 216.239.34.21
- TTL: 3600 (or default)

- Type: A
- Name: @ (or blank for root domain)  
- Value: 216.239.36.21
- TTL: 3600 (or default)

- Type: A
- Name: @ (or blank for root domain)
- Value: 216.239.38.21  
- TTL: 3600 (or default)

### AAAA Records (IPv6)
- Type: AAAA
- Name: @ (or blank for root domain)
- Value: 2001:4860:4802:32::15
- TTL: 3600 (or default)

- Type: AAAA
- Name: @ (or blank for root domain)
- Value: 2001:4860:4802:34::15
- TTL: 3600 (or default)

- Type: AAAA  
- Name: @ (or blank for root domain)
- Value: 2001:4860:4802:36::15
- TTL: 3600 (or default)

- Type: AAAA
- Name: @ (or blank for root domain)
- Value: 2001:4860:4802:38::15
- TTL: 3600 (or default)

## Important Notes

1. DNS changes can take up to 24 hours to propagate, though they often complete within 1-2 hours.

2. Once DNS records are configured, Google will automatically provision an SSL certificate for https://tobermory.ai

3. You can verify DNS propagation using:
   ```bash
   dig tobermory.ai
   # or
   nslookup tobermory.ai
   ```

4. The application will be accessible at:
   - https://tobermory.ai (after SSL provisioning)
   - http://tobermory.ai (redirects to HTTPS)

## Current Status
- Domain mapping created in Google App Engine
- Waiting for DNS records to be configured
- Once DNS is configured, SSL certificate will be automatically provisioned