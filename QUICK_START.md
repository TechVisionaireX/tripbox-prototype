# 🚀 TripBox Quick Start Guide

## Immediate Setup (Windows)

1. **Open PowerShell/Command Prompt in the project folder**

2. **Install dependencies and setup:**
   ```cmd
   start.bat
   ```

3. **Start the backend:**
   ```cmd
   python app.py
   ```
   
   You should see:
   ```
   🚀 Starting TripBox-IntelliOrganizer on port 5000
   * Running on http://127.0.0.1:5000
   ```

4. **Open the frontend:**
   - Double-click `frontend/index.html` 
   - Or drag it to your browser

5. **Login with test credentials:**
   - **Email:** `test@test.com`
   - **Password:** `test123`

## ✅ Verification Steps

1. **Test backend is running:**
   - Open: http://localhost:5000/health
   - Should show: `{"status":"healthy",...}`

2. **Test login page:**
   - Open: `test-login.html` in browser
   - Should show "✅ Connected" status
   - Try logging in with test credentials

## 🔧 Troubleshooting

### "Network Error" on Login
1. **Check backend is running:**
   ```cmd
   python app.py
   ```

2. **Check the browser console (F12):**
   - Look for CORS errors
   - Verify API_BASE URL is correct

3. **Test API directly:**
   ```cmd
   curl http://localhost:5000/health
   ```

### Database Issues
1. **Reset database:**
   ```cmd
   cd backend
   del tripbox.db
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

2. **Recreate test user:**
   ```cmd
   python -c "from app import app, db; from models import User; from auth import bcrypt; app.app_context().push(); db.session.add(User(email='test@test.com', password=bcrypt.generate_password_hash('test123').decode('utf-8'), name='Test User')); db.session.commit()"
   ```

### Port 5000 Already in Use
1. **Find and kill process:**
   ```cmd
   netstat -ano | findstr :5000
   taskkill /PID <PID_NUMBER> /F
   ```

2. **Or use different port:**
   ```cmd
   set PORT=5001 && python app.py
   ```

## 🌐 Production Deployment

### Backend (Render)
1. Push code to GitHub
2. Connect GitHub repo to Render
3. Use these settings:
   - **Build Command:** `cd backend && chmod +x build.sh && ./build.sh`
   - **Start Command:** `cd backend && gunicorn app:app --timeout 120 --bind 0.0.0.0:$PORT`

### Frontend (Netlify)
1. Drag `frontend` folder to Netlify
2. Set build directory to `frontend`
3. Deploy!

## 📱 Features Available

- ✅ User Authentication
- ✅ Trip Management
- ✅ Expense Tracking
- ✅ Photo Gallery
- ✅ Checklists
- ✅ Real-time Chat
- ✅ Location Check-in
- ✅ Polls & Voting
- ✅ PDF Generation
- ✅ AI Recommendations

## 🆘 Still Having Issues?

1. **Run the test login page:** `test-login.html`
2. **Check browser console for errors (F12)**
3. **Verify all files are present**
4. **Make sure Python 3.8+ is installed**

---

**Your TripBox application should now be running perfectly! 🎉** 