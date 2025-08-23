# 🚀 Railway Deployment for InvestigatorAI

Deploy InvestigatorAI's API, Redis, and Qdrant services to Railway using your existing `.env` file.

## 📋 Prerequisites

- [Railway CLI](https://docs.railway.app/develop/cli) installed
- Railway project with 3 services: `repo`, `redis`, and `qdrant`
- API keys in your root `.env` file

## 🚀 One-Command Deployment

```bash
./deploy/railway/deploy.sh
```

This script will:
- ✅ Read API keys from your `.env` file
- ✅ Configure all Railway services optimally
- ✅ Deploy your API service
- ✅ Provide monitoring commands

## 📊 After Deployment

### Monitor Your Services
```bash
# Check deployment status
railway status

# View API logs
railway logs --service repo --follow

# Get your API URL
railway domain
```

### Test Your API
```bash
# Health check
curl https://your-domain.up.railway.app/health

# Test investigation
curl -X POST https://your-domain.up.railway.app/investigate \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 75000,
    "currency": "USD",
    "description": "Test transaction",
    "customer_name": "Test Customer",
    "risk_rating": "High",
    "country_to": "Romania"
  }'
```

## 🔧 Service Configuration

The deployment script automatically configures:

- **API Service (repo)**: FastAPI backend with health checks
- **Redis**: High-performance caching (256MB limit)
- **Qdrant**: Vector database for document embeddings

## 🎉 Success!

Your InvestigatorAI fraud investigation system will be running in the cloud with automatic scaling, HTTPS, and persistent storage! 🌟
