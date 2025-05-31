# Tobermory AI Web Application

A modern web application for tobermory.ai featuring authentication and project management capabilities.

## Features

- 🔐 Password-protected authentication (password: "Minesing")
- 🎨 Beautiful glassmorphic login page with forest theme
- 📊 Project dashboard with Activation Manager integration
- 🍁 Canadian-themed design with forest aesthetics
- 📱 Fully responsive design

## Tech Stack

- React 18 with TypeScript
- React Router v6 for navigation
- CSS Modules for styling
- Context API for state management
- Vite for fast development

## Project Structure

```
tobermory-web/
├── src/
│   ├── assets/          # Images and static files
│   ├── components/      # Reusable components
│   │   ├── Auth/       # Authentication components
│   │   ├── Layout/     # Layout components
│   │   └── Projects/   # Project-related components
│   ├── context/        # React Context providers
│   ├── pages/          # Page components
│   ├── styles/         # Global styles
│   └── App.tsx         # Main app component
├── public/             # Public assets
└── package.json        # Dependencies
```

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- The existing Activation Manager project

### Installation

1. Navigate to the tobermory-web directory:
   ```bash
   cd tobermory-web
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000)

### Building for Production

Run the build script:
```bash
./build-and-deploy.sh
```

This will:
1. Install dependencies
2. Build the React app
3. Copy files to the audience-manager directory
4. Prepare for Google App Engine deployment

## Deployment

The app is designed to be deployed to Google App Engine along with the Activation Manager backend.

1. Build the app using the build script
2. Deploy to App Engine:
   ```bash
   cd ..
   gcloud app deploy app_production.yaml --project=feisty-catcher-461000-g2
   ```

## Authentication

- Password: `Minesing`
- Auth state is stored in localStorage
- Protected routes redirect to login if not authenticated

## Customization

### Images

Replace the placeholder images in `src/assets/images/`:
- `forest-mist.jpg`: Background image for login page
- `tobermory-logo.png`: Company logo (80x80px circular)

### Colors

Edit the CSS variables in `src/styles/globals.css`:
```css
--primary-green: #34a896;
--dark-green: #2d8f7f;
--forest-dark: #1a2f2a;
```

## Integration with Activation Manager

The Activation Manager project is embedded in an iframe when users click on the project card. Make sure the main Activation Manager app is accessible at the root URL.

## License

Copyright © 2024 Tobermory AI. All rights reserved.