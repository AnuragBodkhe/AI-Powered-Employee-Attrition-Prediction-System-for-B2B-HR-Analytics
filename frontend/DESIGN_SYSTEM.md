# HR Analytics Dashboard - Modern Design System

## 🎨 Visual Design Language

This document outlines the enterprise-grade, minimalistic design system implemented for the AI-Powered Employee Attrition Prediction System.

### Color Palette

#### Primary Colors
- **Deep Blue/Indigo**: `#4f46e5` → Gradient to `#3730a3`
  - Used for primary CTAs, accents, and active states
  - Conveys trust, professionalism, and intelligence

- **Neutral Grays**: Slate palette
  - `#111827` - Text/darkest
  - `#374151` - Secondary text
  - `#6b7280` - Tertiary text
  - `#f9fafb` - Light backgrounds

#### Accent & Status Colors
- **Teal/Emerald** `#14b8a6` - Success, positive insights
- **Red** `#ef4444` - High risk, warnings
- **Amber** `#f59e0b` - Medium risk, cautions
- **Green** `#10b981` - Low risk, positive signals

### Typography

- **Font Family**: Inter (Google Fonts)
- **Font Weights**:
  - Bold (800): Large headings, CTAs
  - Semibold (700): Section titles, labels
  - Medium (600): Emphasis, secondary text
  - Regular (400): Body text

- **Scale**:
  - `h1`: 2rem (32px), font-weight 800
  - `h2`: 1.5rem (24px), font-weight 700
  - `h3`: 1.25rem (20px), font-weight 700
  - Body: 0.95rem (15px), line-height 1.6

### Spacing System

- Base unit: 4px
- Scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64

Used consistently across:
- Padding (p-*, px-*, py-*)
- Margins (m-*, mx-*, my-*)
- Gaps (gap-*)

### Border Radius

- Small elements: 6-8px
- Cards & containers: 12px
- Large modals/containers: 16px+
- Circles: 50%

### Shadows

- **xs**: `0 1px 2px 0 rgba(0, 0, 0, 0.05)`
- **sm**: Hover states
- **md**: Cards, interactive elements
- **lg**: Elevated modals, important actions
- **elevated**: Special emphasis, gradient-tinted `rgba(79, 70, 229, 0.15)`

## 🧩 Component Design

### Buttons

#### Primary Button
- Background: Gradient (indigo 600 → 700)
- Text: White
- Padding: 10px 20px, rounded-8px
- Hover: Lifted (translateY -2px), enhanced shadow
- Disabled: Gray background, no shadow

```jsx
<button className="btn-primary py-3 px-6 rounded-lg font-semibold">
  Action
</button>
```

#### Secondary Button
- Background: White
- Border: 1.5px solid slate-200
- Text: Indigo 600
- Hover: Light gray background

#### Danger Button
- Background: Light red
- Border: Light red
- Text: Dark red

### Cards

- Background: White
- Border: 1px solid slate-200
- Padding: 20px
- Border-radius: 12px
- Shadow: Subtle `0 1px 3px`
- Hover: Enhanced shadow, subtle border brightening

```jsx
<div className="card">
  <h2 className="text-lg font-bold text-slate-900 mb-4">Title</h2>
  <p className="text-slate-600">Content</p>
</div>
```

### Form Elements

#### Input Fields
- Padding: 12px 14px
- Border: 2px solid slate-200
- Border-radius: 8px
- Font: 0.95rem inherit
- Focus: Border indigo-500, shadow ring rgba(79, 70, 229, 0.1)
- Background: White, hover to light gray

#### Labels
- Font-size: 0.95rem
- Font-weight: 600
- Color: slate-700
- Margin-bottom: 8px

#### Selects
- Same styling as inputs
- Rounded corners: 8px

### Badges & Pills

```jsx
<div className="badge badge-success">Low Risk</div>
<div className="badge badge-warning">Medium Risk</div>
<div className="badge badge-danger">High Risk</div>
```

## 📊 Dashboard Layout

### Metrics Cards (KPIs)

- **Grid**: 3 columns on desktop, 2 on tablet, 1 on mobile
- **Background**: Gradient backgrounds (different for each metric)
- **Content**: 
  - Icon (emoji or simple SVG)
  - Label + trend indicator
  - Large bold value
  - Timeframe indicator

### Charts

#### Risk Distribution (Pie Chart)
- Colors: Red, Amber, Green for risk levels
- Smooth animations
- Tooltip on hover
- Legend at bottom

#### Department Comparison (Bar Chart)
- X-axis: Department names
- Y-axis: Metrics (count, rate, score)
- Multiple series with distinct colors
- Rounded bar tops

#### Salary Impact (Line Chart)
- X-axis: Salary ranges
- Multiple lines for different metrics
- Smooth curves
- Interactive dots on hover

### Employee Table

- Header: Bold labels, light gray background
- Rows: White background, hover to light gray
- Alternating colors (subtle visual separation)
- Columns:
  1. Employee avatar + name/ID
  2. Department
  3. Role
  4. Risk score (progress bar + percentage)
  5. Risk level (colored badge)
  6. Experience
  7. View button (text link)

### Pagination

- Page buttons (numbered)
- Current page: Indigo background
- Previous/Next arrows
- Text showing range (e.g., "Showing 1-10 of 45")

## 🧭 Navigation & Layout

### Navbar
- Position: Fixed top, sticky
- Background: White
- Border-bottom: 1px solid slate-200
- Content:
  - Logo + brand name (left)
  - Search bar (center, hidden on mobile)
  - Notifications + profile dropdown (right)
- Shadow: Subtle

### Sidebar
- Position: Fixed left, 256px width (hidden on mobile, collapsible)
- Background: White
- Border-right: 1px solid slate-200
- Navigation items:
  - Group headers (uppercase, small text, gray)
  - Links with icons and labels
  - Active state: Light indigo background + left border + indicator dot
- Bottom section: AI insights card (teal background)

### Main Content
- Max-width: 1280px centered
- Padding: 32-48px (responsive)
- Spacing between sections: 32px

## 🎬 Animations & Interactions

### Transitions
- Standard duration: 0.3s `cubic-bezier(0.4, 0, 0.2, 1)`
- Hover effects: Smooth color/shadow transitions
- Loading: Spinner with CSS animation

### Hover Effects
- Buttons: Lift effect, shadow enhancement, color deepening
- Cards: Shadow increase, subtle border brightening
- Links: Color change to indigo, underline optional

### Loading States
- Spinner: Animated border (top color = primary color)
- Pulse animations for skeleton screens
- Progress bars with smooth transitions

### Feedback Messages

#### Success
- Background: `#d1fae5` (light green)
- Border: `#a7f3d0` (border green)
- Text: `#065f46` (dark green)
- Icon: ✓

#### Error
- Background: `#fee2e2` (light red)
- Border: `#fecaca` (border red)
- Text: `#991b1b` (dark red)
- Icon: ⚠️

#### Warning
- Background: `#fef3c7` (light amber)
- Border: `#fde68a` (border amber)
- Text: `#92400e` (dark amber)

## 📱 Responsive Design

### Breakpoints (Tailwind)
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### Layout Changes
- **Mobile**: 
  - Single column layouts
  - Sidebar hidden (hamburger menu)
  - Full-width inputs and buttons
  - Stacked charts

- **Tablet**: 
  - 2-column layouts
  - Sidebar hidden by default
  - Adjusted spacing
  - Horizontal scrolling for wide tables

- **Desktop**: 
  - Full layouts (3+ columns)
  - Sidebar visible
  - Optimal spacing and sizing

## 🧠 AI Feel

### Visual Cues
- **Spark icons** (✦) for AI features
- **Lightbulb icons** (💡) for AI insights
- **Gradient backgrounds** for special sections
- **Animated elements** for data processing

### Confidence Indicators
- Progress bars showing prediction confidence
- Percentage displays with visual emphasis
- Tooltip explanations on hover

### Insights Cards
- Teal gradient background for positive insights
- Blue background for general information
- Icons for visual hierarchy
- Human-readable explanations

## 🎨 Specific Page Designs

### Login Page
- Centered layout
- Gradient background (indigo + teal decorative circles)
- White card with rounded corners
- Subtle shadows
- Clear hierarchy: Logo → Title → Form → Link
- Smooth animations on form submission

### Dashboard
- Grid of metric cards (6 items, 3 columns)
- Filter panel with collapsible state
- Charts in 2-column layout (risk distribution + salary impact)
- Department chart spanning full width
- Employee table with pagination
- AI insights card at bottom (full width, special styling)

### Manual Prediction
- Multi-step form with grouped sections
- Each section: Icon + title + fields grid
- Slider inputs with visual feedback
- Large prediction button

### Bulk Upload
- 2/3 + 1/3 layout on desktop
- Main section: Drag-and-drop area
- Sidebar: Requirements + template download
- Progress indicator during upload
- Results card with breakdown

## 💾 Implementation Notes

### Tailwind CSS Classes Used
- Color system: `bg-{color}-{shade}`, `text-{color}-{shade}`
- Spacing: `p-*`, `m-*`, `gap-*`
- Sizing: `w-*`, `h-*`
- Layout: `flex`, `grid`, `gap-*`, `grid-cols-*`
- Responsiveness: `lg:`, `md:`, `sm:` prefixes
- Interactive: `hover:`, `focus:`, `active:`, `disabled:`

### Custom CSS Classes
- `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.btn-success`, `.btn-icon`
- `.badge`, `.badge-success`, `.badge-warning`, `.badge-danger`
- `.card`, `.card.elevated`
- `.error-message`, `.success-message`, `.warning-message`
- `.loading`, `.loading-spinner`
- `.table-responsive`, `table`, `thead`, `th`, `td`

### Font Stack
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
```

## 🔄 Data Visualization Best Practices

1. **Clarity First**: Charts prioritize readability over aesthetics
2. **Color Consistency**: Risk levels always use red/amber/green
3. **Tooltips**: Hover information for detailed data
4. **Legends**: Always included for chart interpretation
5. **Labels**: Clear axes and data labels
6. **Animations**: Smooth transitions, not distracting

## ✅ Quality Checklist

- [ ] Consistent spacing and alignment throughout
- [ ] All interactive elements have hover/focus states
- [ ] Loading states are visually distinct
- [ ] Error messages are clear and actionable
- [ ] Success feedback is positive and encouraging
- [ ] Colors provide sufficient contrast (WCAG AA)
- [ ] No text is justified (improves readability)
- [ ] Shadows are subtle and purposeful
- [ ] Animations serve a functional purpose
- [ ] Mobile layout is single-column and touch-friendly

---

**Last Updated**: February 2024
**Framework**: React + Tailwind CSS
**Design Tool**: As-coded (No Figma)
