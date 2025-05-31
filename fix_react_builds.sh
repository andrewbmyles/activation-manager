#!/bin/bash
# Fix React builds with proper base paths

echo "Fixing React builds for proper deployment..."

# 1. Fix Activation Manager build
echo "1. Rebuilding Activation Manager..."
cd audience-manager

# Update package.json to use absolute paths
echo "   Updating package.json..."
cat > package.json.tmp << 'EOF'
{
  "name": "audience-manager",
  "version": "0.1.0",
  "private": true,
  "homepage": "/activation-manager",
  "dependencies": {
    "@tanstack/react-query": "^5.76.2",
    "@testing-library/dom": "^10.4.0",
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/react": "^16.3.0",
    "@testing-library/user-event": "^13.5.0",
    "@types/jest": "^27.5.2",
    "@types/node": "^16.18.126",
    "@types/react": "^19.1.5",
    "@types/react-dom": "^19.1.5",
    "@types/react-router-dom": "^5.3.3",
    "autoprefixer": "^10.4.21",
    "clsx": "^2.1.1",
    "framer-motion": "^11.18.2",
    "lucide-react": "^0.511.0",
    "postcss": "^8.5.3",
    "react": "^19.1.0",
    "react-dom": "^19.1.0",
    "react-hook-form": "^7.56.4",
    "react-router-dom": "^7.6.0",
    "react-scripts": "5.0.1",
    "recharts": "^2.15.3",
    "tailwind-merge": "^3.3.0",
    "tailwindcss": "^3.4.17",
    "typescript": "^4.9.5",
    "web-vitals": "^2.1.4"
  },
  "proxy": "http://localhost:8080",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF

mv package.json.tmp package.json

# Build
echo "   Building..."
npm run build

echo "   Build complete!"
cd ..

# 2. Fix Tobermory Web build
echo "2. Rebuilding Tobermory Web..."
cd tobermory-web

# Update package.json to use absolute paths
echo "   Updating package.json..."
if [ -f package.json ]; then
    # Add homepage field
    node -e "
    const fs = require('fs');
    const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    pkg.homepage = '/';
    fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2));
    "
    echo "   Updated package.json"
fi

# Build if node_modules exist
if [ -d node_modules ]; then
    echo "   Building..."
    npm run build
    echo "   Build complete!"
else
    echo "   Skipping build - node_modules not found"
fi

cd ..

echo "React builds fixed!"
echo ""
echo "Next steps:"
echo "1. Deploy using: gcloud app deploy app_tobermory_optimized.yaml"
echo "2. Test at: https://tobermory-ai.uc.r.appspot.com/activation-manager"