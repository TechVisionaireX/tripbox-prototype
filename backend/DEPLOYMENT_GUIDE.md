# TripBox Deployment Guide

## Backend Deployment on Render

### Current Status
- **Backend URL**: https://tripbox-intelliorganizer.onrender.com/
- **Frontend URL**: https://resilient-marshmallow-13df59.netlify.app/

### Steps to Deploy/Update Backend on Render:

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Update backend for production deployment"
   git push origin main
   ```

2. **Configure Environment Variables on Render**:
   - Go to your Render dashboard
   - Navigate to your service settings
   - Add these environment variables:
     - `JWT_SECRET_KEY`: Generate a secure random string (e.g., use https://randomkeygen.com/)
     - `DATABASE_URL`: Will be automatically set if using Render PostgreSQL

3. **Database Setup**:
   - If not already done, create a PostgreSQL database on Render
   - Link it to your web service
   - The `DATABASE_URL` will be automatically configured

4. **Deploy**:
   - Render will automatically deploy when you push to GitHub
   - Or manually trigger a deploy from the Render dashboard

### Frontend Deployment on Netlify:

1. **Ensure all API endpoints use the Render URL**:
   - Replace all `localhost:5000` with `https://tripbox-intelliorganizer.onrender.com`
   - This is already done in your current frontend

2. **Deploy to Netlify**:
   ```bash
   # If using Netlify CLI
   netlify deploy --prod --dir=frontend
   ```
   
   Or drag and drop the `frontend` folder to Netlify dashboard

### Important Notes:

1. **CORS Configuration**: 
   - Backend is configured to accept requests from your Netlify domain
   - Update `app.py` if you change your frontend domain

2. **Database Migrations**:
   - The `build.sh` script automatically creates tables on deployment
   - For future schema changes, consider using Flask-Migrate

3. **Free Tier Limitations**:
   - Render free tier services spin down after inactivity
   - First request after inactivity may take 30-50 seconds
   - Consider upgrading for production use

4. **Security Checklist**:
   - ✅ Use strong JWT_SECRET_KEY
   - ✅ HTTPS enabled by default on both platforms
   - ✅ CORS properly configured
   - ✅ Database credentials secured as environment variables

5. **Monitoring**:
   - Check Render logs for backend errors
   - Use browser developer tools for frontend debugging
   - Monitor database performance in Render dashboard

### Testing Your Deployment:

1. **Test Backend**:
   ```bash
   curl https://tripbox-intelliorganizer.onrender.com/
   # Should return: {"message":"TripBox-IntelliOrganizer backend is running!"}
   ```

2. **Test Frontend**:
   - Visit https://resilient-marshmallow-13df59.netlify.app/
   - Try registering a new user
   - Create a trip and test all features

### Troubleshooting:

1. **Backend not responding**:
   - Check Render logs
   - Verify environment variables are set
   - Ensure database is connected

2. **CORS errors**:
   - Update CORS origins in `app.py`
   - Clear browser cache
   - Check browser console for specific errors

3. **Database issues**:
   - Verify DATABASE_URL is correct
   - Check if tables are created (use Render's database dashboard)
   - Look for migration errors in build logs 