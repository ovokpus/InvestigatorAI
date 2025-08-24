# 🚂 Railway Deployment Setup for InvestigatorAI

## 🔧 **Service Connection Fix**

Railway uses **IPv6-only internal networking**. Services connect using internal hostnames like `servicename.railway.internal`.

## 📋 **Required Environment Variables**

### **For the API Service (repo):**

#### **Redis Connection:**
```bash
# Railway should auto-generate REDIS_URL - check your service variables
# If not available, Railway may provide these individual variables:
REDISHOST=<redis_internal_host>
REDISPORT=6379
REDISPASSWORD=<generated_password>
REDISUSER=default
```

#### **Qdrant Connection:**
```bash
# Railway may provide these variables - check your Qdrant service:
QDRANT_PRIVATE_URL=<qdrant_internal_url>
# OR set manually if Railway doesn't auto-generate:
QDRANT_HOST=<qdrant_internal_host>
QDRANT_PORT=6333
```

> **Note**: Railway's internal hostnames are auto-generated and may not follow the `servicename.railway.internal` pattern. Check your service's "Variables" tab for the actual values.

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
