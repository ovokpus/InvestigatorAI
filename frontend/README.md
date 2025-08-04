# InvestigatorAI Frontend

> **📂 Navigation**: [🏠 Home](../README.md) | [🔧 API Docs](../api/README.md) | [🤖 Agent Architecture](../docs/AGENT_PROMPTS.md) | [📈 Advanced Retrievers](../docs/ADVANCED_RETRIEVERS.md) | [💼 Business Case](../docs/BUSINESS_CASE.md) | [🎓 Certification](../docs/CERTIFICATION_CHALLENGE.md) | [🎬 Demo Guide](../docs/DEMO_GUIDE.md) | [💻 Frontend](README.md) | [📊 Data](../data/README.md) | [🚀 Deploy](../deploy/README.md) | [🧪 Tests](../tests/README.md) | [🔄 Merge](../MERGE.md)

A modern Next.js frontend for the InvestigatorAI Multi-Agent Fraud Investigation System.

## 📋 Table of Contents

- [User Guide](#user-guide)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Implementation Playbook](#implementation-playbook)
- [Development Reference](#development-reference)

---

## 👤 User Guide

### 🚀 Features

- **Fraud Investigation Interface**: Submit transaction details for AI-powered fraud analysis
- **Real-time Status Monitoring**: API health checks and system status updates
- **Document Search**: Query regulatory databases and compliance documents
- **Exchange Rate Lookup**: Get current currency exchange rates
- **Interactive Help & Documentation**: Comprehensive user guide with demo examples
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark Blue Theme**: Professional, accessible interface with high contrast

### 🛠️ Technology Stack

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Custom CSS Variables** - Theme customization
- **REST API Integration** - Connects to FastAPI backend

### 📋 Prerequisites

- Node.js 18+ 
- npm or yarn
- InvestigatorAI API running on `http://localhost:8000`

## 🚀 Quick Start

### Installation & Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

## 📖 Usage Guide

### Investigation Workflow

1. **Start New Investigation**
   - Fill in transaction details (amount, currency, customer, etc.)
   - Click "Start Investigation" to begin AI analysis
   - Monitor progress as 4 agents process the case

2. **Review Results**
   - View investigation status and final decision
   - Check detailed transaction analysis
   - See agent progress and completion status

3. **Additional Tools**
   - Navigate to "Tools & Search" for auxiliary features
   - Search regulatory documents
   - Look up current exchange rates

4. **Help & Documentation**
   - Visit "Help & Docs" for comprehensive user guide
   - Try real-world fraud investigation examples
   - Learn about system features and best practices

### Form Validation

All required fields must be completed:
- ✅ Transaction Amount
- ✅ Customer/Company Name  
- ✅ Transaction Description
- ✅ Destination Country

## 🎨 Theme & Styling

The application uses a professional dark blue theme:

- **Primary Colors**: Deep blues for trust and authority
- **High Contrast**: Excellent readability and accessibility
- **Responsive**: Adapts to all screen sizes
- **Modern UI**: Clean, professional interface

## 🔌 API Integration

The frontend connects to these backend endpoints:

### **Core Investigation Endpoints**
- `GET /health` - System health check
- `POST /investigate` - Start fraud investigation  
- `POST /investigate/stream` - Stream investigation progress
- `GET /search` - Vector search regulatory documents

### **External Intelligence Endpoints**
- `GET /exchange-rate` - Currency exchange rates
- `GET /web-search` - Web intelligence search via Tavily
- `GET /arxiv-search` - Academic fraud research search

### **Cache Management Endpoints**
- `GET /cache/stats` - Cache performance metrics
- `DELETE /cache/clear` - Clear all cache
- `DELETE /cache/clear/investigations` - Clear investigation cache  
- `DELETE /cache/clear/external` - Clear external API cache

## 📱 Pages & Components

### Pages
- `/` - Main investigation interface
- `/tools` - Additional tools and search features

### Key Components
- `Header` - Application branding and navigation
- `HealthStatus` - Real-time API status monitoring
- `InvestigationForm` - Transaction input form
- `InvestigationResults` - Results display and analysis
- `DocumentSearch` - Regulatory document search
- `ExchangeRate` - Currency rate lookup

## 🔧 Development Commands

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Linting
npm run lint
```

## 📦 Build & Deployment

### Local Production Build
```bash
npm run build
npm start
```

### Vercel Deployment
1. Connect your repository to Vercel
2. Set environment variables if needed
3. Deploy with automatic builds

## 🌐 Environment Configuration

The frontend is configured to connect to the API at `http://localhost:8000` by default. For production deployment, update the API endpoints in the components to point to your production API URL.

## 🎯 Performance

- **Fast Loading**: Optimized Next.js build
- **Code Splitting**: Automatic component splitting
- **Image Optimization**: Next.js Image component
- **CSS Optimization**: Tailwind CSS purging

## 🔍 Features Overview

### Investigation Form
- Comprehensive transaction details input
- Real-time form validation
- Loading states during processing
- Currency selection with major currencies

### Results Display
- Visual progress indicators
- Color-coded decision outcomes
- Detailed transaction breakdown
- Agent completion tracking

### Additional Tools
- Regulatory document search with filters
- Multi-currency exchange rate lookup
- Real-time API status monitoring
- Responsive navigation

## 📞 Support

For technical support or questions about the frontend:
- Check the API is running on port 8000
- Verify all required fields are filled
- Monitor the health status indicator
- Check browser developer console for errors

## 🔄 Updates

The application automatically reloads during development. For production updates, rebuild and redeploy the application.

## 🎬 Demo Guide

For comprehensive demo instructions and real-world fraud scenarios, see the **[`DEMO_GUIDE.md`](../DEMO_GUIDE.md)** in the project root.

The demo guide includes:
- 5 real-world fraud investigation scenarios
- Step-by-step 5-minute demo script  
- Technical demonstration points
- Expected performance metrics
- Troubleshooting guide

---

# 📚 Implementation Playbook

**Version:** 1.0  
**Last Updated:** January 31, 2025  
**Technology Stack:** Next.js 15, TypeScript, Tailwind CSS

## 📖 Development Overview

### Goal
Build a professional, accessible frontend for the InvestigatorAI Multi-Agent Fraud Investigation System that provides:
- Intuitive fraud investigation workflow
- Real-time API status monitoring
- Additional investigation tools
- Professional dark blue theme
- Responsive design

### Requirements Met
- ✅ Dark blue theme with high contrast
- ✅ Password-style inputs for sensitive data
- ✅ Next.js with Vercel deployment compatibility
- ✅ Local testing capability
- ✅ Pleasant UX with proper content fitting
- ✅ Well-documented codebase

## 🚀 Implementation Steps

### Step 1: Project Initialization
```bash
# Created Next.js project with optimal configuration
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias="@/*" \
  --no-turbopack
```

**Rationale:** 
- TypeScript for type safety
- Tailwind for utility-first styling  
- App Router for modern Next.js features
- src directory for clean organization
- Import aliases for clean imports

### Step 2: Project Structure
```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   ├── tools/
│   │   │   └── page.tsx        # Tools page
│   │   └── globals.css         # Global styles
│   └── components/
│       ├── Header.tsx          # App header
│       ├── HealthStatus.tsx    # API status
│       ├── InvestigationForm.tsx
│       ├── InvestigationResults.tsx
│       ├── DocumentSearch.tsx
│       └── ExchangeRate.tsx
├── package.json
└── README.md
```

**Key Decisions:**
- App Router over Pages Router for better performance
- Component-based architecture for reusability
- Separate tools page for auxiliary features

## 🎨 Theme Implementation

### Step 3: CSS Variables System

**File:** `src/app/globals.css`

```css
:root {
  /* Light theme with dark blue accents */
  --background: #ffffff;
  --foreground: #1e293b;
  --primary: #1e40af;
  --primary-foreground: #ffffff;
  --secondary: #f1f5f9;
  --border: #e2e8f0;
  /* ... additional variables */
}

@media (prefers-color-scheme: dark) {
  :root {
    /* Dark blue theme */
    --background: #0f172a;
    --foreground: #f1f5f9;
    --primary: #3b82f6;
    /* ... dark theme variables */
  }
}
```

**Implementation Strategy:**
1. **CSS Custom Properties** - Enable dynamic theming
2. **Semantic Naming** - Clear variable purposes
3. **Contrast Optimization** - Ensure accessibility
4. **Media Query Support** - Respect user preferences

### Step 4: Component Styling Classes

```css
.btn-primary {
  background: var(--primary);
  color: var(--primary-foreground);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}
```

**Benefits:**
- Consistent button styling across components
- Smooth hover animations
- Professional visual feedback

## 🧩 Component Architecture

### Step 5: Header Component

**File:** `src/components/Header.tsx`

```typescript
'use client';

export default function Header() {
  return (
    <header className="bg-primary text-primary-foreground shadow-lg">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">InvestigatorAI</h1>
            <p className="text-sm opacity-90">Multi-Agent Fraud Investigation System</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-sm opacity-90">Powered by</div>
              <div className="font-semibold">OpenAI & LangChain</div>
            </div>
            
            <div className="w-12 h-12 bg-primary-foreground/20 rounded-full flex items-center justify-center">
              {/* SVG Icon */}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
```

**Design Principles:**
- **Clear Branding** - Prominent logo and tagline
- **Technology Credits** - Show AI capabilities
- **Visual Balance** - Logo left, info right
- **Responsive Layout** - Works on all screen sizes

### Step 6: Investigation Form Component

**File:** `src/components/InvestigationForm.tsx`

```typescript
interface InvestigationFormProps {
  onSubmit: (formData: any) => void;
  isLoading: boolean;
}

export default function InvestigationForm({ onSubmit, isLoading }: InvestigationFormProps) {
  const [formData, setFormData] = useState({
    amount: '',
    currency: 'USD',
    description: '',
    customer_name: '',
    account_type: 'Business',
    risk_rating: 'Medium',
    country_to: ''
  });
  // ... form logic
}
```

**Form Features:**
- **Controlled Components** - React state management
- **Input Validation** - Required field checking
- **Loading States** - Disabled form during submission
- **User Feedback** - Clear validation messages
- **Responsive Grid** - Adaptive layout

## 🔌 API Integration

### Step 7: API Endpoint Integration

**Endpoints Implemented:**

1. **Health Check** - `GET /health`
   ```typescript
   const response = await fetch('http://localhost:8000/health');
   const data = await response.json();
   ```

2. **Investigation** - `POST /investigate`
   ```typescript
   const investigationData = {
     amount: 75000,
     currency: "USD", 
     description: "International wire transfer",
     customer_name: "John Doe",
     account_type: "Personal",
     risk_rating: "High",
     country_to: "Romania"
   };
   
   const response = await fetch('http://localhost:8000/investigate', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify(investigationData),
   });
   
   const result = await response.json();
   // Returns: { investigation_id, status, final_decision, agents_completed, full_results }
   ```

3. **Document Search** - `GET /search`
   ```typescript
   const response = await fetch(
     `http://localhost:8000/search?query=${encodeURIComponent('AML compliance requirements')}&max_results=5`
   );
   
   const results = await response.json();
   // Returns: [{ content, metadata, score, source }]
   ```

4. **Exchange Rate** - `GET /exchange-rate`
   ```typescript
   const response = await fetch(
     `http://localhost:8000/exchange-rate?from_currency=USD&to_currency=EUR`
   );
   
   const data = await response.json();
   // Returns: { result: "USD to EUR: 0.85", source: "exchangerate-api.com" }
   ```

5. **Investigation Streaming** - `POST /investigate/stream`
   ```typescript
   const response = await fetch('http://localhost:8000/investigate/stream', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify(investigationData),
   });
   
   const reader = response.body?.getReader();
   // Stream real-time investigation progress updates
   ```

6. **Web Intelligence** - `GET /web-search`
   ```typescript
   const response = await fetch(
     `http://localhost:8000/web-search?query=${encodeURIComponent('Romania financial regulations')}&max_results=3`
   );
   
   const intelligence = await response.json();
   // Returns: { result: "Current intelligence summary", source: "tavily" }
   ```

7. **Cache Statistics** - `GET /cache/stats`
   ```typescript
   const response = await fetch('http://localhost:8000/cache/stats');
   const stats = await response.json();
   // Returns: { cache: { hit_rate, total_calls, cache_size }, timestamp, endpoints }
   ```

**Error Handling Strategy:**
```typescript
try {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  const result = await response.json();
  // Handle success
} catch (error) {
  console.error('API call failed:', error);
  setError('User-friendly error message');
}
```

## ✅ Testing & Validation

### Step 8: Manual Testing Checklist

**Form Validation:**
- ✅ Required fields prevent submission
- ✅ Number input accepts decimal values
- ✅ Dropdown selections work correctly
- ✅ Textarea handles multi-line input
- ✅ Loading states disable form during submission

**API Integration:**
- ✅ Health status updates every 30 seconds
- ✅ Investigation form submits successfully
- ✅ Results display correctly formatted
- ✅ Search functionality returns results
- ✅ Exchange rate lookup works
- ✅ Error handling displays user-friendly messages

**Responsive Design:**
- ✅ Mobile layout stacks components vertically
- ✅ Desktop layout uses grid system
- ✅ Touch targets are appropriately sized
- ✅ Text remains readable at all sizes

**Accessibility:**
- ✅ High contrast ratios throughout
- ✅ Keyboard navigation works
- ✅ Screen reader friendly markup
- ✅ Proper heading hierarchy

## 📈 Development Timeline

### Phase 1: Foundation (Day 1)
- ✅ Next.js project setup
- ✅ TypeScript configuration
- ✅ Tailwind CSS integration
- ✅ Project structure planning

### Phase 2: Design System (Day 1)
- ✅ CSS variable system
- ✅ Dark blue theme implementation
- ✅ Component styling classes
- ✅ Responsive design foundation

### Phase 3: Core Components (Day 1)
- ✅ Header component
- ✅ Health status monitoring
- ✅ Investigation form
- ✅ Results display component

### Phase 4: Feature Enhancement (Day 1)
- ✅ Document search tool
- ✅ Exchange rate lookup
- ✅ Navigation system
- ✅ Tools page creation

### Phase 5: Integration & Testing (Day 1)
- ✅ API integration
- ✅ Error handling
- ✅ Form validation
- ✅ Manual testing

### Phase 6: Documentation (Day 1)
- ✅ README creation
- ✅ Implementation playbook
- ✅ Development instructions
- ✅ Deployment preparation

## 💡 Lessons Learned

### What Worked Well

1. **CSS Variables Approach**
   - Enabled consistent theming
   - Easy dark/light mode support
   - Simplified maintenance

2. **Component-First Development**
   - Reusable, modular code
   - Clear separation of concerns
   - Easy testing and debugging

3. **TypeScript Integration**
   - Caught errors early
   - Better IDE support
   - Self-documenting interfaces

4. **Next.js App Router**
   - Modern development experience
   - Excellent performance
   - Simple routing system

### Challenges Overcome

1. **Theme Implementation**
   - **Challenge:** Balancing dark blue theme with accessibility
   - **Solution:** Careful contrast ratio testing and CSS variable system

2. **API Integration**
   - **Challenge:** Handling various API response formats
   - **Solution:** Consistent error handling patterns and TypeScript interfaces

3. **Form Validation**
   - **Challenge:** Complex form state management
   - **Solution:** Controlled components with clear validation feedback

4. **Responsive Design**
   - **Challenge:** Complex layouts on different screen sizes
   - **Solution:** CSS Grid and Flexbox with Tailwind utilities

### Best Practices Established

1. **File Organization**
   ```
   - Components in /components directory
   - Pages in /app directory with clear naming
   - Shared styles in globals.css
   - README and documentation at project root
   ```

2. **Component Structure**
   ```typescript
   // 1. Imports
   // 2. Interface definitions
   // 3. Component function
   // 4. State management
   // 5. Event handlers
   // 6. Render logic
   ```

3. **Error Handling**
   ```typescript
   // Consistent try-catch blocks
   // User-friendly error messages
   // Console logging for debugging
   // Loading state management
   ```

4. **Styling Approach**
   ```
   - CSS variables for theming
   - Tailwind for utilities
   - Custom classes for reusable patterns
   - Component-scoped styles when needed
   ```

## 🔄 Future Enhancements

### Short Term (Next Sprint)
- [ ] Add loading skeletons for better UX
- [ ] Implement toast notifications
- [ ] Add keyboard shortcuts
- [ ] Enhanced mobile touch interactions

### Medium Term (Next Month)
- [ ] User authentication system
- [ ] Investigation history
- [ ] Data export functionality
- [ ] Advanced search filters

### Long Term (Next Quarter)
- [ ] Real-time investigation updates
- [ ] Dashboard analytics
- [ ] Multi-language support
- [ ] Progressive Web App features

## 📚 Technical Reference

### Key Dependencies
```json
{
  "next": "15.4.5",
  "react": "^19.0.0",
  "typescript": "^5.0.0",
  "tailwindcss": "^4.0.0"
}
```

### API Endpoints Used
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | System status and configuration |
| `/investigate` | POST | Start fraud investigation |
| `/investigate/stream` | POST | Stream investigation progress |
| `/search` | GET | Vector search regulatory documents |
| `/exchange-rate` | GET | Currency exchange rates |
| `/web-search` | GET | Web intelligence via Tavily |
| `/arxiv-search` | GET | Academic fraud research |
| `/cache/stats` | GET | Cache performance metrics |
| `/cache/clear` | DELETE | Clear all cache |
| `/cache/clear/investigations` | DELETE | Clear investigation cache |
| `/cache/clear/external` | DELETE | Clear external API cache |

---

**Implementation Playbook Last Updated:** January 31, 2025  
*This document is maintained as development progresses and new features are added.*