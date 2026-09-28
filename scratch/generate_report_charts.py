"""
generate_report_charts.py
Renders the 3 missing academic report charts for Cache-Craft:
1. Figure 4.3: Cache-Craft System Block Diagram and Component Interaction
2. Figure 4.4: Cache-Craft Consolidated UML Diagram (Use Case, Class, Component, Sequence, Activity)
3. Figure 4.5: Cache-Craft End-to-End Process Flow Diagram

Renders to ultra-crisp 2x retina PNG images in reports_assets/ using Playwright and Google Chrome.
"""

import os
import sys
from playwright.sync_api import sync_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ASSETS_DIR = r"c:\Projects\Cache-Craft\reports_assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

# ==============================================================================
# HTML 1: Block Diagram (Figure 4.3)
# ==============================================================================
HTML_BLOCK_DIAGRAM = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: #ffffff;
    color: #1e293b;
    padding: 30px;
    width: 1400px;
    margin: 0 auto;
  }

  .watermark {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 160px;
    font-weight: 900;
    color: rgba(148, 163, 184, 0.05);
    letter-spacing: 20px;
    pointer-events: none;
    z-index: 0;
  }

  .header {
    text-align: center;
    margin-bottom: 25px;
    position: relative;
    z-index: 1;
  }
  .header h1 {
    font-size: 26px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.5px;
  }
  .header h2 {
    font-size: 16px;
    font-weight: 600;
    color: #475569;
    margin-top: 4px;
  }

  .badge-a-plus {
    position: absolute;
    right: 20px;
    top: 0;
    background: linear-gradient(135deg, #fef2f2, #fee2e2);
    border: 2px solid #ef4444;
    border-radius: 12px;
    padding: 8px 16px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
  }
  .badge-a-plus .grade { font-size: 22px; font-weight: 900; color: #dc2626; line-height: 1; }
  .badge-a-plus .sub { font-size: 10px; font-weight: 700; color: #991b1b; text-transform: uppercase; }

  .diagram-container {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  /* Top 3 Columns: Frontend, API Middleware, LLM Providers */
  .top-grid {
    display: grid;
    grid-template-columns: 360px 50px 520px 50px 360px;
    align-items: center;
  }

  .card {
    background: #ffffff;
    border-radius: 14px;
    padding: 16px 20px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
    border: 2px solid #e2e8f0;
    position: relative;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #f1f5f9;
  }
  .card-num {
    background: #0f172a;
    color: #fff;
    font-size: 12px;
    font-weight: 800;
    width: 22px;
    height: 22px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .card-title {
    font-size: 14px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.2px;
  }
  .card-subtitle {
    font-size: 11px;
    color: #64748b;
    font-weight: 500;
    margin-left: auto;
  }

  /* Card 1: Frontend */
  .card-frontend {
    background: #f8fbff;
    border-color: #93c5fd;
  }
  .card-frontend .card-header { border-bottom-color: #bfdbfe; }
  .card-frontend .card-num { background: #2563eb; }
  .card-frontend ul { list-style: none; display: flex; flex-direction: column; gap: 7px; }
  .card-frontend li {
    font-size: 12px;
    font-weight: 600;
    color: #1e3a8a;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .card-frontend li::before {
    content: "•";
    color: #3b82f6;
    font-size: 16px;
    font-weight: 900;
  }

  /* Connectors */
  .connector {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: 4px;
  }
  .connector-arrow {
    width: 100%;
    height: 2px;
    background: #64748b;
    position: relative;
  }
  .connector-arrow::after {
    content: "";
    position: absolute;
    right: 0;
    top: -4px;
    border: 5px solid transparent;
    border-left: 7px solid #64748b;
  }
  .connector-arrow.bi::before {
    content: "";
    position: absolute;
    left: 0;
    top: -4px;
    border: 5px solid transparent;
    border-right: 7px solid #64748b;
  }
  .connector-label {
    font-size: 10px;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    background: #fff;
    padding: 2px 4px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
  }

  /* Card 2: Middleware API */
  .card-middleware {
    background: #fffcf8;
    border-color: #fdba74;
  }
  .card-middleware .card-header { border-bottom-color: #fed7aa; }
  .card-middleware .card-num { background: #ea580c; }
  .middleware-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .sub-pill {
    background: #ffffff;
    border: 1.5px solid #fed7aa;
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 11px;
    font-weight: 600;
    color: #9a3412;
    display: flex;
    flex-direction: column;
    gap: 2px;
    box-shadow: 0 1px 3px rgba(234, 88, 12, 0.05);
  }
  .sub-pill span {
    font-size: 9.5px;
    font-weight: 500;
    color: #c2410c;
    font-family: Consolas, monospace;
  }

  /* Card 3: LLM Providers */
  .card-llm {
    background: #fff9f9;
    border-color: #fca5a5;
  }
  .card-llm .card-header { border-bottom-color: #fecaca; }
  .card-llm .card-num { background: #dc2626; }
  .llm-box {
    background: #ffffff;
    border: 1.5px solid #fecaca;
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .llm-icon {
    font-size: 20px;
  }
  .llm-info h4 { font-size: 12px; font-weight: 700; color: #991b1b; }
  .llm-info p { font-size: 10px; color: #7f1d1d; font-family: Consolas, monospace; }

  /* Middle Row: Decision Engine & Database Layer */
  .mid-grid {
    display: grid;
    grid-template-columns: 620px 40px 700px;
    align-items: stretch;
  }

  /* Card 4: Routing Decision */
  .card-routing {
    background: #f0fdf4;
    border-color: #86efac;
  }
  .card-routing .card-header { border-bottom-color: #bbf7d0; }
  .card-routing .card-num { background: #16a34a; }
  .route-badges {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .badge-item {
    background: #ffffff;
    border: 1.5px solid #bbf7d0;
    border-radius: 8px;
    padding: 8px 10px;
  }
  .badge-title { font-size: 11.5px; font-weight: 700; color: #166534; display: flex; align-items: center; justify-content: space-between; }
  .badge-desc { font-size: 10px; color: #15803d; margin-top: 2px; }
  .badge-tag {
    font-size: 9px;
    font-weight: 800;
    padding: 1px 6px;
    border-radius: 4px;
    text-transform: uppercase;
  }
  .tag-green { background: #dcfce7; color: #15803d; }
  .tag-blue { background: #dbeafe; color: #1d4ed8; }
  .tag-red { background: #fee2e2; color: #b91c1c; }

  /* Card 5: Multi-Tier Storage */
  .card-db {
    background: #f0fdfa;
    border-color: #5eead4;
  }
  .card-db .card-header { border-bottom-color: #99f6e4; }
  .card-db .card-num { background: #0d9488; }
  .db-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .db-column {
    background: #ffffff;
    border: 1.5px solid #99f6e4;
    border-radius: 10px;
    padding: 12px;
  }
  .db-name {
    font-size: 12px;
    font-weight: 800;
    color: #115e59;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 6px;
    padding-bottom: 4px;
    border-bottom: 1px solid #ccfbf1;
  }
  .db-column ul { list-style: none; display: flex; flex-direction: column; gap: 5px; }
  .db-column li {
    font-size: 10.5px;
    color: #134e4a;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .db-column li::before {
    content: "▸";
    color: #0d9488;
    font-size: 12px;
  }

  /* Bottom Row: Deployment & Benchmarking */
  .bottom-grid {
    display: grid;
    grid-template-columns: 660px 40px 660px;
    align-items: stretch;
  }

  .card-deploy {
    background: #fefce8;
    border-color: #fde047;
  }
  .card-deploy .card-header { border-bottom-color: #fef08a; }
  .card-deploy .card-num { background: #ca8a04; }
  .deploy-list {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  .deploy-item {
    background: #ffffff;
    border: 1.5px solid #fef08a;
    border-radius: 8px;
    padding: 8px 12px;
  }
  .deploy-item h5 { font-size: 11.5px; font-weight: 700; color: #854d0e; }
  .deploy-item p { font-size: 10px; color: #a16207; margin-top: 2px; }

  .card-bench {
    background: #faf5ff;
    border-color: #d8b4fe;
  }
  .card-bench .card-header { border-bottom-color: #e9d5ff; }
  .card-bench .card-num { background: #9333ea; }
  .bench-list {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  .bench-item {
    background: #ffffff;
    border: 1.5px solid #e9d5ff;
    border-radius: 8px;
    padding: 8px 12px;
  }
  .bench-item h5 { font-size: 11.5px; font-weight: 700; color: #6b21a8; }
  .bench-item p { font-size: 10px; color: #7e22ce; margin-top: 2px; }

  .caption {
    text-align: center;
    margin-top: 20px;
    font-size: 14px;
    font-weight: 700;
    color: #1e293b;
    letter-spacing: -0.2px;
  }
</style>
</head>
<body>

  <div class="watermark">CACHE-CRAFT</div>

  <div class="header">
    <h1>Block Diagram</h1>
    <h2>Cache-Craft – Autonomous Semantic RAG Router & Multi-Tier Caching Middleware</h2>
  </div>

  <div class="diagram-container">
    
    <!-- TOP ROW: Frontend -> API Middleware -> LLM Providers -->
    <div class="top-grid">
      
      <!-- Card 1: Frontend -->
      <div class="card card-frontend">
        <div class="card-header">
          <div class="card-num">1</div>
          <div class="card-title">User / Client (Frontend)</div>
          <div class="card-subtitle">Next.js 15 + React</div>
        </div>
        <ul>
          <li>Interactive Chat Playground & Live Q&A</li>
          <li>Real-Time Analytics & Cost Dashboard</li>
          <li>Dynamic Similarity Slider (0.70 – 0.95)</li>
          <li>Dual-Tier TTL Controls (1h to 30d)</li>
          <li>Active LLM Switcher (Gemini vs. Ollama)</li>
          <li>Vector Cache Explorer (pgvector Inspector)</li>
          <li>On-Demand Cache Vacuum / Purge</li>
          <li>Live SSE Performance Metrics Stream</li>
        </ul>
      </div>

      <!-- Connector 1 -->
      <div class="connector">
        <div class="connector-label">HTTP / REST<br>& SSE</div>
        <div class="connector-arrow bi"></div>
      </div>

      <!-- Card 2: Middleware API -->
      <div class="card card-middleware">
        <div class="card-header">
          <div class="card-num">2</div>
          <div class="card-title">API & Application Middleware Layer</div>
          <div class="card-subtitle">FastAPI (Python 3.11)</div>
        </div>
        <div class="middleware-grid">
          <div class="sub-pill">
            <strong>API Router Core</strong>
            <span>/api/chat, /api/cache, /api/metrics</span>
          </div>
          <div class="sub-pill">
            <strong>L1 Exact Hash Engine</strong>
            <span>SHA-256 Pre-filtering (&lt;2ms)</span>
          </div>
          <div class="sub-pill">
            <strong>Dense Vector Embedder</strong>
            <span>all-MiniLM-L6-v2 (384-dim)</span>
          </div>
          <div class="sub-pill">
            <strong>Context Turn Binder</strong>
            <span>Referential Follow-Up Routing</span>
          </div>
          <div class="sub-pill">
            <strong>Cosine Similarity Scorer</strong>
            <span>HNSW Vector Distance Evaluator</span>
          </div>
          <div class="sub-pill">
            <strong>Resilient Failover Manager</strong>
            <span>Cloud-to-Local Dynamic Reroute</span>
          </div>
          <div class="sub-pill">
            <strong>Dual-Tier TTL Engine</strong>
            <span>Redis EX + PostgreSQL Vacuum</span>
          </div>
          <div class="sub-pill">
            <strong>SSE Stream Dispatcher</strong>
            <span>Real-time Telemetry Push</span>
          </div>
        </div>
      </div>

      <!-- Connector 2 -->
      <div class="connector">
        <div class="connector-label">PROMPTS /<br>COMPLETIONS</div>
        <div class="connector-arrow bi"></div>
      </div>

      <!-- Card 3: LLM Providers -->
      <div class="card card-llm">
        <div class="card-header">
          <div class="card-num">3</div>
          <div class="card-title">LLM Provider Layer</div>
          <div class="card-subtitle">Cloud & Local</div>
        </div>
        <div class="llm-box">
          <div class="llm-icon">☁️</div>
          <div class="llm-info">
            <h4>Google Gemini Cloud API</h4>
            <p>gemini-3.8-flash (High Throughput)</p>
          </div>
        </div>
        <div class="llm-box">
          <div class="llm-icon">💻</div>
          <div class="llm-info">
            <h4>Local Ollama Daemon</h4>
            <p>llama3.2:3b (Offline Zero-Cost)</p>
          </div>
        </div>
        <div class="llm-box" style="margin-bottom:0; background: #fff0f0; border-color: #f87171;">
          <div class="llm-icon">⚡</div>
          <div class="llm-info">
            <h4>Resilient Auto-Failover</h4>
            <p>Reroutes HTTP 503 / Quota Limits</p>
          </div>
        </div>
      </div>

    </div>

    <!-- MIDDLE ROW: Decision Engine & Database Layer -->
    <div class="mid-grid">
      
      <!-- Card 4: Routing Decision -->
      <div class="card card-routing">
        <div class="card-header">
          <div class="card-num">4</div>
          <div class="card-title">Cache Hit / Routing Decision Categories</div>
          <div class="card-subtitle">Zero-Leakage Multi-Tier Routing</div>
        </div>
        <div class="route-badges">
          <div class="badge-item">
            <div class="badge-title">L1 Exact Hit <span class="badge-tag tag-green">&lt; 2ms</span></div>
            <div class="badge-desc">Exact SHA-256 match from Redis in-memory key-value cache.</div>
          </div>
          <div class="badge-item">
            <div class="badge-title">L2 Semantic Hit <span class="badge-tag tag-blue">~ 25ms</span></div>
            <div class="badge-desc">Cosine similarity &ge; Threshold via pgvector HNSW ANN scan.</div>
          </div>
          <div class="badge-item">
            <div class="badge-title">Cache Miss <span class="badge-tag tag-red">~ 1200ms</span></div>
            <div class="badge-desc">Novel semantic intent dispatched to cloud/local LLM engine.</div>
          </div>
          <div class="badge-item">
            <div class="badge-title">Context Turn Hit <span class="badge-tag tag-green">Follow-Up</span></div>
            <div class="badge-desc">Partition-filtered lookup preserving conversational context.</div>
          </div>
        </div>
      </div>

      <!-- Connector 3 -->
      <div class="connector">
        <div class="connector-label">CACHE SYNC</div>
        <div class="connector-arrow bi"></div>
      </div>

      <!-- Card 5: Database Layer -->
      <div class="card card-db">
        <div class="card-header">
          <div class="card-num">5</div>
          <div class="card-title">Multi-Tier Database & Cache Layer</div>
          <div class="card-subtitle">In-Memory + Persistent Storage</div>
        </div>
        <div class="db-grid">
          <div class="db-column">
            <div class="db-name">⚡ Redis 7 (L1 In-Memory)</div>
            <ul>
              <li>Sub-2ms exact match query resolution</li>
              <li>SHA-256 deterministic key indexing</li>
              <li>Coordinated native TTL expiration (EX)</li>
              <li>Lightweight in-memory LRU eviction</li>
            </ul>
          </div>
          <div class="db-column">
            <div class="db-name">🐘 PostgreSQL 16 + pgvector (L2)</div>
            <ul>
              <li>384-dimensional dense vector embeddings</li>
              <li>HNSW Graph Index (m=16, ef_construction=64)</li>
              <li>Partition filtering for multi-turn chats</li>
              <li>Persistent query, metadata, & cost logs</li>
            </ul>
          </div>
        </div>
      </div>

    </div>

    <!-- BOTTOM ROW: Deployment & Benchmarking -->
    <div class="bottom-grid">
      
      <!-- Card 6: Deployment -->
      <div class="card card-deploy">
        <div class="card-header">
          <div class="card-num">6</div>
          <div class="card-title">Containerized Deployment & Runtime</div>
          <div class="card-subtitle">Microservices Architecture</div>
        </div>
        <div class="deploy-list">
          <div class="deploy-item">
            <h5>Docker Compose Multi-Service</h5>
            <p>Frontend (Next.js), Backend (FastAPI), Redis 7, & PostgreSQL 16</p>
          </div>
          <div class="deploy-item">
            <h5>PyTorch SIMD Vector Engine</h5>
            <p>Accelerated CPU/GPU tensor calculations for dense embeddings</p>
          </div>
          <div class="deploy-item">
            <h5>Isolated Docker Network</h5>
            <p>Zero external exposure of vector databases and cache ports</p>
          </div>
          <div class="deploy-item">
            <h5>Healthchecks & Volume Persistence</h5>
            <p>Automatic service restart with persistent pgvector storage</p>
          </div>
        </div>
      </div>

      <!-- Connector 4 -->
      <div class="connector">
        <div class="connector-label">EVAL METRICS</div>
        <div class="connector-arrow bi"></div>
      </div>

      <!-- Card 7: Benchmarking -->
      <div class="card card-bench">
        <div class="card-header">
          <div class="card-num">7</div>
          <div class="card-title">Continuous Benchmarking & Analytics Layer</div>
          <div class="card-subtitle">Empirical Validation Suite</div>
        </div>
        <div class="bench-list">
          <div class="bench-item">
            <h5>1,200-Query Benchmark Suite</h5>
            <p>500 seeds, 500 paraphrases, 200 out-of-domain evaluation corpus</p>
          </div>
          <div class="bench-item">
            <h5>Multi-Threshold Sensitivity Sweeps</h5>
            <p>Profiles precision, recall, and F1 across 0.70 to 0.95 boundaries</p>
          </div>
          <div class="bench-item">
            <h5>Latency & Speedup Analysis</h5>
            <p>Empirical 3.2x overall speedup and 98.9% latency reduction on hits</p>
          </div>
          <div class="bench-item">
            <h5>Token Cost Savings Calculator</h5>
            <p>Real-time calculation of avoided LLM inference expenditures</p>
          </div>
        </div>
      </div>

    </div>

  </div>

  <div class="caption">
    Figure 4.3. Cache-Craft System Block Diagram and Component Interaction
  </div>

</body>
</html>
"""

# ==============================================================================
# HTML 2: UML Diagram (Figure 4.4)
# ==============================================================================
HTML_UML_DIAGRAM = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: #ffffff;
    color: #1e293b;
    padding: 24px 30px;
    width: 1400px;
    margin: 0 auto;
  }

  /* Academic Banner */
  .academic-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 20px;
    background: #f8fafc;
    border: 1.5px solid #cbd5e1;
    border-radius: 10px;
    margin-bottom: 20px;
  }
  .banner-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .logo-badge {
    background: linear-gradient(135deg, #f43f5e, #e11d48);
    color: #fff;
    font-weight: 900;
    font-size: 18px;
    padding: 6px 14px;
    border-radius: 8px;
    letter-spacing: 1px;
  }
  .univ-title h3 {
    font-size: 16px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.3px;
  }
  .univ-title p {
    font-size: 11px;
    font-weight: 600;
    color: #64748b;
    letter-spacing: 0.5px;
  }
  .banner-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .naac-tag {
    background: #fef2f2;
    border: 1.5px solid #ef4444;
    color: #dc2626;
    font-size: 11px;
    font-weight: 800;
    padding: 4px 10px;
    border-radius: 6px;
  }
  .dept-tag {
    background: #f0fdf4;
    border: 1.5px solid #22c55e;
    color: #15803d;
    font-size: 13px;
    font-weight: 800;
    padding: 6px 14px;
    border-radius: 6px;
  }

  .main-title {
    text-align: center;
    margin-bottom: 20px;
  }
  .main-title h1 {
    font-size: 24px;
    font-weight: 900;
    color: #0f172a;
    letter-spacing: -0.5px;
  }

  /* Grid Layout: 2 Columns */
  .uml-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }

  .panel {
    border-radius: 12px;
    border: 2px solid #cbd5e1;
    background: #ffffff;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
    display: flex;
    flex-direction: column;
  }
  .panel-header {
    background: #0f172a;
    color: #ffffff;
    text-align: center;
    padding: 8px 12px;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }

  /* 1. USE CASE DIAGRAM */
  .use-case-content {
    padding: 16px;
    display: flex;
    align-items: center;
    background: #f8fafc;
    flex: 1;
    gap: 20px;
  }
  .actor-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 80px;
  }
  .stick-man {
    width: 40px;
    height: 60px;
  }
  .actor-label {
    font-size: 11px;
    font-weight: 700;
    color: #334155;
    text-align: center;
    margin-top: 4px;
  }
  .uc-system {
    flex: 1;
    border: 2px dashed #94a3b8;
    border-radius: 10px;
    padding: 12px;
    background: #ffffff;
    position: relative;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .uc-title {
    position: absolute;
    top: -10px;
    right: 14px;
    background: #ffffff;
    padding: 0 8px;
    font-size: 10px;
    font-weight: 800;
    color: #64748b;
    text-transform: uppercase;
  }
  .uc-oval {
    border: 1.5px solid #3b82f6;
    background: #eff6ff;
    color: #1e40af;
    border-radius: 20px;
    padding: 6px 10px;
    font-size: 10.5px;
    font-weight: 600;
    text-align: center;
    box-shadow: 0 1px 3px rgba(59, 130, 246, 0.1);
  }

  /* 2. CLASS DIAGRAM */
  .class-content {
    padding: 14px;
    background: #fdfefe;
    flex: 1;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .uml-class {
    border: 1.5px solid #0284c7;
    border-radius: 6px;
    background: #ffffff;
    overflow: hidden;
    font-family: Consolas, monospace;
    font-size: 9.5px;
  }
  .class-head {
    background: #e0f2fe;
    color: #0369a1;
    font-weight: 800;
    text-align: center;
    padding: 4px 6px;
    border-bottom: 1.5px solid #0284c7;
  }
  .class-attrs {
    padding: 6px;
    border-bottom: 1px solid #e2e8f0;
    color: #334155;
    line-height: 1.4;
  }
  .class-methods {
    padding: 6px;
    color: #0f172a;
    line-height: 1.4;
  }

  /* 3. COMPONENT DIAGRAM */
  .comp-content {
    padding: 16px;
    background: #fafaf9;
    flex: 1;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }
  .uml-comp {
    border: 1.5px solid #d97706;
    background: #fffbeb;
    border-radius: 8px;
    padding: 10px;
    position: relative;
    box-shadow: 0 2px 4px rgba(217, 119, 6, 0.08);
  }
  .comp-tag {
    font-size: 8.5px;
    font-weight: 800;
    color: #b45309;
    text-transform: uppercase;
  }
  .comp-name {
    font-size: 11px;
    font-weight: 800;
    color: #78350f;
    margin-top: 2px;
  }
  .comp-tech {
    font-size: 9.5px;
    color: #92400e;
    margin-top: 4px;
    font-family: Consolas, monospace;
  }

  /* 4. SEQUENCE DIAGRAM */
  .seq-content {
    padding: 16px;
    background: #fdf4ff;
    flex: 1;
  }
  .lifelines {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    text-align: center;
    margin-bottom: 12px;
  }
  .ll-box {
    background: #ffffff;
    border: 1.5px solid #a855f7;
    color: #6b21a8;
    font-size: 10.5px;
    font-weight: 700;
    padding: 6px 4px;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(168, 85, 247, 0.1);
  }
  .seq-steps {
    display: flex;
    flex-direction: column;
    gap: 8px;
    font-size: 10px;
    font-weight: 600;
  }
  .seq-msg {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #ffffff;
    border: 1px solid #e9d5ff;
    border-radius: 6px;
    padding: 5px 10px;
    color: #581c87;
  }
  .seq-num {
    background: #9333ea;
    color: #ffffff;
    font-size: 9px;
    font-weight: 800;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* 5. ACTIVITY DIAGRAM */
  .act-content {
    padding: 14px;
    background: #f0fdf4;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .act-flow {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
  }
  .act-node {
    background: #ffffff;
    border: 1.5px solid #16a34a;
    color: #14532d;
    padding: 6px 8px;
    border-radius: 6px;
    font-size: 9.5px;
    font-weight: 700;
    text-align: center;
    flex: 1;
    box-shadow: 0 1px 3px rgba(22, 163, 74, 0.08);
  }
  .act-decision {
    background: #fef08a;
    border: 1.5px solid #ca8a04;
    color: #854d0e;
    transform: rotate(0deg);
    padding: 5px;
    border-radius: 6px;
    font-size: 9px;
    font-weight: 800;
    text-align: center;
    width: 90px;
  }
  .act-arrow {
    color: #15803d;
    font-weight: 900;
    font-size: 14px;
  }

  .caption {
    text-align: center;
    margin-top: 20px;
    font-size: 14px;
    font-weight: 700;
    color: #1e293b;
    letter-spacing: -0.2px;
  }
</style>
</head>
<body>

  <div class="main-title" style="margin-top: 10px; margin-bottom: 25px;">
    <h1>Cache-Craft – Unified UML Architectural Blueprint</h1>
    <h2 style="font-size: 15px; font-weight: 600; color: #475569; margin-top: 6px;">Comprehensive Structural & Behavioral System Models</h2>
  </div>

  <div class="uml-grid">
    
    <!-- 1. USE CASE DIAGRAM -->
    <div class="panel">
      <div class="panel-header" style="background:#1e40af;">Use Case Diagram</div>
      <div class="use-case-content">
        <div class="actor-box">
          <svg class="stick-man" viewBox="0 0 24 48">
            <circle cx="12" cy="8" r="6" fill="none" stroke="#0f172a" stroke-width="2"/>
            <line x1="12" y1="14" x2="12" y2="30" stroke="#0f172a" stroke-width="2"/>
            <line x1="2" y1="20" x2="22" y2="20" stroke="#0f172a" stroke-width="2"/>
            <line x1="12" y1="30" x2="4" y2="46" stroke="#0f172a" stroke-width="2"/>
            <line x1="12" y1="30" x2="20" y2="46" stroke="#0f172a" stroke-width="2"/>
          </svg>
          <div class="actor-label">User / Client Developer</div>
        </div>
        <div class="uc-system">
          <div class="uc-title">Cache-Craft Boundary</div>
          <div class="uc-oval">Enter Natural Query</div>
          <div class="uc-oval">L1 Exact Hash Match</div>
          <div class="uc-oval">L2 Semantic HNSW Search</div>
          <div class="uc-oval">Multi-Turn Context Query</div>
          <div class="uc-oval">Route to Gemini/Ollama</div>
          <div class="uc-oval">Adjust Dynamic Threshold</div>
          <div class="uc-oval">Configure Dual-Tier TTL</div>
          <div class="uc-oval">Inspect Vector Cache DB</div>
          <div class="uc-oval" style="grid-column: span 2;">View Real-Time SSE Metrics &amp; Token Savings</div>
        </div>
      </div>
    </div>

    <!-- 2. CLASS DIAGRAM -->
    <div class="panel">
      <div class="panel-header" style="background:#0369a1;">Class Diagram</div>
      <div class="class-content">
        
        <div class="uml-class">
          <div class="class-head">QueryRequest</div>
          <div class="class-attrs">
            + query: str<br>
            + session_id: str<br>
            + threshold: float = 0.85<br>
            + model: str = "gemini"
          </div>
          <div class="class-methods">
            + validate(): bool<br>
            + get_normalized(): str
          </div>
        </div>

        <div class="uml-class">
          <div class="class-head">CacheResponse</div>
          <div class="class-attrs">
            + response: str<br>
            + cache_hit: bool<br>
            + tier_hit: str (L1/L2/MISS)<br>
            + similarity: float<br>
            + latency_ms: float
          </div>
          <div class="class-methods">
            + to_dict(): dict<br>
            + get_token_savings(): int
          </div>
        </div>

        <div class="uml-class">
          <div class="class-head">RedisL1Cache</div>
          <div class="class-attrs">
            - client: Redis<br>
            - default_ttl: int = 86400
          </div>
          <div class="class-methods">
            + get_exact(hash: str): str<br>
            + set_exact(h, resp, ttl)<br>
            + flush_cache(): bool
          </div>
        </div>

        <div class="uml-class">
          <div class="class-head">PgVectorL2Store</div>
          <div class="class-attrs">
            - pool: ConnectionPool<br>
            - dim: int = 384
          </div>
          <div class="class-methods">
            + search_hnsw(vec, thr): list<br>
            + insert_entry(q, vec, r, ttl)<br>
            + vacuum_expired(): int
          </div>
        </div>

      </div>
    </div>

    <!-- 3. COMPONENT DIAGRAM -->
    <div class="panel" style="grid-column: span 2;">
      <div class="panel-header" style="background:#b45309;">Component Diagram</div>
      <div class="comp-content">
        <div class="uml-comp">
          <div class="comp-tag">&laquo;component&raquo; Presentation</div>
          <div class="comp-name">Next.js 15 Client</div>
          <div class="comp-tech">React 19, Tailwind CSS, SSE Client</div>
        </div>
        <div class="uml-comp">
          <div class="comp-tag">&laquo;component&raquo; Core Middleware</div>
          <div class="comp-name">FastAPI REST Router</div>
          <div class="comp-tech">Pydantic v2, AsyncIO, SSE Hub</div>
        </div>
        <div class="uml-comp">
          <div class="comp-tag">&laquo;component&raquo; Embedding Worker</div>
          <div class="comp-name">SentenceTransformer</div>
          <div class="comp-tech">all-MiniLM-L6-v2 (384-dim Torch)</div>
        </div>
        <div class="uml-comp">
          <div class="comp-tag">&laquo;component&raquo; In-Memory Tier</div>
          <div class="comp-name">Redis 7 L1 Cache</div>
          <div class="comp-tech">SHA-256 Exact Store, Sub-2ms</div>
        </div>
        <div class="uml-comp">
          <div class="comp-tag">&laquo;component&raquo; Vector Storage</div>
          <div class="comp-name">PostgreSQL 16 + pgvector</div>
          <div class="comp-tech">HNSW Index (m=16, ef=64)</div>
        </div>
        <div class="uml-comp">
          <div class="comp-tag">&laquo;component&raquo; Inference Gateway</div>
          <div class="comp-name">Dual LLM Engine</div>
          <div class="comp-tech">Google Gemini API + Local Ollama</div>
        </div>
      </div>
    </div>

    <!-- 4. SEQUENCE DIAGRAM -->
    <div class="panel">
      <div class="panel-header" style="background:#6b21a8;">Sequence Diagram</div>
      <div class="seq-content">
        <div class="lifelines">
          <div class="ll-box">User</div>
          <div class="ll-box">Next.js UI</div>
          <div class="ll-box">FastAPI</div>
          <div class="ll-box">Redis L1</div>
          <div class="ll-box">pgvector L2</div>
        </div>
        <div class="seq-steps">
          <div class="seq-msg">
            <div class="seq-num">1</div>
            <span>User submits prompt to Next.js Chat Playground</span>
          </div>
          <div class="seq-msg">
            <div class="seq-num">2</div>
            <span>Frontend dispatches HTTP POST /api/chat</span>
          </div>
          <div class="seq-msg">
            <div class="seq-num">3</div>
            <span>FastAPI calculates SHA-256 hash &amp; checks Redis L1</span>
          </div>
          <div class="seq-msg" style="background:#ecfdf5; border-color:#6ee7b7;">
            <div class="seq-num" style="background:#059669;">4</div>
            <span>[Alt 1: Exact Hit] Redis returns cached response (&lt;2ms)</span>
          </div>
          <div class="seq-msg">
            <div class="seq-num">5</div>
            <span>[Else: Miss] PyTorch generates 384-dim dense embedding</span>
          </div>
          <div class="seq-msg" style="background:#eff6ff; border-color:#93c5fd;">
            <div class="seq-num" style="background:#2563eb;">6</div>
            <span>[Alt 2: Semantic Hit] pgvector HNSW matches (cos &ge; thr, ~25ms)</span>
          </div>
          <div class="seq-msg" style="background:#fff1f2; border-color:#fecdd3;">
            <div class="seq-num" style="background:#e11d48;">7</div>
            <span>[Else: Miss] Fallback LLM generation &rarr; persist to L2 &amp; L1</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 5. ACTIVITY DIAGRAM -->
    <div class="panel">
      <div class="panel-header" style="background:#15803d;">Activity Diagram</div>
      <div class="act-content">
        <div class="act-flow">
          <div class="act-node" style="background:#0f172a; color:#fff; border-color:#0f172a; border-radius:50px; flex:0.4;">Start</div>
          <div class="act-arrow">&rarr;</div>
          <div class="act-node">User Enters Query</div>
          <div class="act-arrow">&rarr;</div>
          <div class="act-node">SHA-256 Hash</div>
          <div class="act-arrow">&rarr;</div>
          <div class="act-decision">L1 Hit?</div>
        </div>
        <div class="act-flow">
          <div class="act-node" style="background:#ecfdf5;">[Yes] Return Redis Response (&lt;2ms)</div>
          <div class="act-arrow">&larr;</div>
          <div class="act-node" style="background:#fef2f2;">[No] Generate 384-dim Embedding</div>
          <div class="act-arrow">&rarr;</div>
          <div class="act-node">HNSW Search</div>
        </div>
        <div class="act-flow">
          <div class="act-decision">Cos &ge; Thr?</div>
          <div class="act-arrow">&rarr;</div>
          <div class="act-node" style="background:#eff6ff;">[Yes] L2 Semantic Hit (~25ms) &rarr; Warm L1</div>
          <div class="act-arrow">&rarr;</div>
          <div class="act-node" style="background:#fef2f2;">[No] Dispatch to Gemini Cloud</div>
        </div>
        <div class="act-flow">
          <div class="act-decision">API Spikes?</div>
          <div class="act-arrow">&rarr;</div>
          <div class="act-node" style="background:#fff7ed;">[Failover] Reroute to Local Ollama</div>
          <div class="act-arrow">&rarr;</div>
          <div class="act-node">Persist DB &amp; L1</div>
          <div class="act-arrow">&rarr;</div>
          <div class="act-node" style="background:#0f172a; color:#fff; border-color:#0f172a; border-radius:50px; flex:0.4;">End</div>
        </div>
      </div>
    </div>

  </div>

  <div class="caption">
    Figure 4.4. Cache-Craft Consolidated UML Architectural Blueprints
  </div>

</body>
</html>
"""

# ==============================================================================
# HTML 3: Process Flow Diagram (Figure 4.5)
# ==============================================================================
HTML_PROCESS_FLOW = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: #ffffff;
    color: #1e293b;
    padding: 24px 30px;
    width: 1400px;
    margin: 0 auto;
  }

  /* Academic Banner */
  .academic-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 20px;
    background: #f8fafc;
    border: 1.5px solid #cbd5e1;
    border-radius: 10px;
    margin-bottom: 20px;
  }
  .banner-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .logo-badge {
    background: linear-gradient(135deg, #f43f5e, #e11d48);
    color: #fff;
    font-weight: 900;
    font-size: 18px;
    padding: 6px 14px;
    border-radius: 8px;
    letter-spacing: 1px;
  }
  .univ-title h3 {
    font-size: 16px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.3px;
  }
  .univ-title p {
    font-size: 11px;
    font-weight: 600;
    color: #64748b;
    letter-spacing: 0.5px;
  }
  .banner-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .naac-tag {
    background: #fef2f2;
    border: 1.5px solid #ef4444;
    color: #dc2626;
    font-size: 11px;
    font-weight: 800;
    padding: 4px 10px;
    border-radius: 6px;
  }
  .dept-tag {
    background: #f0fdf4;
    border: 1.5px solid #22c55e;
    color: #15803d;
    font-size: 13px;
    font-weight: 800;
    padding: 6px 14px;
    border-radius: 6px;
  }

  .main-title {
    text-align: center;
    margin-bottom: 24px;
  }
  .main-title h1 {
    font-size: 24px;
    font-weight: 900;
    color: #0f172a;
    letter-spacing: -0.5px;
  }

  /* 11-Step Process Grid: 4 columns x 3 rows */
  .process-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    position: relative;
  }

  .step-card {
    border-radius: 12px;
    border: 2px solid #e2e8f0;
    background: #ffffff;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .step-head {
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1.5px solid #e2e8f0;
  }
  .step-icon {
    font-size: 18px;
  }
  .step-num-title {
    font-size: 12.5px;
    font-weight: 800;
    letter-spacing: -0.2px;
  }
  .step-body {
    padding: 12px 14px;
    font-size: 11px;
    color: #334155;
    line-height: 1.5;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .step-pill {
    background: #f1f5f9;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 9.5px;
    font-weight: 700;
    font-family: Consolas, monospace;
    display: inline-block;
    align-self: flex-start;
  }

  /* Color Themes for Steps */
  .c-blue { border-color: #93c5fd; }
  .c-blue .step-head { background: #eff6ff; color: #1e40af; border-color: #bfdbfe; }
  .c-blue .step-pill { background: #dbeafe; color: #1e40af; }

  .c-amber { border-color: #fcd34d; }
  .c-amber .step-head { background: #fffbeb; color: #92400e; border-color: #fde68a; }
  .c-amber .step-pill { background: #fef3c7; color: #92400e; }

  .c-emerald { border-color: #6ee7b7; }
  .c-emerald .step-head { background: #ecfdf5; color: #065f46; border-color: #a7f3d0; }
  .c-emerald .step-pill { background: #d1fae5; color: #065f46; }

  .c-purple { border-color: #d8b4fe; }
  .c-purple .step-head { background: #faf5ff; color: #6b21a8; border-color: #e9d5ff; }
  .c-purple .step-pill { background: #f3e8ff; color: #6b21a8; }

  .c-rose { border-color: #fda4af; }
  .c-rose .step-head { background: #fff1f2; color: #9f1239; border-color: #fecdd3; }
  .c-rose .step-pill { background: #ffe4e6; color: #9f1239; }

  .c-indigo { border-color: #a5b4fc; }
  .c-indigo .step-head { background: #eef2ff; color: #3730a3; border-color: #c7d2fe; }
  .c-indigo .step-pill { background: #e0e7ff; color: #3730a3; }

  .c-teal { border-color: #5eead4; }
  .c-teal .step-head { background: #f0fdfa; color: #115e59; border-color: #99f6e4; }
  .c-teal .step-pill { background: #ccfbf1; color: #115e59; }

  .c-slate { border-color: #cbd5e1; }
  .c-slate .step-head { background: #f8fafc; color: #0f172a; border-color: #e2e8f0; }
  .c-slate .step-pill { background: #f1f5f9; color: #0f172a; }

  .caption {
    text-align: center;
    margin-top: 24px;
    font-size: 14px;
    font-weight: 700;
    color: #1e293b;
    letter-spacing: -0.2px;
  }
</style>
</head>
<body>

  <div class="main-title" style="margin-top: 10px; margin-bottom: 25px;">
    <h1>Process Flow Diagram</h1>
    <h2 style="font-size: 15px; font-weight: 600; color: #475569; margin-top: 6px;">Cache-Craft End-to-End Query Execution & Multi-Tier Routing Pipeline</h2>
  </div>

  <div class="process-grid">
    
    <!-- Step 1 -->
    <div class="step-card c-blue">
      <div class="step-head">
        <div class="step-icon">👤</div>
        <div class="step-num-title">1. User Query Access</div>
      </div>
      <div class="step-body">
        <p>User submits natural language query via Next.js 15 Chat Playground or direct REST API.</p>
        <p>Loads dynamic cosine similarity threshold (default: 0.85) and active LLM configuration.</p>
        <div class="step-pill">POST /api/chat</div>
      </div>
    </div>

    <!-- Step 2 -->
    <div class="step-card c-amber">
      <div class="step-head">
        <div class="step-icon">🔒</div>
        <div class="step-num-title">2. SHA-256 Hashing</div>
      </div>
      <div class="step-body">
        <p>Strips redundant whitespaces, converts text to lowercase, and normalizes formatting.</p>
        <p>Computes deterministic 64-character SHA-256 cryptographic digest key for L1 indexing.</p>
        <div class="step-pill">hashlib.sha256(q)</div>
      </div>
    </div>

    <!-- Step 3 -->
    <div class="step-card c-emerald">
      <div class="step-head">
        <div class="step-icon">⚡</div>
        <div class="step-num-title">3. L1 Redis Lookup</div>
      </div>
      <div class="step-body">
        <p>Performs instant O(1) in-memory key-value check against Redis 7.</p>
        <p>If key exists: Serves instant Exact Match in <strong>&lt; 2ms</strong> with zero GPU/CPU vector compute overhead.</p>
        <div class="step-pill">redis.get(exact_key)</div>
      </div>
    </div>

    <!-- Step 4 -->
    <div class="step-card c-purple">
      <div class="step-head">
        <div class="step-icon">🧠</div>
        <div class="step-num-title">4. Dense Vectorization</div>
      </div>
      <div class="step-body">
        <p>On L1 cache miss: Dispatches raw query to PyTorch SentenceTransformer model.</p>
        <p>Generates a 384-dimensional unit L2-normalized float embedding in ~15ms.</p>
        <div class="step-pill">all-MiniLM-L6-v2</div>
      </div>
    </div>

    <!-- Step 5 -->
    <div class="step-card c-indigo">
      <div class="step-head">
        <div class="step-icon">🔗</div>
        <div class="step-num-title">5. Multi-Turn Binder</div>
      </div>
      <div class="step-body">
        <p>Referential intent classifier checks for follow-up phrasing ('summarize', 'why', 'details').</p>
        <p>Binds conversation history with pgvector partition filtering to prevent semantic drift.</p>
        <div class="step-pill">WHERE query LIKE '% -> %'</div>
      </div>
    </div>

    <!-- Step 6 -->
    <div class="step-card c-teal">
      <div class="step-head">
        <div class="step-icon">🔍</div>
        <div class="step-num-title">6. pgvector HNSW Search</div>
      </div>
      <div class="step-body">
        <p>Executes Approximate Nearest Neighbor (ANN) search in PostgreSQL 16.</p>
        <p>Traverses HNSW graph index (m=16, ef=64) to find closest semantic neighbor in ~10ms.</p>
        <div class="step-pill">1 - (emb &lt;=&gt; stored_emb)</div>
      </div>
    </div>

    <!-- Step 7 -->
    <div class="step-card c-amber">
      <div class="step-head">
        <div class="step-icon">⚖️</div>
        <div class="step-num-title">7. Threshold Gate</div>
      </div>
      <div class="step-body">
        <p>Evaluates cosine similarity score against active user threshold (e.g., 0.85).</p>
        <p>Branches execution: Score &ge; Threshold &rarr; L2 Semantic Hit. Score &lt; Threshold &rarr; Cache Miss.</p>
        <div class="step-pill">score &ge; 0.85 ? HIT : MISS</div>
      </div>
    </div>

    <!-- Step 8 -->
    <div class="step-card c-emerald">
      <div class="step-head">
        <div class="step-icon">🎯</div>
        <div class="step-num-title">8. L2 Semantic Hit</div>
      </div>
      <div class="step-body">
        <p>Retrieves cached response from PostgreSQL in <strong>~25ms</strong>. Bypasses LLM entirely.</p>
        <p>Asynchronously sets key in Redis 7 (L1 cache warming) with active TTL policy.</p>
        <div class="step-pill">100% Token Cost Saved</div>
      </div>
    </div>

    <!-- Step 9 -->
    <div class="step-card c-rose">
      <div class="step-head">
        <div class="step-icon">☁️</div>
        <div class="step-num-title">9. Cloud LLM Inference</div>
      </div>
      <div class="step-body">
        <p>On cache miss: Dispatches query to Google Gemini 3.8 Flash Cloud API (~1200ms).</p>
        <p>Tracks input and output token consumption for live cost analytics and audit logging.</p>
        <div class="step-pill">gemini-3.8-flash</div>
      </div>
    </div>

    <!-- Step 10 -->
    <div class="step-card c-amber">
      <div class="step-head">
        <div class="step-icon">🛡️</div>
        <div class="step-num-title">10. Resilient Fallback</div>
      </div>
      <div class="step-body">
        <p>If Gemini returns HTTP 503 or quota limits, failover handler catches error instantly.</p>
        <p>Reroutes query to local Ollama Llama 3.2 daemon with 100% availability guarantee.</p>
        <div class="step-pill">ollama/llama3.2:3b</div>
      </div>
    </div>

    <!-- Step 11 -->
    <div class="step-card c-teal">
      <div class="step-head">
        <div class="step-icon">💾</div>
        <div class="step-num-title">11. Dual-Tier Persistence</div>
      </div>
      <div class="step-body">
        <p>Saves novel prompt, 384-dim vector, and response into PostgreSQL with expires_at timestamp.</p>
        <p>Sets exact key in Redis with EX TTL. Emits live SSE event to update dashboard analytics.</p>
        <div class="step-pill">SSE Stream &amp; Metrics</div>
      </div>
    </div>

    <!-- Empty 12th Slot: Summary / Status Card -->
    <div class="step-card c-slate">
      <div class="step-head">
        <div class="step-icon">🏁</div>
        <div class="step-num-title">End-to-End Resolution</div>
      </div>
      <div class="step-body">
        <p>Formatted Markdown answer delivered to Next.js UI with latency &amp; hit indicators.</p>
        <p>System maintains full audit history, cache efficiency statistics, and ROI metrics.</p>
        <div class="step-pill">Latency: &lt;2ms / 25ms / 1200ms</div>
      </div>
    </div>

  </div>

  <div class="caption">
    Figure 4.5. Cache-Craft End-to-End Process Flow Diagram
  </div>

</body>
</html>
"""

def render_chart(browser, html_content, output_name, viewport_height=1000):
    page = browser.new_page(
        viewport={"width": 1460, "height": viewport_height},
        device_scale_factor=2  # Crisp 2x retina rendering
    )
    page.set_content(html_content, wait_until="load")
    page.wait_for_timeout(300)
    
    out_path = os.path.join(ASSETS_DIR, output_name)
    page.screenshot(path=out_path, full_page=True)
    print(f"Rendered: {out_path} ({os.path.getsize(out_path)} bytes)", flush=True)
    page.close()

def main():
    print("Starting Playwright with Chrome...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
        
        # 1. Figure 4.3: Block Diagram
        render_chart(browser, HTML_BLOCK_DIAGRAM, "figure_4_3_block_diagram.png", viewport_height=1100)
        render_chart(browser, HTML_BLOCK_DIAGRAM, "block_diagram.png", viewport_height=1100)
        
        # 2. Figure 4.4: UML Diagram
        render_chart(browser, HTML_UML_DIAGRAM, "figure_4_4_uml_diagram.png", viewport_height=1250)
        render_chart(browser, HTML_UML_DIAGRAM, "uml_diagram.png", viewport_height=1250)
        
        # 3. Figure 4.5: Process Flow Diagram
        render_chart(browser, HTML_PROCESS_FLOW, "figure_4_5_process_flow_diagram.png", viewport_height=1100)
        render_chart(browser, HTML_PROCESS_FLOW, "process_flow_diagram.png", viewport_height=1100)
        
        browser.close()
        print("All 3 charts successfully generated!", flush=True)

if __name__ == "__main__":
    main()
