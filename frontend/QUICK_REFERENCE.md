# ⚡ Quick Reference - Common Tasks

## 🚀 Quick Commands

```bash
# Install & run
npm install
npm start

# Production build
npm run build

# Check errors
npm run lint
```

## 🎨 Common CSS Patterns

### Responsive Grid (3-col desktop, 2-col tablet, 1-col mobile)
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map(item => <div key={item.id}>{item}</div>)}
</div>
```

### Card Component
```jsx
<div className="bg-white rounded-xl shadow-sm hover:shadow-md p-6 transition-shadow">
  <h3 className="text-lg font-bold text-slate-900 mb-2">Title</h3>
  <p className="text-slate-600">Description</p>
</div>
```

### Form Input Group
```jsx
<div className="form-group">
  <label className="block text-sm font-semibold text-slate-700 mb-2">
    Input Label
  </label>
  <input
    type="text"
    className="w-full px-4 py-2.5 rounded-lg border-2 border-slate-200 
               focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 
               transition-colors"
    placeholder="Enter value"
  />
</div>
```

### Button Variants
```jsx
// Primary
<button className="btn-primary py-3 px-6 rounded-lg font-semibold">
  Primary Button
</button>

// Secondary
<button className="btn-secondary py-2 px-4 rounded-lg font-semibold">
  Secondary Button
</button>

// Danger
<button className="btn-danger py-2 px-4 rounded-lg font-semibold">
  Delete
</button>

// With Icon
<button className="btn-icon">
  <svg className="w-5 h-5" fill="currentColor">
    {/* SVG path */}
  </svg>
</button>
```

### Status Badge
```jsx
<span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold">
  {risk === 'High' && <span className="badge badge-danger">🔴 High Risk</span>}
  {risk === 'Medium' && <span className="badge badge-warning">🟡 Medium Risk</span>}
  {risk === 'Low' && <span className="badge badge-success">🟢 Low Risk</span>}
</span>
```

### Loading Spinner
```jsx
{isLoading ? (
  <div className="flex justify-center items-center py-12">
    <div className="animate-spin rounded-full h-12 w-12 border-2 border-indigo-200 border-t-indigo-600"></div>
  </div>
) : (
  <div>Content</div>
)}
```

## 🎨 Color Reference

### Tailwind Colors Used
```
Primary: indigo-600, indigo-500, indigo-400
Danger: red-500, red-600
Warning: amber-500, amber-600
Success: green-500, green-600
Accent: teal-500, teal-600
Neutral: slate-50 to slate-900
```

### Usage Examples
```jsx
// Text
<p className="text-slate-600">Neutral text</p>
<p className="text-indigo-600 font-bold">Primary text</p>
<p className="text-red-600">Error text</p>

// Background
<div className="bg-indigo-50">Light background</div>
<div className="bg-red-500 text-white">Alert</div>
<div className="bg-gradient-to-r from-slate-50 to-slate-100">Gradient</div>

// Borders
<div className="border border-slate-200">Light border</div>
<div className="border-2 border-indigo-500">Thick primary border</div>
```

## 📊 Chart Quick Setup

### Basic Pie Chart
```jsx
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const data = [
  { name: 'Low', value: 60, fill: '#10b981' },
  { name: 'Medium', value: 25, fill: '#f59e0b' },
  { name: 'High', value: 15, fill: '#ef4444' },
];

<ResponsiveContainer width="100%" height={300}>
  <PieChart>
    <Pie data={data} cx="50%" cy="50%" labelLine={false} label>
      {data.map((entry, index) => (
        <Cell key={`cell-${index}`} fill={entry.fill} />
      ))}
    </Pie>
    <Tooltip formatter={(value) => `${value}%`} />
    <Legend />
  </PieChart>
</ResponsiveContainer>
```

### Basic Bar Chart
```jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Dept A', attrition: 12, employees: 45 },
  { name: 'Dept B', attrition: 8, employees: 52 },
];

<ResponsiveContainer width="100%" height={300}>
  <BarChart data={data}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="name" />
    <YAxis />
    <Tooltip />
    <Legend />
    <Bar dataKey="attrition" fill="#ef4444" />
    <Bar dataKey="employees" fill="#4f46e5" />
  </BarChart>
</ResponsiveContainer>
```

## 🔄 State Management Patterns

### useState for Form
```jsx
const [formData, setFormData] = useState({
  name: '',
  email: '',
  department: '',
});

const handleChange = (e) => {
  const { name, value } = e.target;
  setFormData(prev => ({ ...prev, [name]: value }));
};

return (
  <input
    name="name"
    value={formData.name}
    onChange={handleChange}
    type="text"
  />
);
```

### useEffect for Data Loading
```jsx
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

useEffect(() => {
  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dashboard');
      setData(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  fetchData();
}, []); // Empty dependency = run once on mount

return loading ? <Spinner /> : error ? <Error msg={error} /> : <Content data={data} />;
```

### useState for Toggle/Modal
```jsx
const [isOpen, setIsOpen] = useState(false);

return (
  <>
    <button onClick={() => setIsOpen(!isOpen)}>
      {isOpen ? 'Close' : 'Open'}
    </button>
    {isOpen && <Modal onClose={() => setIsOpen(false)} />}
  </>
);
```

## 📱 Responsive Utilities

### Hide/Show by Breakpoint
```jsx
<div className="hidden lg:block">Desktop only</div>
<div className="block lg:hidden">Mobile/Tablet only</div>
<div className="hidden md:block lg:hidden">Tablet only</div>
```

### Responsive Spacing
```jsx
<div className="p-4 md:p-6 lg:p-8">
  {/* 16px on mobile, 24px on tablet, 32px on desktop */}
</div>
```

### Responsive Text Size
```jsx
<h1 className="text-2xl md:text-3xl lg:text-4xl font-bold">
  {/* 24px mobile, 30px tablet, 36px desktop */}
</h1>
```

### Responsive Grid
```jsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
  {/* 1 col mobile, 2 col tablet, 4 col desktop */}
</div>
```

## 🔗 Navigation Patterns

### React Router Link
```jsx
import { Link } from 'react-router-dom';

<Link 
  to="/dashboard" 
  className="text-indigo-600 hover:text-indigo-700 font-semibold"
>
  Go to Dashboard
</Link>
```

### useNavigate Hook
```jsx
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();

const handleLogout = () => {
  logout();
  navigate('/login');
};
```

### Active Link Styling
```jsx
import { useLocation } from 'react-router-dom';

const location = useLocation();
const isActive = location.pathname === '/dashboard';

<button 
  className={`py-3 px-4 rounded-lg font-semibold transition-colors ${
    isActive 
      ? 'bg-indigo-100 text-indigo-700 border-l-4 border-indigo-600'
      : 'text-slate-700 hover:bg-slate-100'
  }`}
>
  Dashboard
</button>
```

## 🛡️ Form Validation

### Basic Email Validation
```jsx
const validateEmail = (email) => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};
```

### Password Strength
```jsx
const-getPasswordStrength = (password) => {
  if (password.length < 8) return 'weak';
  if (!/[A-Z]/.test(password)) return 'weak';
  if (!/[0-9]/.test(password)) return 'weak';
  return 'strong';
};
```

### Form Error Display
```jsx
{errors.email && (
  <p className="text-red-600 text-sm font-semibold mt-1">
    {errors.email}
  </p>
)}
```

## 🎯 Common Selectors

### Text Truncation
```jsx
<p className="truncate">Long text that gets cut off...</p>
<p className="line-clamp-2">Two lines max...</p>
```

### Hover Effects
```jsx
<div className="hover:shadow-lg hover:scale-105 transition-all cursor-pointer">
  Hoverable card
</div>
```

### Transition Classes
```jsx
<div className="transition-all duration-300 ease-in-out">
  Smooth transition
</div>
```

### Flex Layouts
```jsx
{/* Center content */}
<div className="flex items-center justify-center h-screen">
  <h1>Centered</h1>
</div>

{/* Space between */}
<div className="flex justify-between items-center">
  <span>Left</span>
  <span>Right</span>
</div>

{/* Vertical stack */}
<div className="flex flex-col gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
</div>
```

## 🚨 Debugging Tips

### Check Element in DevTools
1. Right-click element → "Inspect"
2. Look at "Classes" tab → See applied Tailwind classes
3. Check "Styles" tab → See computed CSS

### Debug State
```jsx
useEffect(() => {
  console.log('Component mounted or deps changed');
  console.log('Current data:', data);
}, [data]);
```

### Check API Response
```jsx
const response = await api.get('/endpoint');
console.log('API Response:', response.data);
```

---

**Pro Tips:**
- Use browser DevTools to inspect Tailwind class names
- Test filter and sort logic with console.log()
- Use CSS Grid for complex layouts, Flexbox for simple alignment
- Always reset form state after successful submission
- Test on mobile view in dev tools (F12 → Toggle Device Toolbar)
