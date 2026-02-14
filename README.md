# MW-VISION

**Visual Command Center for Multi-Agent AI Development**

[![Status](https://img.shields.io/badge/Status-MVP%20Complete-success)](http://localhost:5189)
[![Framework](https://img.shields.io/badge/Framework-React%2018.3.1-61dafb)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-Latest-646cff)](https://vitejs.dev/)

---

## 🎯 Overview

MW-Vision is the **Visual Command Center** for orchestrating AI agent crews in multi-agent development environments. Built with React + TypeScript + Vite, it provides real-time visualization, cost tracking, and natural language control over autonomous development crews.

### Key Features

- ✅ **Toast Notification System** - Real-time feedback (success, error, warning, info)
- ✅ **Zustand State Management** - Global state for agents, costs, and crews
- ✅ **WebSocket Live Updates** - Simulated real-time agent status updates
- ✅ **Cost Preview with Warnings** - Pre-execution cost estimation (killer feature)
- ✅ **React Flow Visual Canvas** - Interactive node-based agent workflow
- ✅ **GitHub Import Simulation** - Clone + analyze + classify code
- ✅ **Hydra Protocol v2 Mock** - Code obfuscation for proprietary files
- ✅ **MindWareHouse UI** - Glassmorphism with custom color palette

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or pnpm

### Installation

```bash
cd mw-vision-app
npm install
```

### Development

```bash
npm run dev
```

**Application runs on:** http://localhost:5189

---

## 📂 Project Structure

```
MW-Vision/
├── README.md
├── .gitignore
├── MW-VISION-EXECUTIVE-SUMMARY.md (21KB - Market analysis, TAM/SAM, pricing)
├── MW-VISION-VISION-MISSION.md (15KB - Vision, mission, personas)
├── MW-VISION-TECHNICAL-SPECIFICATION.md (>100KB - Complete architecture)
└── mw-vision-app/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── main.tsx (Entry point + ToastProvider)
        ├── App.tsx (Main app with tabs + WebSocket init)
        ├── index.css (MindWareHouse styles + glassmorphism)
        ├── components/
        │   ├── Toast.tsx (Notification system)
        │   └── FlowCanvas.tsx (React Flow integration)
        ├── views/
        │   ├── FlowView.tsx (Visual workflow + cost preview)
        │   ├── TeamView.tsx (KPIs + agent cards)
        │   ├── ChatView.tsx (Natural language interface)
        │   └── BlueprintView.tsx (GitHub import + Hydra)
        ├── stores/
        │   └── crewStore.ts (Zustand global state)
        └── services/
            └── websocketService.ts (Live updates simulation)
```

---

## 🎨 UI Design

### MindWareHouse Color Palette

- **Cyan**: `#00d4ff` - Primary actions, highlights
- **Purple**: `#9d4edd` - Hydra Protocol, secondary
- **Green**: `#00ff88` - Success, active states
- **Orange**: `#ff9900` - Warnings, pause actions
- **Red**: `#ff3366` - Errors, critical alerts
- **Background**: `#0a0e27` - Dark base

### Typography

- **Headers**: Orbitron (sci-fi, futuristic)
- **Code**: JetBrains Mono (monospace)
- **Body**: Inter (clean, readable)

### Glassmorphism

- `.glass-panel` - Main containers with backdrop blur
- `.glass-card` - Nested content cards
- Hover glow effects on buttons
- Animated pulse on status indicators

---

## 📊 Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | React 18.3.1 |
| **Language** | TypeScript |
| **Build Tool** | Vite |
| **State Management** | Zustand 4.5.2 |
| **Styling** | Tailwind CSS |
| **Visual Workflow** | @xyflow/react 12.3.5 |
| **Icons** | Lucide React |

---

## 🧩 Core Components

### 1. Flow View

Visual canvas with React Flow for agent orchestration:
- Drag & drop agent nodes
- Animated connections between agents
- Real-time status updates (running/paused/idle/error)
- MiniMap for navigation
- Interactive controls

### 2. Team View

Dashboard with KPIs and agent monitoring:
- Active Agents count
- Total Tasks processed
- Total Cost accumulated
- Average Response Time
- Individual agent cards with pause/details buttons

### 3. Chat View

Natural language command interface:
- Send commands like "Launch debugging crew on main.py"
- Quick Commands (Bug Hunter, Run Tests, Code Review, Pause All)
- Message history with user/system/agent messages
- Enter key support

### 4. Blueprint View

Code import and security:
- GitHub repository import with URL validation
- Automatic code classification (proprietary vs public)
- Hydra Protocol v2 protection for sensitive files
- File statistics and protection status

---

## 💰 Cost Preview System

**Killer Feature:** Pre-execution cost estimation

### How It Works

1. **Model-Based Calculation**
   - Claude 3.5 Sonnet: $0.015 per 1K tokens
   - DeepSeek Chat: $0.002 per 1K tokens
   - GPT-4o: $0.03 per 1K tokens

2. **Budget Warning**
   - Default budget: $10.00
   - Visual warning (red) when estimated cost exceeds budget
   - Toast notification before crew launch

3. **Real-Time Accumulation**
   - Cost updates every 3 seconds (WebSocket simulation)
   - Total cost displayed in Flow View and Team View

---

## 🔐 Hydra Protocol v2

Code obfuscation system for proprietary files sent to untrusted models:

- **Fragmentation** - Code split into chunks
- **Steganography** - Hidden markers in comments
- **Schema Rotation** - Every ~50 requests
- **Trust Levels** - 0-4 scale determines protection intensity

---

## 🛠️ Development

### Available Scripts

```bash
npm run dev     # Start development server (port 5189)
npm run build   # Build for production
npm run preview # Preview production build
npm run lint    # Lint code
```

### Environment

- Development server: http://localhost:5189
- HMR (Hot Module Reload) enabled
- TypeScript strict mode

---

## 📈 Roadmap

### Phase 1: MVP (✅ COMPLETE)
- [x] Toast notification system
- [x] Zustand state management
- [x] WebSocket live updates (simulated)
- [x] Cost Preview with budget warnings
- [x] React Flow visual canvas
- [x] GitHub import simulation
- [x] Hydra Protocol mock

### Phase 2: Backend Integration
- [ ] Connect to real FastAPI backend
- [ ] Implement real WebSocket connection
- [ ] Integrate CrewAI for actual agent execution
- [ ] Real GitHub API integration
- [ ] Implement Hydra Protocol backend

### Phase 3: Production Features
- [ ] User authentication
- [ ] Database persistence
- [ ] Real-time collaboration
- [ ] Cost limit enforcement
- [ ] Agent performance analytics

### Phase 4: Advanced Features
- [ ] Custom agent creation UI
- [ ] Workflow templates
- [ ] Export/import workflows
- [ ] Integration with VSCode extension

---

## 🤝 Contributing

This is a private MVP project. For questions or suggestions, contact the development team.

---

## 📄 License

Proprietary - All rights reserved.

---

## 🎓 Documentation

- **Executive Summary**: See `MW-VISION-EXECUTIVE-SUMMARY.md`
- **Vision & Mission**: See `MW-VISION-VISION-MISSION.md`
- **Technical Spec**: See `MW-VISION-TECHNICAL-SPECIFICATION.md`

---

**Built with ❤️ by MindWareHouse Team**

*ONE STEP AHEAD*