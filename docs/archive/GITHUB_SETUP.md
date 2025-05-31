# GitHub Setup Instructions

To push your code to GitHub, follow these steps:

## 1. Create a GitHub Repository

Go to https://github.com/new and create a new repository:
- Repository name: `activation-manager` (or your preferred name)
- Description: "Sophisticated audience segmentation platform with NLP and ML"
- Choose: Public or Private
- Don't initialize with README (we already have one)

## 2. Update Your Remote URL

After creating the repository, update your local git remote:

```bash
# Replace YOUR_USERNAME with your GitHub username
# Replace REPO_NAME with your repository name
git remote set-url origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# For example:
# git remote set-url origin https://github.com/johndoe/activation-manager.git
```

## 3. Push Your Code

```bash
# Push to GitHub
git push -u origin main

# If your default branch is 'master' instead of 'main':
git push -u origin master
```

## 4. Verify

Visit your repository on GitHub to confirm all files were uploaded successfully.

## Alternative: Using GitHub CLI

If you have GitHub CLI installed:

```bash
# Create repo and push in one command
gh repo create activation-manager --public --source=. --remote=origin --push
```

## Notes

- The repository contains large embedding files in `data/embeddings/`
- Consider using Git LFS for these files if needed
- Add a `.gitignore` for sensitive files like `.env`
- The live deployment is at: https://feisty-catcher-461000-g2.nn.r.appspot.com