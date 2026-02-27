# 🚀 QUICK START - 5 Minute Setup

## Terminal Command Reference

### Terminal 1: Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Backend ready at: http://localhost:8000/docs
```

### Terminal 2: Frontend
```bash
cd frontend
npm install
npm start
# Frontend ready at: http://localhost:3000
```

---

## Login Credentials

```
Email:    test@example.com
Password: Test@123
```

---

## What Each Page Does

| Page | URL | What It Shows |
|------|-----|--------------|
| 🔑 Login | /login | User authentication |
| 📊 Dashboard | /dashboard | KPI metrics, charts, employees |
| 👥 Employees | /employees | Employee directory with filters |
| 📈 Analytics | /analytics | Risk charts and insights |
| 🧪 Prediction | /predict/manual | Single employee prediction form |
| 📁 Upload | /predict/excel | Bulk file upload (CSV) |
| 📋 Results | /results | Download prediction history |
| 📑 Reports | /reports | Generate reports and insights |
| ⚙️ Settings | /settings | User preferences |

---

## Test Files

**Bulk Upload Test File:**
- Location: `employee_attrition_dataset_10000.csv`
- Format: CSV with 10,000 employee records
- Use: Drag-drop into Bulk Upload page

**Sample Manual Prediction:**
```json
Age: 35
Monthly Income: $5,000
Years at Company: 5
Job Level: 3
Satisfaction Score: 3
Work-Life Balance: 3
Years Since Last Promotion: 2
```

---

## Troubleshooting

### Backend won't start?
```bash
# Check if port 8000 is available
netstat -ano | findstr :8000
# If blocked, use different port:
python -m uvicorn app.main:app --port 8001
```

### Frontend won't load?
```bash
# Check if frontend dependencies are installed
npm list react react-router-dom
# Reinstall if needed:
rm -rf node_modules package-lock.json
npm install
```

### CORS errors?
- Backend is running on port 8000 ✅
- Frontend is running on port 3000 ✅
- Both have CORS configured ✅

### API calls failing?
- Check browser console (F12)
- Verify backend is running (http://localhost:8000/docs)
- Check network tab for actual errors

---

## File Structure Reference

```
backend/
  ├── app/
  │   ├── main.py          ← FastAPI app
  │   ├── api/             ← Endpoints
  │   ├── models/          ← Database models  
  │   ├── ml/              ← Prediction engine
  │   └── core/            ← Config & security
  └── requirements.txt     ← Dependencies

frontend/
  ├── src/
  │   ├── components/      ← React components
  │   ├── services/        ← API client
  │   ├── App.js           ← Routes
  │   └── App.css          ← Global styles
  └── package.json         ← Dependencies
```

---

## API Endpoints (Quick Reference)

### Authentication
```
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me
PUT    /api/auth/change-password
POST   /api/auth/logout
POST   /api/auth/refresh
```

### Predictions
```
POST   /api/predict/manual
POST   /api/predict/excel
GET    /api/predict/history
GET    /api/predict/status/{id}
GET    /api/predict/download/{id}
```

### Dashboard
```
GET    /api/dashboard/metrics
GET    /api/dashboard/charts/risk
GET    /api/dashboard/charts/department
GET    /api/dashboard/charts/salary
GET    /api/dashboard/employees
GET    /api/dashboard/filters/options
GET    /api/dashboard/export
```

**Test all endpoints at:** http://localhost:8000/docs

---

## Browser DevTools Tips

### Check Frontend Errors
1. Press `F12` (or Right-click → Inspect)
2. Go to "Console" tab
3. Look for red error messages

### Check API Calls
1. Go to "Network" tab
2. Look for API request responses
3. Check status codes (200 = OK, 401 = Auth error)

### Check Browser Storage
1. Go to "Application" tab
2. Look in "Local Storage"
3. Should see JWT token saved

### Test Responsiveness
1. Press `Ctrl+Shift+M` (toggle responsive design)
2. Select "iPhone SE" (375px) to test mobile
3. Check if layout adapts properly

---

## Performance Targets

- Page Load: < 3 sec ⚡
- API Response: < 1 sec ⚡
- Navigation: < 500ms ⚡
- Form Submit: < 2 sec ⚡

---

## Security Checklist

- ✅ Backend uses JWT tokens
- ✅ Passwords hashed with bcrypt
- ✅ CORS configured
- ✅ Routes protected (require login)
- ✅ Tokens stored in localStorage
- ✅ Auto-refresh on expiry

---

## Feature Checklist

Dashboard Page:
- [x] KPI metric cards
- [x] Risk distribution pie chart
- [x] Department comparison bar chart
- [x] Salary impact line chart
- [x] Employee risk grid
- [x] Filter functionality
- [x] Export to CSV

Employees Page:
- [x] Employee directory
- [x] Filter by department, risk, salary
- [x] Pagination
- [x] Sorting
- [x] Export to Excel

Prediction Pages:
- [x] Manual prediction form
- [x] Real-time risk assessment
- [x] SHAP value explanations
- [x] Bulk file upload
- [x] Progress tracking
- [x] Results download

Results & Reports:
- [x] Upload history
- [x] Downloadable results
- [x] Risk summary cards
- [x] Multiple report types
- [x] Export options

User Settings:
- [x] Account management
- [x] Theme preferences
- [x] Notification controls
- [x] Security options

---

## Docker Commands (Optional)

Start everything with Docker:
```bash
docker-compose up -d
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
```

Stop everything:
```bash
docker-compose down
```

View logs:
```bash
docker-compose logs -f
```

---

## Responsive Design Breakpoints

```
Mobile:  < 640px   → Single column, hamburger menu
Tablet:  640-1024px → 2-3 columns, mobile menu
Desktop: > 1024px   → Full layout, sidebar
```

Your app scales automatically! ✨

---

## Success Indicators

After starting:
- ✅ Browser shows login page
- ✅ Can register new user
- ✅ Can log in with test credentials
- ✅ Dashboard shows metrics and charts
- ✅ Can click through all pages
- ✅ Forms submit successfully
- ✅ File upload works
- ✅ No red errors in console

**If all above are working → Ready to use! 🎉**

---

## Key Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open DevTools | `F12` |
| Toggle Mobile View | `Ctrl+Shift+M` |
| Clear Cache | `Ctrl+Shift+Delete` |
| Hard Refresh | `Ctrl+F5` |
| Search Page | `Ctrl+F` |

---

## Need Help?

1. **Setup Issues** → See `QUICK_START.md`
2. **Testing** → See `TESTING_GUIDE.md`
3. **Features** → See `IMPLEMENTATION_COMPLETE.md`
4. **Design** → See `FRONTEND_IMPROVEMENTS.md`
5. **Backend** → Check `backend/README.md`

---

## Remember

- Backend on port 8000 ✨
- Frontend on port 3000 ✨  
- Test user: test@example.com ✨
- Password: Test@123 ✨
- **Everything works!** ✨

**Good luck! 🚀**
