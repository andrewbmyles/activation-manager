# 🚀 Simple Deployment Instructions

I've created a guided deployment script that will walk you through each step. Here's how to deploy your application:

## Option 1: Use the Quick Deploy Script (Recommended)

```bash
./quick-deploy.sh
```

This script will:
1. Check if you have all the required tools
2. Guide you through each command step-by-step
3. Help you create a GCP project
4. Deploy your backend to Google Cloud
5. Deploy your frontend to Vercel
6. Test everything is working

## Option 2: Manual Step-by-Step

If you prefer to do it manually, here are the exact commands to copy and paste:

### 1️⃣ First, check you have the required tools:

```bash
# Check Node.js
node --version

# Check Google Cloud SDK
gcloud --version

# Install Vercel CLI if needed
npm i -g vercel
```

### 2️⃣ Set up Google Cloud:

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (replace YOUR-PROJECT-ID with your choice)
gcloud projects create YOUR-PROJECT-ID --name="Audience Manager"

# Set the project
gcloud config set project YOUR-PROJECT-ID

# Enable required APIs
gcloud services enable appengine.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com redis.googleapis.com storage.googleapis.com

# Create App Engine app
gcloud app create --region=us-central1
```

### 3️⃣ Deploy Backend:

```bash
# Go to the GCP directory
cd gcp

# Deploy the backend
gcloud app deploy app.yaml --quiet

# Note the URL shown after deployment (https://YOUR-PROJECT-ID.appspot.com)
```

### 4️⃣ Deploy Frontend:

```bash
# Go back to project root
cd ..

# Create environment file with your backend URL
echo 'REACT_APP_API_URL=https://YOUR-PROJECT-ID.appspot.com' > .env.production.local

# Deploy to Vercel
vercel --prod
```

When Vercel asks:
- Set up and deploy: **Y**
- Which scope: Select your account
- Link to existing project: **N**
- Project name: Press Enter (use default)
- Directory: Press Enter (use ./)
- Override settings: **N**

### 5️⃣ Add Environment Variable in Vercel:

After deployment, go to your Vercel dashboard:
1. Click on your project
2. Go to Settings → Environment Variables
3. Add: `REACT_APP_API_URL` = `https://YOUR-PROJECT-ID.appspot.com`
4. Redeploy: `vercel --prod`

## 🎯 That's it! Your app is now live!

### Test Your Deployment:

```bash
# Test backend
curl https://YOUR-PROJECT-ID.appspot.com/health

# Visit your frontend
# The URL will be shown in the Vercel output (like https://your-app.vercel.app)
```

## ❓ Need Help?

If you run into any issues:

1. **"Permission denied" errors**: Make sure you're logged into gcloud
2. **"Project already exists"**: Use a different project ID
3. **API not enabled**: Run the enable command again
4. **Backend not responding**: Check logs with `gcloud app logs tail -s default`

## 🎉 Success Checklist

- [ ] GCP project created
- [ ] APIs enabled
- [ ] Backend deployed to App Engine
- [ ] Backend health check working
- [ ] Frontend deployed to Vercel
- [ ] Environment variable set in Vercel
- [ ] Can access the frontend and use the app

---

**Quick Tip**: Save your project ID! You'll need it for future updates:
```bash
export PROJECT_ID=YOUR-PROJECT-ID
echo "Backend URL: https://$PROJECT_ID.appspot.com"
```