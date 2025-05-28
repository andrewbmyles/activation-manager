#!/bin/bash

# Monitor SSL Certificate Provisioning

echo "=== SSL Certificate Monitoring ==="
echo "Started at: $(date)"
echo ""

check_ssl() {
    echo -n "Checking tobermory.ai SSL... "
    if curl -Is https://tobermory.ai 2>/dev/null | head -n 1 | grep -q "200\|301\|302"; then
        echo "✅ SSL ACTIVE!"
        return 0
    else
        echo "⏳ Still provisioning"
        return 1
    fi
}

check_api_ssl() {
    echo -n "Checking api.tobermory.ai SSL... "
    if curl -Is https://api.tobermory.ai/health 2>/dev/null | head -n 1 | grep -q "200"; then
        echo "✅ SSL ACTIVE!"
        return 0
    else
        echo "⏳ Still provisioning"
        return 1
    fi
}

echo "Monitoring SSL certificate provisioning..."
echo "This typically takes 15-30 minutes after DNS configuration."
echo ""

# Check every 2 minutes
while true; do
    frontend_ready=false
    api_ready=false
    
    if check_ssl; then
        frontend_ready=true
    fi
    
    if check_api_ssl; then
        api_ready=true
    fi
    
    if $frontend_ready && $api_ready; then
        echo ""
        echo "🎉 Both SSL certificates are active!"
        echo "Frontend: https://tobermory.ai"
        echo "API: https://api.tobermory.ai"
        break
    fi
    
    echo "Checking again in 2 minutes... (Press Ctrl+C to stop)"
    sleep 120
done