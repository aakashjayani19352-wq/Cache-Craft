# Cache-Craft: Next.js 15 Presentation Tier

[![Next.js 15](https://img.shields.io/badge/Next.js-15.0-black.svg?style=flat&logo=next.js&logoColor=white)](https://nextjs.org/)
[![React 19](https://img.shields.io/badge/React-19.0-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![Tailwind CSS v4](https://img.shields.io/badge/Tailwind-v4.0-38B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Deployed on Vercel](https://img.shields.io/badge/Vercel-Deployed-000000.svg?style=flat&logo=vercel&logoColor=white)](https://vercel.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

The official presentation tier for **Cache-Craft** — an autonomous semantic RAG router and multi-tier caching middleware. Built on the Next.js 15 App Router, React 19, and Tailwind CSS v4, this interface features a refined **Cupertino Dark / Glassmorphism** design system with live Server-Sent Events (SSE) telemetry and granular cache management.

---

## 🖥️ Application Pages

### 1. Analytics Overview (`/dashboard/overview`)
- **Real-Time KPIs**: Live monitoring of Total Queries Routed, Global Hit Rate (%), Estimated Cost Savings (%), and Average Cache Latency (ms vs. cold LLM path).
- **Multi-Tier Latency Visualizer**: Microsecond-accurate latency comparisons between L1 Redis (<2ms), L2 pgvector (~20ms), and L3 LLM Cloud Inference (~1,500ms - 3,000ms).
- **Cluster Health Status**: Active heartbeat indicators for Redis, PostgreSQL pgvector, and LLM inference endpoints.

### 2. Chat Playground (`/dashboard/chat`)
- **Conversational Turn-Context Binder**: Eliminates semantic drift by dynamically binding prior turns (`<prior_turn> -> <follow_up>`) into compound embeddings.
- **Cache Hit / Miss Badge Indicators**: Every response displays its provenance (`L1 Exact Redis`, `L2 Semantic pgvector`, or `L3 Gemini Cloud / Ollama Local`), similarity score, and retrieval latency.
- **Mid-Session Controls**: Switch between Cloud API mode and Local GPU Offline mode mid-conversation.

### 3. Cache Explorer (`/dashboard/cache`)
- **Dual-Tier Cache Inspector**: Browse, search, and paginate through entries cached across Redis and PostgreSQL.
- **SHA-256 Digest Search**: Search cache records by query content or SHA-256 hash.
- **Granular Eviction**: Flush individual cache records or trigger an atomic cluster-wide purge.

### 4. Settings & System Controls (`/dashboard/settings`)
- **Dynamic Similarity Threshold Slider**: Adjust the cosine distance cutoff in real time (0.50 – 0.99) without restarting the backend daemon.
- **TTL Preset Lifecycle Manager**: Configure coordinated cache expiration (1 Hour, 6 Hours, 24 Hours, 7 Days, 30 Days, or Permanent).
- **Hardware Authorization Gateway**: Creator hardware fingerprint validation for local GPU model allocation.

---

## 🛠️ Technology Stack

- **Framework**: Next.js 15.0 (App Router)
- **UI Primitives**: Base UI & Radix UI
- **Styling**: Tailwind CSS v4 with custom Cupertino dark/glass tokens
- **Icons**: Tabler Icons & Lucide React
- **Animations**: Framer Motion
- **State & Data Fetching**: TanStack React Query, Nuqs (URL search param sync), Server-Sent Events (SSE)
- **Notifications**: Sonner

---

## ⚙️ Environment Configuration

Create a `.env.local` file in the `frontend` directory:

```env
# Cache-Craft Backend API URL
# In local development: defaults to http://localhost:8000
# In production on Vercel: set to your Railway backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Disable Sentry error logging during development
NEXT_PUBLIC_SENTRY_DISABLED=true
```

> **Smart LAN Resolution**: When running locally or across a local network (`192.168.x.x`), `src/lib/api.ts` automatically resolves the backend on port 8000 of the requesting host without requiring manual `.env` changes.

---

## 🚀 Getting Started

### Local Development

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

### Production Build

```bash
npm run build
npm run start
```

---

## ☁️ Deployment on Vercel

1. Push your repository to GitHub.
2. In the [Vercel Dashboard](https://vercel.com/new), import the repository.
3. Configure the project settings:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Next.js`
4. Add the Environment Variable:
   - `NEXT_PUBLIC_API_URL`: Your Railway backend production URL (e.g., `https://cache-craft-production.up.railway.app`)
5. Click **Deploy**.

---

## 📄 License

This frontend is open-source under the [MIT License](../LICENSE).
