# 🚀 QUICK START - Deploy to Render in 15 Minutes

## Prerequisites (2 minutes)
- [ ] GitHub account with your project repository
- [ ] Render account (sign up free at render.com)
- [ ] 2 secure keys generated (see below)

---

## Step 1: Generate Secure Keys (1 minute)

Run this command:
```bash
cd backend
python generate_keys.py
```

Copy the two keys that appear. You'll need them in Step 3.

---

## Step 2: Deploy Backend (10 minutes)

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com/
   - Click: **"New +"** → **"Web Service"**

2. **Connect Repository**
   - Select your GitHub repository
   - Click **"Connect"**

3. **Configure Service**
   ```
   Name:                hal-drone-backend
   Region:              Oregon (US West) or nearest
   Branch:              main
   Root Directory:      backend
   Runtime:             Python 3
   Build Command:       pip install -r requirements.txt
   Start Command:       gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --threads 4
   ```

4. **Add Environment Variables**
   Click **"Advanced"** → **"Add Environment Variable"**
   
   Add these (use your generated keys from Step 1):
   ```
   JWT_SECRET_KEY       <paste-key-1-here>
   SECRET_KEY           <paste-key-2-here>
   FLASK_ENV            production
   FLASK_DEBUG          False
   ```

5. **Create Service**
   - Click **"Create Web Service"**
   - Wait 5-10 minutes for deployment
   - Copy your backend URL: `https://xxx.onrender.com`

---

## Step 3: Deploy Frontend (5 minutes)

1. **Create Static Site**
   - Click: **"New +"** → **"Static Site"**
   - Select your repository

2. **Configure Site**
   ```
   Name:                hal-drone-frontend
   Branch:              main
   Root Directory:      drone-surveillance-frontend
   Build Command:       npm install && npm run build
   Publish Directory:   dist
   ```

3. **Add Environment Variable**
   ```
   VITE_API_URL         <paste-backend-url-from-step-2>
   ```
   Example: `https://hal-drone-backend.onrender.com`

4. **Create Static Site**
   - Click **"Create Static Site"**
   - Wait 2-3 minutes
   - Copy your frontend URL: `https://yyy.onrender.com`

---

## Step 4: Update CORS (2 minutes)

1. Go back to **Backend Service** in Render
2. Click **"Environment"**
3. Add new variable:
   ```
   CORS_ORIGINS         <paste-frontend-url-from-step-3>
   ```
   Example: `https://hal-drone-frontend.onrender.com`
4. Click **"Save Changes"**
5. Service will auto-redeploy (1-2 minutes)

---

## Step 5: Test Deployment (5 minutes)

1. **Open Your App**
   - Visit: `https://your-frontend.onrender.com`

2. **Login**
   - Username: `admin`
   - Password: `admin123`

3. **Test Features**
   - [ ] Dashboard loads
   - [ ] Upload an image (test detection)
   - [ ] Check Analytics
   - [ ] View Heatmap
   - [ ] Check History
   - [ ] Generate PDF report

4. **Change Password** (IMPORTANT!)
   - This is a demo password
   - Change it immediately after first login

---

## 🎉 Success!

Your HAL Drone Surveillance System is now live!

**URLs:**
- Frontend: `https://your-frontend.onrender.com`
- Backend: `https://your-backend.onrender.com`

**Login:**
- Admin: `admin` / `admin123` ⚠️ CHANGE THIS
- Operator: `operator` / `operator123`
- Viewer: `viewer` / `viewer123`

---

## ⚠️ Important Notes

### Free Tier Limitations:
- Backend spins down after 15 min inactivity
- First request after spin-down takes 30-60 seconds
- Database resets on restart (no persistent storage)
- 512MB RAM (sufficient for YOLOv8n)

### Upgrade to Paid ($7/month) for:
- Always-on backend (no spin-down)
- Persistent disk storage
- Better performance
- Production use

---

## 🐛 Troubleshooting

### "Network Error" in frontend:
- Check VITE_API_URL is correct
- Verify CORS_ORIGINS includes frontend URL
- Check backend logs for errors

### Backend build fails:
- Verify Python version in runtime.txt
- Check requirements.txt syntax
- Review build logs in Render dashboard

### Authentication fails:
- Verify JWT_SECRET_KEY is set
- Check backend logs
- Try clearing browser cache/cookies

### Need Help?
- Read: `RENDER_DEPLOYMENT.md` (detailed guide)
- Check: `DEPLOYMENT_CHECKLIST.md` (troubleshooting)
- View: Backend logs in Render dashboard

---

## 📱 Share Your Project

Once deployed, share these links:
- **Live Demo:** Your frontend URL
- **GitHub:** Your repository
- **Documentation:** README.md

---

**Deployment Time:** 15-20 minutes  
**Difficulty:** Easy  
**Cost:** Free (or $7/month for production)

**Congratulations on your deployment! 🚀**
