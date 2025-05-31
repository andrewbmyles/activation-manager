#!/bin/bash

# Script to fix GCP permissions for App Engine deployment

echo "🔧 Fixing GCP permissions for App Engine deployment..."
echo ""

# Check current user
echo "📋 Current gcloud account:"
gcloud config get-value account
echo ""

# Check current project
echo "📋 Current project:"
gcloud config get-value project
echo ""

# List current IAM policy
echo "📋 Current IAM roles for andrew@tobermory.ai:"
gcloud projects get-iam-policy tobermory-ai \
    --flatten="bindings[].members" \
    --filter="bindings.members:andrew@tobermory.ai" \
    --format="table(bindings.role)"
echo ""

# Instructions for fixing permissions
echo "🔑 To fix the permissions issue, run one of these commands:"
echo ""
echo "Option 1: Grant App Engine Deployer role (recommended):"
echo "  gcloud projects add-iam-policy-binding tobermory-ai \\"
echo "    --member='user:andrew@tobermory.ai' \\"
echo "    --role='roles/appengine.deployer'"
echo ""
echo "Option 2: Grant App Engine Admin role (more permissions):"
echo "  gcloud projects add-iam-policy-binding tobermory-ai \\"
echo "    --member='user:andrew@tobermory.ai' \\"
echo "    --role='roles/appengine.appAdmin'"
echo ""
echo "Option 3: Grant Editor role (broad permissions):"
echo "  gcloud projects add-iam-policy-binding tobermory-ai \\"
echo "    --member='user:andrew@tobermory.ai' \\"
echo "    --role='roles/editor'"
echo ""
echo "📝 Note: You may need to be logged in as the project owner to grant these permissions."
echo ""
echo "Alternative: Ask the project owner to run the commands above."
echo ""

# Check if we can view the project
echo "🔍 Checking project access..."
if gcloud projects describe tobermory-ai &>/dev/null; then
    echo "✅ Can access project tobermory-ai"
else
    echo "❌ Cannot access project tobermory-ai"
    echo "   You may need to:"
    echo "   1. Set the correct project: gcloud config set project tobermory-ai"
    echo "   2. Authenticate: gcloud auth login"
fi