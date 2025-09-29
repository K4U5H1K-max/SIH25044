# Deployment Guide: Render (Frontend + Backend)

## 🚀 Deploy AI Farming Advisor on Render

### Prerequisites

1. **GitHub Repository**: Push your code to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Groq API Key**: Get your API key from [console.groq.com](https://console.groq.com)

---

## Backend Deployment (Already Done ✅)

Your backend is already deployed at: **https://sih25044.onrender.com**

---

## Frontend Deployment (Static Site)

### Step 1: Deploy Frontend on Render

1. **Go to Render Dashboard**:
   - Visit [render.com](https://render.com) and login
   - Click **"New"** → **"Static Site"**

2. **Connect Repository**:
   - Connect your GitHub account
   - Select repository: `SIH25044`
   - Click **"Connect"**

3. **Configure Static Site**:
   - **Name**: `ai-farming-advisor-frontend` (or your choice)
   - **Root Directory**: `project` (important!)
   - **Build Command**: `npm ci && npx vite build`
   - **Publish Directory**: `dist`

4. **Advanced Settings**:
   - **Auto Deploy**: Yes (recommended)
   - **Environment**: `Node`

### Step 2: Configure Environment (Optional)

Since we've configured the frontend to automatically use the correct backend URL in production, no environment variables are needed! 🎉

### Step 3: Deploy

1. Click **"Create Static Site"**
2. Render will automatically:
   - Install dependencies (`npm install`)
   - Build your project (`npm run build`)
   - Deploy the static files

---

## Final Setup

### Your Live URLs:
- **Frontend**: `https://your-frontend-name.onrender.com`
- **Backend**: `https://sih25044.onrender.com`

### Test Your Deployment:

1. **Visit your frontend URL**
2. **Test the features**:
   - ✅ Language selection
   - ✅ User login
   - ✅ Chat functionality
   - ✅ Voice input (requires HTTPS - ✅ on Render)
   - ✅ Dashboard updates

---

## 🔧 Configuration Details

### Automatic API Detection:
The frontend automatically detects the correct backend URL:
- **Development**: `http://127.0.0.1:5000`
- **Production**: `https://sih25044.onrender.com`

### CORS Configuration:
The backend allows requests from:
- ✅ `localhost` (development)
- ✅ `*.onrender.com` (production)
- ✅ `*.vercel.app` (if you switch back)

---

## 💰 Costs

- **Frontend**: Free tier (sufficient for static site)
- **Backend**: Free tier (sleeps after 15 min inactivity)
- **Total**: **$0/month** 🎉

---

## 🔧 Troubleshooting

### Build Fails
- Check that `Root Directory` is set to `project`
- Use `Build Command`: `npm ci && npx vite build` (not just `npm run build`)
- Ensure `Publish Directory` is `dist`
- If you get "vite: not found" error, make sure you're using `npx vite build`

### CORS Errors
- Your backend already allows `*.onrender.com` domains
- No additional configuration needed

### Backend Sleeping
- Free tier sleeps after 15 minutes of inactivity
- First request may take 30 seconds to "wake up"
- Consider upgrading to paid tier for production use

---

## 🚀 You're Live!

Once deployed, your AI Farming Advisor will be accessible worldwide at:
**https://your-frontend-name.onrender.com**

Farmers can now get multilingual farming advice with voice input! 🌾🤖

---

## 📁 Files Created/Modified

- ✅ `render.yaml` - Render static site configuration
- ✅ Updated `vite.config.ts` - Production build settings
- ✅ Updated `src/utils/api.ts` - Automatic API URL detection
- ✅ Updated `Backend1.py` - Added Render CORS support
- ✅ Updated `package.json` - Added production build scripts

## 🎯 Next Steps

1. **Deploy the frontend** following the steps above
2. **Test all functionality** on the live site
3. **Share your live URL** with users
4. **Monitor usage** in Render dashboard

Your farming advisor is ready to help farmers worldwide! 🌱