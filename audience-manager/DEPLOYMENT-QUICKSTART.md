# Audience Manager - Deployment Quick Start Guide

## 🚀 Quick Deploy Options

### Option 1: Local Development with Docker (Recommended for Testing)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd audience-manager

# 2. Copy environment variables
cp .env.example .env

# 3. Edit .env with your settings
# Important: Update DATABASE_URL, POSTGRES_PASSWORD, and API keys

# 4. Run with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
```

### Option 2: Deploy to Vercel (Recommended for Production)

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy
vercel --prod

# 3. Add environment variables in Vercel dashboard:
# - REACT_APP_API_URL (your backend URL)
# - Any other required variables
```

### Option 3: Quick Deploy Script

```bash
# Make deploy script executable
chmod +x deploy.sh

# Deploy to Docker (local)
./deploy.sh --target docker

# Deploy to Vercel
./deploy.sh --target vercel --env production

# Deploy to AWS
./deploy.sh --target aws --env production

# Skip tests for faster deployment
./deploy.sh --target docker --skip-tests
```

## 📋 Pre-Deployment Checklist

- [ ] Node.js 20+ installed
- [ ] Python 3.11+ installed (for backend)
- [ ] Docker & Docker Compose installed (for Docker deployment)
- [ ] Environment variables configured
- [ ] Data file available (or use sample data)

## 🔧 Environment Configuration

### Required Environment Variables

```env
# Frontend
REACT_APP_API_URL=http://localhost:5000

# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/audience_manager
REDIS_URL=redis://localhost:6379
DATA_PATH=/path/to/your/data.csv

# Optional
ANTHROPIC_API_KEY=your_key_here
SECRET_KEY=your-secret-key
```

## 📊 Sample Data

For testing, create a sample dataset:

```bash
# Generate 1000-record sample
cd src/api
python -c "
from enhanced_nl_audience_builder import DataRetriever
dr = DataRetriever('', '')
df = dr.fetch_data(['AGE_RANGE', 'INCOME_LEVEL', 'LOCATION_TYPE'], 1000)
df.to_csv('sample_data.csv', index=False)
print('Sample data created!')
"
```

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose build
docker-compose up -d

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh
```

## 🌐 Production Deployment

### Vercel + External Backend

1. **Deploy Frontend to Vercel:**
   ```bash
   vercel --prod
   ```

2. **Deploy Backend to Railway:**
   ```bash
   cd src/api
   railway init
   railway up
   ```

3. **Update Frontend Environment:**
   - Set `REACT_APP_API_URL` to your Railway backend URL

### Full AWS Deployment

1. **Build Docker Images:**
   ```bash
   docker build -f Dockerfile.frontend -t audience-frontend .
   docker build -f Dockerfile.backend -t audience-backend .
   ```

2. **Push to ECR:**
   ```bash
   aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URI
   docker tag audience-frontend:latest $ECR_URI/audience-frontend:latest
   docker push $ECR_URI/audience-frontend:latest
   ```

3. **Deploy with ECS or EKS**

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Find process using port
   lsof -i :3000
   # Kill process
   kill -9 <PID>
   ```

2. **Docker permission denied:**
   ```bash
   sudo usermod -aG docker $USER
   # Log out and back in
   ```

3. **Large data file issues:**
   - Use sample data for testing
   - Mount data volume in Docker
   - Use cloud storage for production

### Health Checks

```bash
# Check frontend
curl http://localhost:3000

# Check backend
curl http://localhost:5000/health

# Check all services
docker-compose ps
```

## 📚 Next Steps

1. Review [DEPLOYMENT_OPTIONS.md](./DEPLOYMENT_OPTIONS.md) for detailed platform comparisons
2. Read [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md) for enterprise setup
3. Configure monitoring and logging
4. Set up CI/CD pipeline
5. Implement backup strategy

## 🆘 Support

- Documentation: `/docs` directory
- Issues: GitHub Issues
- Logs: `docker-compose logs -f`

---

**Quick Links:**
- [Full Documentation](./docs/README.md)
- [API Reference](./docs/API.md)
- [Architecture Guide](./docs/TECHNICAL-ARCHITECTURE.md)
- [Component Guide](./docs/COMPONENT-DEVELOPMENT-GUIDE.md)