# 🚂 Railway Deployment Setup for InvestigatorAI

## 🔧 **Service Connection Fix**

Railway uses **IPv6-only internal networking**. Services connect using internal hostnames like `servicename.railway.internal`.

## 📋 **Required Environment Variables**

### **For the API Service (repo):**

#### **Redis Connection:**
```bash
# Railway auto-generates these - you may need to set manually:
REDIS_URL=redis://default:password@redis.railway.internal:6379
# OR individual components:
REDISHOST=redis.railway.internal
REDISPORT=6379
REDISPASSWORD=your_redis_password
REDISUSER=default
```

#### **Qdrant Connection:**
```bash
# Set these in your Railway API service:
QDRANT_HOST=qdrant.railway.internal
QDRANT_PORT=6333
# OR full URL:
QDRANT_URL=http://qdrant.railway.internal:6333
```

#### **Your API Keys:**
```bash
OPENAI_API_KEY=your_openai_key
TAVILY_SEARCH_API_KEY=your_tavily_key
LANGSMITH_API_KEY=your_langsmith_key  # optional
```

## 🚀 **Deployment Steps**

### 1. **Create Railway Project**
```bash
railway login
railway new
```

### 2. **Add Services**
```bash
# Add Redis service
railway add --service redis

# Add Qdrant service  
railway add --service qdrant

# Your repo service should already exist
```

### 3. **Configure Qdrant Service**
In the Qdrant service, set these environment variables:
```bash
# Make Qdrant listen on all interfaces (IPv6 compatible)
QDRANT__SERVICE__HTTP_PORT=6333
QDRANT__SERVICE__GRPC_PORT=6334
QDRANT__SERVICE__HOST=::  # Listen on all interfaces (IPv6)
```

### 4. **Configure API Service Environment Variables**
Set all the environment variables listed above in your `repo` service.

### 5. **Deploy**
```bash
railway up
```

## 🔍 **Troubleshooting**

### **Redis Connection Issues:**
- ✅ Check `REDIS_URL` includes `?family=0` for IPv6 support
- ✅ Verify Redis service is running: `railway logs --service redis`
- ✅ Test connection: `railway run redis-cli ping`

### **Qdrant Connection Issues:**
- ✅ Verify Qdrant is listening on `::` (all interfaces)
- ✅ Check internal hostname: `qdrant.railway.internal`
- ✅ Test connection: `railway run curl http://qdrant.railway.internal:6333/collections`

### **Service Discovery:**
Railway services connect using:
- **Internal hostname**: `servicename.railway.internal`
- **Port**: Default service port (Redis: 6379, Qdrant: 6333)
- **Protocol**: HTTP for internal, HTTPS for external

## ✅ **Verification**

After deployment, check logs:
```bash
# API service logs
railway logs --service repo --follow

# Redis logs  
railway logs --service redis

# Qdrant logs
railway logs --service qdrant
```

Look for:
- ✅ `Connected to Redis successfully`
- ✅ `Connected to Qdrant successfully`
- ❌ `ENOTFOUND redis.railway.internal` (IPv6 issue)
- ❌ `Connection refused` (service not running)

## 🎯 **Success Indicators**

When working correctly, you should see:
```
🚂 Using Railway REDIS_URL for connection
✅ Connected to Redis successfully
🚂 Detected Railway internal networking - using HTTP REST API  
✅ Connected to Qdrant successfully
🎉 InvestigatorAI API ready!
```
