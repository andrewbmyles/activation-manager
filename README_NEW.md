# Activation Manager

A sophisticated audience segmentation platform that leverages natural language processing and semantic search to help users discover relevant demographic and behavioral variables from a comprehensive database of 49,000+ variables.

## 🚀 Live Demo

**Production URL**: https://tobermory.ai  
**Password**: Contact administrator for access

## ✨ Key Features

### Natural Language Multi-Variate Audience Builder
- Search using plain English: "young affluent millennials who shop online"
- AI-powered semantic understanding of your queries
- Real-time refinement to narrow down results
- Always shows semantic matching with 🧠 icon

### Comprehensive Variable Database
- 49,323 consumer variables
- Categories: Demographics, Behavioral, Psychographic, Geographic, Technographic
- PRIZM segment integration
- Domain-specific optimization (automotive, financial, health, etc.)

### Advanced Search Capabilities
- **Hybrid Search**: Combines keyword and semantic matching
- **Smart Scoring**: Relevance-based ranking
- **Fast Performance**: Parquet format for 5-10x faster loading
- **Pagination**: 50 results with 10 per page

### Professional UI/UX
- Responsive design that scales to larger screens
- Clean, intuitive interface
- Real-time search results
- Export to JSON or CSV

## 🛠️ Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Build**: Create React App
- **State**: React Hooks (no Redux needed)

### Backend
- **Framework**: Flask (Python 3.11)
- **Data Processing**: Pandas, NumPy
- **Search**: Custom implementation with optional FAISS
- **API**: RESTful JSON API
- **CORS**: Enabled for all origins

### Infrastructure
- **Hosting**: Google App Engine
- **Scaling**: Automatic (1-10 instances)
- **Storage**: CSV/Parquet files deployed with app
- **Security**: Password authentication

## 🚦 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd activation-manager
   ```

2. **Install dependencies**
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   cd audience-manager
   npm install
   ```

3. **Start the servers**
   ```bash
   # Terminal 1 - Backend
   python main.py
   
   # Terminal 2 - Frontend
   cd audience-manager
   npm start
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8080

## 📦 Deployment

### Prerequisites
- Google Cloud Platform account
- `gcloud` CLI installed and authenticated
- Project with App Engine enabled

### Deploy to Production
```bash
# Build frontend
cd audience-manager
npm run build
cd ..

# Deploy to Google App Engine
gcloud app deploy app_production.yaml --project=YOUR_PROJECT_ID
```

For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

## 📚 Documentation

- [API Documentation](docs/API_DOCUMENTATION.md) - Complete API reference
- [Architecture Guide](docs/ARCHITECTURE.md) - System design and components
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Detailed deployment instructions
- [Refactoring Plan](REFACTORING_PLAN.md) - Codebase improvement roadmap

## 🧪 Testing

```bash
# Frontend tests
cd audience-manager
npm test

# Backend tests
python -m pytest

# Integration tests
python run_tests.py
```

## 📝 Sample Queries

Try these example queries in the NL Multi-Variate Audience Builder:

**Demographics**
- "Young affluent millennials who shop online frequently"
- "Retired seniors with high disposable income"
- "College-educated parents with children under 10"

**Behavioral**
- "Health-conscious consumers who buy organic food"
- "Tech-savvy early adopters who use mobile devices"
- "Frequent travelers who book luxury vacations"

**Psychographic**
- "Environmentally conscious sustainable shoppers"
- "Sports enthusiasts who follow professional leagues"
- "Food lovers who dine out frequently"

## 🔧 Configuration

### Environment Variables
Create a `.env` file for local development:
```env
FLASK_ENV=development
PORT=8080
GOOGLE_CLOUD_PROJECT=your-project-id
```

### Data Files
Required data files in `data/` directory:
- `Full_Variable_List_2022_CAN.csv` - Main variable database
- `variables_2022_can.parquet` - Optimized format (optional)

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **Build Failures**
   ```bash
   rm -rf audience-manager/build
   cd audience-manager && npm run build
   ```

3. **Search Not Working**
   - Ensure backend is running on port 8080
   - Check data files exist in `data/` directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

[License information]

## 🙏 Acknowledgments

- Built with React and Flask
- Deployed on Google Cloud Platform
- Part of the Tobermory AI suite

## 📞 Support

For issues or questions:
- Check [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- Review [API Documentation](docs/API_DOCUMENTATION.md)
- Contact support team

---

**Version**: 1.4.0  
**Last Updated**: May 2024  
**Status**: Production Ready ✅