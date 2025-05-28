#!/bin/bash

# DNS Verification Script

echo "=== DNS Verification for tobermory.ai ==="
echo ""

echo "Current A records for tobermory.ai:"
dig tobermory.ai A +short | sort

echo ""
echo "Expected Google IPs:"
echo "216.239.32.21"
echo "216.239.34.21"
echo "216.239.36.21"
echo "216.239.38.21"

echo ""
echo "Current CNAME for api.tobermory.ai:"
dig api.tobermory.ai CNAME +short

echo ""
echo "Expected: ghs.googlehosted.com."

echo ""
echo "=== DNS Propagation Check ==="
echo "Checking from different DNS servers..."
echo ""
echo "Google DNS (8.8.8.8):"
dig @8.8.8.8 tobermory.ai A +short | sort
echo ""
echo "Cloudflare DNS (1.1.1.1):"
dig @1.1.1.1 tobermory.ai A +short | sort

echo ""
echo "If the IPs match the expected Google IPs, DNS is properly configured!"