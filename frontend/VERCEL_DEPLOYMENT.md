# 🚀 Vercel Deployment Guide for InvestigatorAI Frontend

This guide will help you deploy the InvestigatorAI frontend to Vercel with proper configuration for production use.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Backend Deployed**: Your InvestigatorAI API should be deployed (e.g., on Railway, Render, or similar)
3. **GitHub Repository**: Your code should be pushed to GitHub
4. **Vercel CLI** (optional): Install with `npm i -g vercel`

## 🛠️ Pre-Deployment Setup

### 1. Environment Variables

The frontend needs to know where your backend API is deployed. You'll need to set:

- `NEXT_PUBLIC_API_URL`: The URL of your deployed backend API

**Example values:**
- Railway: `https://your-app-name.railway.app`
- Render: `https://your-app-name.onrender.com`
- Custom domain: `https://api.yourdomain.com`

### 2. Configuration Files

The following files have been configured for Vercel deployment:

- ✅ `vercel.json` - Vercel-specific configuration
- ✅ `next.config.ts` - Optimized for Vercel
- ✅ API utilities updated to use environment variables

## 🚀 Deployment Methods

### Method 1: Vercel Dashboard (Recommended)

1. **Connect Repository**
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Select the `frontend` folder as the root directory

2. **Configure Build Settings**
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next` (auto-detected)
   - **Install Command**: `npm install`

3. **Set Environment Variables**
   - In project settings, go to "Environment Variables"
   - Add: `NEXT_PUBLIC_API_URL` = `https://your-backend-url.com`
   - Apply to: Production, Preview, and Development

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your app will be available at `https://your-project.vercel.app`

### Method 2: Vercel CLI

1. **Install and Login**
   ```bash
   npm i -g vercel
   vercel login
   ```

2. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

4. **Set Environment Variables**
   ```bash
   vercel env add NEXT_PUBLIC_API_URL production
   # Enter your backend URL when prompted
   ```

5. **Redeploy with Environment Variables**
   ```bash
   vercel --prod
   ```

## 🔧 Configuration Details

### Vercel.json Configuration

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "installCommand": "npm install",
  "env": {
    "NEXT_PUBLIC_API_URL": "@api_url"
  }
}
```

### Next.js Configuration

The `next.config.ts` has been optimized for Vercel with:
- Removed Docker-specific `standalone` output
- Added environment variable handling
- Enabled performance optimizations

### API Integration

All API calls now use the `createApiUrl()` utility function that:
- Reads from `NEXT_PUBLIC_API_URL` environment variable
- Falls back to `localhost:8000` for development
- Handles URL formatting automatically

## 🌐 Custom Domain (Optional)

1. **Add Domain in Vercel Dashboard**
   - Go to Project Settings → Domains
   - Add your custom domain
   - Follow DNS configuration instructions

2. **Update Environment Variables**
   - Ensure `NEXT_PUBLIC_API_URL` points to your backend
   - Consider using the same domain with subdomain (e.g., `api.yourdomain.com`)

## 🔍 Testing Your Deployment

After deployment, verify:

1. **Frontend Loads**: Visit your Vercel URL
2. **API Connection**: Check the health status indicator
3. **Investigation Flow**: Try submitting a test investigation
4. **Error Handling**: Test with backend offline to ensure graceful errors

## 🐛 Troubleshooting

### Build Failures

**Issue**: Build fails with TypeScript errors
```bash
# Solution: Fix TypeScript errors locally first
npm run build
npm run lint
```

**Issue**: Missing dependencies
```bash
# Solution: Ensure all dependencies are in package.json
npm install
```

### Runtime Issues

**Issue**: API calls fail with CORS errors
- **Solution**: Ensure your backend allows requests from your Vercel domain
- Add your Vercel URL to backend CORS configuration

**Issue**: Environment variables not working
- **Solution**: 
  - Ensure variables are prefixed with `NEXT_PUBLIC_`
  - Redeploy after adding environment variables
  - Check Vercel dashboard for correct variable values

**Issue**: 404 errors on page refresh
- **Solution**: This is handled automatically by Next.js App Router

## 📊 Performance Optimization

Your deployment includes:

- ✅ **Static Generation**: Pages pre-rendered at build time
- ✅ **Code Splitting**: Automatic bundle optimization
- ✅ **Image Optimization**: Next.js Image component
- ✅ **Caching**: Vercel Edge Network caching
- ✅ **Compression**: Automatic gzip/brotli compression

## 🔐 Security Headers

The `vercel.json` includes security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

## 📈 Monitoring

Monitor your deployment:
- **Vercel Analytics**: Built-in performance monitoring
- **Function Logs**: View in Vercel dashboard
- **Real User Monitoring**: Available in Pro plans

## 🎯 Next Steps

After successful deployment:

1. **Test thoroughly** with real investigation scenarios
2. **Set up monitoring** and alerts
3. **Configure custom domain** if needed
4. **Set up CI/CD** for automatic deployments
5. **Monitor performance** and optimize as needed

## 🆘 Support

If you encounter issues:

1. Check Vercel build logs in the dashboard
2. Verify environment variables are set correctly
3. Test API connectivity from your deployed frontend
4. Review this guide for common solutions

---

**🎉 Congratulations!** Your InvestigatorAI frontend is now deployed on Vercel with production-ready configuration!
