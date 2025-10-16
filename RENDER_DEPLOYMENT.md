# 🚀 Render Deployment Guide

## Complete Deployment Checklist for Render.com

### ✅ Pre-Deployment Cross-Check

#### **Backend Files - All Present ✓**
- [x] `app.py` - Main Flask application
- [x] `wsgi.py` - WSGI entry point for Gunicorn
- [x] `requirements.txt` - Updated with production dependencies
- [x] `Procfile` - Render process configuration
- [x] `runtime.txt` - Python 3.11.6
- [x] `.env.example` - Environment variable template
- [x] `config.py` - Configuration with environment variables
- [x] `auth.py` - JWT authentication system
- [x] `database.py` - SQLite database manager
- [x] `inference.py` - YOLOv8 detection engine
- [x] `geofence.py` - GPS monitoring
- [x] `analytics.py` - Analytics engine
- [x] `notifications.py` - Email/SMS alerts
- [x] `pdf_reports.py` - PDF report generator
- [x] `real_data_integration.py` - Real data integration

#### **Frontend Files - All Present ✓**
- [x] `package.json` - Updated with build scripts
- [x] `.env.example` - API URL configuration
- [x] `src/App.jsx` - Updated to use VITE_API_URL
- [x] All 11 React components
- [x] HAL logo (hal-logo.svg)
- [x] Tailwind CSS configuration

#### **Key Updates Made ✓**
- [x] Changed `opencv-python` to `opencv-python-headless` (no GUI on server)
- [x] Added `gunicorn` for production WSGI server
- [x] Added `python-dotenv` for environment variables
- [x] Added `flask-jwt-extended` and `bcrypt` for authentication
- [x] Created `wsgi.py` for Gunicorn entry point
- [x] Updated `app.py` to use environment variables
- [x] Updated `config.py` to load from .env
- [x] Updated frontend to use `VITE_API_URL`
- [x] Added CORS configuration for production
- [x] Created `.gitignore` for sensitive files

---

## 📦 Backend Deployment (Web Service)

### Step 1: Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select branch (usually `main` or `master`)

### Step 2: Configure Service

**Basic Settings:**
- **Name:** `hal-drone-surveillance-backend` (or your choice)
- **Region:** Choose closest to your users
- **Branch:** `main`
- **Root Directory:** `backend`
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`

### Step 3: Environment Variables

Add these in Render dashboard (Settings → Environment):

```bash
# Required
JWT_SECRET_KEY=<generate-random-string-here>
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<generate-random-string-here>

# Optional - Email Notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
ALERT_RECIPIENTS=recipient@example.com

# Optional - SMS Notifications
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890
ALERT_PHONE_NUMBERS=+1234567890

# CORS (Add your frontend URL after deployment)
CORS_ORIGINS=https://your-frontend-app.onrender.com

# Video Configuration
VIDEO_SOURCE=0
VIDEO_FPS=15
```

**Generate Secure Keys:**
```python
import secrets
print(secrets.token_urlsafe(32))  # Run this twice for two keys
```

### Step 4: Advanced Settings

- **Instance Type:** Free (or paid for better performance)
- **Auto-Deploy:** Yes (deploys on git push)
- **Health Check Path:** `/health`

### Step 5: Deploy

Click **"Create Web Service"** and wait 5-10 minutes for build.

**Your backend URL will be:** `https://hal-drone-surveillance-backend.onrender.com`

---

## 🎨 Frontend Deployment (Static Site)

### Step 1: Create .env File

Create `drone-surveillance-frontend/.env`:
```bash
VITE_API_URL=https://your-backend-app.onrender.com
```
Replace with your actual backend URL from Step 5 above.

### Step 2: Create New Static Site

1. Click **"New +"** → **"Static Site"**
2. Connect your GitHub repository
3. Select branch

### Step 3: Configure Static Site

**Basic Settings:**
- **Name:** `hal-drone-surveillance-frontend`
- **Branch:** `main`
- **Root Directory:** `drone-surveillance-frontend`
- **Build Command:** `npm install && npm run build`
- **Publish Directory:** `dist`

### Step 4: Environment Variables

Add in Render dashboard:
```bash
VITE_API_URL=https://your-backend-app.onrender.com
```

### Step 5: Deploy

Click **"Create Static Site"** and wait 3-5 minutes.

**Your frontend URL will be:** `https://hal-drone-surveillance-frontend.onrender.com`

---

## 🔄 Update Backend CORS

After frontend deployment, update backend environment variable:

1. Go to backend service → Environment
2. Update `CORS_ORIGINS`:
```bash
CORS_ORIGINS=https://hal-drone-surveillance-frontend.onrender.com
```
3. Save and redeploy

---

## 🧪 Testing Deployment

### Test Backend:
```bash
# Health check
curl https://your-backend-app.onrender.com/health

# API test
curl https://your-backend-app.onrender.com/api/geofence/zones
```

### Test Frontend:
1. Open `https://your-frontend-app.onrender.com`
2. Login with: `admin` / `admin123`
3. Navigate through all views
4. Upload an image to test detection
5. Check Analytics dashboard
6. Verify Heatmap loads

---

## ⚠️ Important Notes

### Free Tier Limitations:
- **Backend:** Spins down after 15 min of inactivity (first request takes 30-60s)
- **Storage:** No persistent disk (database resets on restart)
- **Memory:** 512MB RAM (YOLOv8n works fine)
- **Build Time:** 5-10 minutes for backend

### Recommendations:
1. **Use Paid Plan ($7/month)** for:
   - Always-on backend
   - Persistent disk storage
   - Better performance
   - Custom domains

2. **Database Options:**
   - Free: SQLite (resets on restart)
   - Paid: PostgreSQL ($7/month on Render)
   - External: Supabase, Railway, PlanetScale

3. **Camera Feed:**
   - Live webcam won't work on server (no hardware)
   - Use file upload feature instead
   - Or connect to IP camera via RTSP URL

### Security Best Practices:
- ✅ Change default passwords immediately
- ✅ Use strong JWT_SECRET_KEY (32+ characters)
- ✅ Enable HTTPS only (Render provides free SSL)
- ✅ Restrict CORS to your frontend domain
- ✅ Never commit .env files to GitHub
- ✅ Use environment variables for all secrets

---

## 🐛 Troubleshooting

### Backend Won't Start:
1. Check logs in Render dashboard
2. Verify all dependencies in requirements.txt
3. Test locally: `gunicorn wsgi:app`
4. Check Python version matches runtime.txt

### Frontend Shows "Network Error":
1. Verify VITE_API_URL is correct
2. Check CORS settings in backend
3. Open browser console (F12) for errors
4. Test backend health endpoint

### Database Resets:
1. Free tier doesn't persist disk storage
2. Upgrade to paid plan for persistent disk
3. Or use external database (PostgreSQL)

### YOLOv8 Slow/Crashes:
1. Free tier has limited RAM (512MB)
2. Use YOLOv8n (nano) model only
3. Lower confidence threshold
4. Consider paid tier (2GB RAM)

---

## 📊 Monitoring

### Render Dashboard:
- **Logs:** Real-time application logs
- **Metrics:** CPU, Memory, Network usage
- **Events:** Deployment history
- **Alerts:** Email notifications on failures

### Health Checks:
- Backend: `https://your-backend.onrender.com/health`
- Returns: `{"status": "healthy", "timestamp": "..."}`

---

## 🚀 Production Optimization

### Backend Performance:
```bash
# Increase workers for better concurrency
gunicorn wsgi:app --workers 4 --threads 2 --timeout 120

# Enable gzip compression
gunicorn wsgi:app --workers 2 --threads 4 --worker-class gthread
```

### Frontend Performance:
- Already optimized with Vite
- Static assets served via CDN
- Lazy loading for components
- Code splitting enabled

### Database Optimization:
- Add indexes to frequently queried columns
- Use pagination for large datasets
- Enable WAL mode for SQLite
- Regular cleanup of old records

---

## 📝 Deployment Checklist

### Before Deploying:
- [ ] Test locally with production settings
- [ ] Update all dependencies to latest stable
- [ ] Generate secure secret keys
- [ ] Backup any local database data
- [ ] Test file upload functionality
- [ ] Verify all API endpoints work
- [ ] Check authentication flows

### After Deploying:
- [ ] Test login with all user roles
- [ ] Upload test image/video
- [ ] Check analytics dashboard
- [ ] Verify PDF export works
- [ ] Test CSV export
- [ ] Check heatmap visualization
- [ ] Verify historical data loads
- [ ] Test email notifications (if configured)
- [ ] Check mobile responsiveness
- [ ] Monitor logs for errors

### Post-Deployment:
- [ ] Update README with deployment URLs
- [ ] Document environment variables
- [ ] Set up monitoring/alerts
- [ ] Schedule regular backups
- [ ] Plan for database migrations
- [ ] Configure custom domain (optional)
- [ ] Set up SSL certificates (automatic on Render)

---

## 🎉 Success!

Your HAL Drone Surveillance System is now live at:
- **Frontend:** `https://hal-drone-surveillance-frontend.onrender.com`
- **Backend:** `https://hal-drone-surveillance-backend.onrender.com`

**Default Login:**
- Admin: `admin` / `admin123`
- Operator: `operator` / `operator123`
- Viewer: `viewer` / `viewer123`

**⚠️ IMPORTANT:** Change these passwords immediately after first login!

---

## 📞 Support

- **Render Docs:** https://render.com/docs
- **Render Community:** https://community.render.com
- **GitHub Issues:** Create issue in your repository
- **Email:** support@render.com

---

## 🔗 Useful Links

- [Render Dashboard](https://dashboard.render.com/)
- [Render Documentation](https://render.com/docs)
- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)

---

**Last Updated:** October 16, 2025  
**Status:** ✅ Production Ready
