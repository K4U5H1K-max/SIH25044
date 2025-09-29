# Deployment Guide: Vercel + Render

## 🚀 Deploy AI Farming Advisor

### Backend Deployment (Render)

1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New" → "Web Service"
   - Connect your GitHub repository: `SIH25044`
   - Configure:
     - **Name**: `ai-farming-advisor-backend` (or your choice)
     - **Root Directory**: `/project` (if repo root is different)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python Backend1.py`

3. **Set Environment Variables** on Render:
   ```
   GROQ_API_KEY=your_actual_groq_api_key
   FLASK_DEBUG=False
   FRONTEND_ORIGINS=https://your-vercel-app.vercel.app
   ```

4. **Deploy** - Render will automatically build and deploy your backend

   **Alternative Start Commands** (if you encounter issues):
   ```bash
   # Option 1 (Recommended): Direct Python
   python Backend1.py
   
   # Option 2: Gunicorn with full path
   python -m gunicorn --bind 0.0.0.0:$PORT Backend1:app
   
   # Option 3: Traditional gunicorn
   gunicorn --bind 0.0.0.0:$PORT Backend1:app
   ```

### 🔧 **Common Deployment Issues**

#### "ModuleNotFoundError: No module named 'requests'"
- **Solution**: Make sure your `requirements.txt` file is in the root directory of your project
- **Check**: Render looks for `requirements.txt` in the same directory as your start command file
- **Fix**: If the issue persists, try adding this to your start command:
  ```bash
  pip install -r requirements.txt && python Backend1.py
  ```

#### "Build failed" or dependency issues
- Audio dependencies (PyAudio, playsound) may not install on Render
- These are optional and wrapped in try-except blocks in the code
- The backend will work without them (audio features will be handled by the frontend)

### Frontend Deployment (Vercel)

1. **Deploy on Vercel**:
   - Go to [vercel.com](https://vercel.com) and sign up/login
   - Click "Add New..." → "Project"
   - Import your GitHub repository: `SIH25044`
   - Configure:
     - **Framework Preset**: Vite
     - **Root Directory**: `project` (if needed)
     - **Build Command**: `npm run build` (auto-detected)
     - **Output Directory**: `dist` (auto-detected)

2. **Set Environment Variables** on Vercel:
   - Go to your Vercel project dashboard
   - Click "Settings" → "Environment Variables"
   - Add a new environment variable:
     - **Key**: `VITE_API_BASE`
     - **Value**: `https://sih25044.onrender.com`
     - **Environment**: Select "Production", "Preview", and "Development"
   - Click "Save"

3. **Test your backend** (should return JSON, not 404):
   - Visit: `https://sih25044.onrender.com/health` (if available)
   - Or test the chat endpoint: `https://sih25044.onrender.com/chat`

3. **Deploy** - Vercel will automatically build and deploy your frontend

### Final Configuration

1. **Update Backend CORS** (after getting Vercel URL):
   - Note your Vercel app URL: `https://your-app-name.vercel.app`
   - Update Render environment variable:
     ```
     FRONTEND_ORIGINS=https://your-app-name.vercel.app
     ```

2. **Update Frontend API** (after getting Render URL):
   - Note your Render backend URL: `https://your-backend-name.render.com`
   - Update Vercel environment variable:
     ```
     VITE_API_BASE=https://your-backend-name.render.com
     ```

3. **Redeploy both services** to apply the changes

## 🔧 Files Created for Deployment

- ✅ `requirements.txt` - Python dependencies for Render
- ✅ `vercel.json` - Vercel configuration
- ✅ `.env.example` - Environment variables template
- ✅ Updated `Backend1.py` - Production-ready Flask app
- ✅ Updated CORS settings - Allows Vercel domains

## 🌐 Architecture

```
[Users] → [Vercel Frontend] → [Render Backend] → [Groq AI API]
         https://*.vercel.app   https://*.render.com
```

## 💰 Costs

- **Vercel**: Free tier (sufficient for this app)
- **Render**: Free tier (sufficient for backend, sleeps after 15 min inactivity)
- **Groq API**: Free tier available

## 📱 Testing

After deployment, test:
1. Frontend loads on Vercel URL
2. Language selection works
3. Chat functionality works
4. Voice input works (if using HTTPS)
5. Dashboard updates correctly

## 🔧 Troubleshooting

- **CORS errors**: Check `FRONTEND_ORIGINS` env var on Render
- **API errors**: Check `VITE_API_BASE` env var on Vercel  
- **Backend sleeping**: Render free tier sleeps after 15min inactivity
- **Build failures**: Check logs in Render/Vercel dashboard

## 🚀 Go Live!

Your AI Farming Advisor will be live at:
- **Frontend**: `https://your-app-name.vercel.app`
- **Backend**: `https://your-backend-name.render.com`

Farmers worldwide can now access multilingual farming advice! 🌾🤖