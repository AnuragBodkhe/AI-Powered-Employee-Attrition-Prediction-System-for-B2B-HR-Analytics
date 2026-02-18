# Testing Guide - Frontend & Backend Integration

## 🚀 Quick Start

### Backend Setup & Testing

```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file (or use existing)
# Should contain:
# DATABASE_URL=sqlite:///./employee_attrition.db
# SECRET_KEY=your-secret-key-here
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30

# 4. Start backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Backend will be available at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Frontend Setup & Testing

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm start

# Frontend will be available at: http://localhost:3000
```

---

## ✅ Backend Testing

### API Documentation
Once backend is running, visit: **http://localhost:8000/docs**

This provides interactive Swagger UI for testing all endpoints.

### Manual Backend Tests

#### 1. **Health Check**
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

#### 2. **Authentication - Register**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "full_name": "Test User"
  }'
```

#### 3. **Authentication - Login**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
# Expected: {"access_token": "...", "refresh_token": "..."}
```

#### 4. **Get Dashboard Metrics** (Requires token from login)
```bash
curl http://localhost:8000/api/dashboard/metrics \
  -H "Authorization: Bearer <your_access_token>"
```

#### 5. **Make Prediction**
```bash
curl -X POST http://localhost:8000/api/predict/manual \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "age": 35,
    "monthly_income": 5000,
    "years_at_company": 5,
    "job_level": 3,
    "satisfaction_score": 3,
    "work_life_balance": 3,
    "years_since_last_promotion": 2
  }'
```

---

## ✅ Frontend Testing

### Test Scenario 1: Complete User Flow

**Step 1: Register New User**
- Visit: http://localhost:3000
- Click "Register" link
- Fill in: Email, Password, Full Name
- Click "Register"
- Should redirect to Dashboard

**Step 2: Navigate Through Pages**
- Click "Employees" → Should show employee list
- Click "Analytics" → Should show charts
- Click "Manual Prediction" → Should show form
- Click "Bulk Upload" → Should show file upload
- Click "Results" → Should show upload history
- Click "Reports" → Should show metrics
- Click "Settings" → Should show preferences

**Step 3: Test Prediction**
- Go to "Manual Prediction"
- Fill form with sample data
- Click "Predict Attrition"
- Should show result with risk level and SHAP values

**Step 4: Test File Upload**
- Go to "Bulk Upload"
- Drag & drop or select employee_attrition_dataset_10000.csv
- Wait for upload progress
- Should show results summary
- Click "Download Results" to verify

**Step 5: Test Results Page**
- Go to "Results"
- Should show upload history
- Click expand on result card
- Should show detailed risk breakdown

### Test Scenario 2: Responsive Design

**Desktop (1920x1080)**
- [ ] Sidebar is fixed on left
- [ ] All pages display properly
- [ ] Tables have all columns visible
- [ ] Forms display in grid layout
- [ ] No horizontal scrolling

**Tablet (768x1024)**
- [ ] Sidebar may collapse (or similar behavior)
- [ ] Content adjusts to available width
- [ ] Forms stack to 2 columns
- [ ] All buttons easily clickable

**Mobile (375x667 - iPhone)**
- [ ] Sidebar appears as hamburger menu
- [ ] Navbar is compact
- [ ] Forms stack to 1 column
- [ ] Touch targets are adequate (44px+)
- [ ] Text is readable without zoom

### Test Scenario 3: Form Validation

**Manual Prediction Form**
- [ ] Try submitting empty form → Should show validation errors
- [ ] Fill partially → Should highlight required fields
- [ ] Fill all fields → Should submit successfully
- [ ] Check error message styling

**Bulk Upload Form**
- [ ] Try uploading wrong file format → Should show error
- [ ] Upload valid CSV → Should show progress
- [ ] After completion → Should show results summary

### Test Scenario 4: Data Display

**Dashboard**
- [ ] KPI cards show correct metrics
- [ ] Charts render properly
- [ ] Filter dropdowns work
- [ ] Export button works

**Employees Table**
- [ ] Filters update results in real-time
- [ ] Pagination works
- [ ] Sorting works on columns
- [ ] Export downloads Excel file

**Analytics**
- [ ] All charts load
- [ ] Charts are responsive and resize properly
- [ ] Legends work on charts
- [ ] Insights section displays

**Results**
- [ ] Upload history loads
- [ ] Expandable cards show details
- [ ] Download button works
- [ ] Status badges show correct colors

---

## 🔍 Common Issues & Solutions

### Issue: Backend won't start
**Solution:**
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# If in use, either:
# 1. Kill the process
# 2. Change port: python -m uvicorn app.main:app --port 8001
```

### Issue: Frontend won't connect to backend
**Solution:**
- Check if backend is running on http://localhost:8000
- Check browser console (F12) for CORS errors
- Verify API endpoint URLs in frontend/src/services/api.js

### Issue: CORS errors
**Solution:**
- Backend should have CORS middleware enabled
- Check frontend is accessing correct backend URL
- Verify allowed origins in backend config

### Issue: Forms not submitting
**Solution:**
- Check browser console (F12) for JavaScript errors
- Verify all required fields are filled
- Check network tab to see API response
- Verify JWT token is valid (check localStorage)

### Issue: File upload not working
**Solution:**
- Check file size (should be under 10MB for demo)
- Verify file format is CSV
- Check backend is running
- Check network connectivity

### Issue: Navigation items don't work
**Solution:**
- Hard refresh browser (Ctrl+F5)
- Clear browser cache
- Check console for routing errors
- Verify all routes are in App.js

---

## 📊 Data for Testing

### Sample Employee Data
File: `employee_attrition_dataset_10000.csv`
- Contains: 10,000 employee records
- Use for bulk upload testing
- Covers all prediction fields

### Manual Prediction Sample Values
```json
{
  "age": 35,
  "monthly_income": 5000,
  "years_at_company": 5,
  "job_level": 3,
  "satisfaction_score": 3,
  "work_life_balance": 3,
  "years_since_last_promotion": 2
}
```

---

## 🎯 Success Criteria

### ✅ Backend Pass Criteria
- [ ] Server starts without errors
- [ ] API docs load at /docs
- [ ] User can register and login
- [ ] Predictions return valid results
- [ ] Dashboard metrics load
- [ ] File upload processes CSV
- [ ] All endpoints return proper status codes

### ✅ Frontend Pass Criteria
- [ ] Application loads without errors
- [ ] All 9 pages are accessible via navigation
- [ ] Forms submit and show results
- [ ] API responses display correctly
- [ ] Mobile responsive on all breakpoints
- [ ] No console JavaScript errors
- [ ] All animations work smoothly
- [ ] Logout/session management works

### ✅ Integration Pass Criteria
- [ ] Backend and Frontend communicate correctly
- [ ] User sessions persist
- [ ] Prediction results shown properly
- [ ] File uploads process end-to-end
- [ ] Charts render with data
- [ ] Filters work on all pages

---

## 📱 Device Testing Sizes

```
iPhone SE (375x667)      - Small phone
iPhone 12 (390x844)      - Standard phone
iPhone 12 Pro (390x844)  - Standard phone
iPad (768x1024)          - Tablet
iPad Pro (1024x1366)     - Large tablet
Laptop (1366x768)        - Standard desktop
Desktop (1920x1080)      - Full HD desktop
2K Screen (2560x1440)    - High resolution
```

---

## 🐛 Debug Mode

### Enable Verbose Logging
In frontend/.env:
```
REACT_APP_DEBUG=true
```

In backend/.env:
```
LOG_LEVEL=DEBUG
```

### Browser DevTools
- F12 or Right-click → Inspect
- **Console tab** - Check for JavaScript errors
- **Network tab** - Monitor API calls and responses
- **Application tab** - Check localStorage (JWT tokens)
- **Responsive Design Mode** (Ctrl+Shift+M) - Test mobile sizes

---

## 📝 Performance Benchmarks

Targets for responsive experience:

```
Page Load:           < 3 seconds
API Response:        < 1 second
Navigation:          < 500ms
Form Submission:     < 2 seconds
File Upload:         Depends on file size (progress shown)
Charts Rendering:    < 1 second
```

---

## ✨ Final Checklist

Before considering complete:
- [ ] Backend runs without errors
- [ ] Frontend runs without errors
- [ ] All 9 pages are functional
- [ ] Mobile responsive (tested in DevTools)
- [ ] Forms submit successfully
- [ ] File upload works
- [ ] Charts display
- [ ] Navigation works
- [ ] Logout works
- [ ] No console errors

---

**Ready to Test! 🚀**

If you encounter any issues, check the browser console (F12) and backend logs for detailed error messages.
