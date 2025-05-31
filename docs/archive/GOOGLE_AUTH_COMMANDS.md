# Google Cloud Authentication Commands

## 1. Login to Google Cloud
```bash
gcloud auth login
```

This will open your browser to authenticate with Google. Follow the prompts to sign in.

## 2. Set the project (after login)
```bash
gcloud config set project feisty-catcher-461000-g2
```

## 3. Verify authentication
```bash
gcloud auth list
```

## 4. Deploy the Variable Picker fix
After authentication is complete, run:
```bash
cd "/Users/myles/Documents/Activation Manager"
./deploy-variable-picker-fix.sh
```

## Alternative: Application Default Credentials
If you need application default credentials:
```bash
gcloud auth application-default login
```