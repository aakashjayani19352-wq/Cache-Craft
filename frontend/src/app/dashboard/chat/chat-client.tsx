'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { 
  Zap, 
  Database, 
  Server, 
  Copy, 
  Check, 
  Sparkles, 
  ArrowUp, 
  ThumbsUp, 
  ThumbsDown, 
  RotateCcw, 
  Cpu, 
  Globe, 
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { api, getBaseUrl } from '@/lib/api';

const SUPERSCRIPTS: Record<string, string> = {
  '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
  '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
  '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾',
  'n': 'ⁿ', 'i': 'ⁱ', 'x': 'ˣ', 'y': 'ʸ'
};

const SUBSCRIPTS: Record<string, string> = {
  '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
  '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
  '+': '₊', '-': '₋', '=': '₌', '(': '₍', ')': '₎',
  'a': 'ₐ', 'e': 'ₑ', 'h': 'ₕ', 'i': 'ᵢ', 'j': 'ⱼ',
  'k': 'ₖ', 'l': 'ₗ', 'm': 'ₘ', 'n': 'ₙ', 'o': 'ₒ',
  'p': 'ₚ', 'r': 'ᵣ', 's': 'ₛ', 't': 'ₜ', 'u': 'ᵤ',
  'v': 'ᵥ', 'x': 'ₓ', 'y': 'ᵧ', 'z': 'ᵤ'
};

/**
 * Normalizes math/scientific LaTeX expressions into elegant, human-readable Unicode
 * and prepares complex formulas for KaTeX rendering without ugly raw syntax.
 */
function preprocessMathMarkdown(content: string): string {
  if (!content) return '';

  let processed = content;

  // Convert LaTeX bracket delimiters \[ ... \] -> $$ ... $$
  processed = processed.replace(/\\\[([\s\S]*?)\\\]/g, (_, eq) => `\n\n$$\n${eq.trim()}\n$$\n\n`);

  // Convert LaTeX inline delimiters \( ... \) -> $ ... $
  processed = processed.replace(/\\\(([\s\S]*?)\\\)/g, (_, eq) => `$${eq.trim()}$`);

  // Convert definition-style display equations (without complex calculus/matrices) to clean blockquotes
  processed = processed.replace(/\$\$([\s\S]*?)\$\$/g, (match, eq) => {
    if (/\\(frac|sum|int|sqrt|matrix|begin|prod)/.test(eq)) {
      return `\n\n$$\n${eq.trim()}\n$$\n\n`;
    }
    const cleanEq = eq
      .replace(/\\text\{([^}]+)\}/g, '$1')
      .replace(/\\times/g, '×')
      .replace(/\^?\s*\\circ/g, '°')
      .replace(/\\sigma/g, 'σ')
      .replace(/\\pi/g, 'π')
      .replace(/\\\s+/g, ' ')
      .replace(/\\/g, '')
      .trim();
    return `\n\n> **${cleanEq}**\n\n`;
  });

  // Convert inline math to clean typography
  processed = processed.replace(/\$([^$]+?)\$/g, (match, inner) => {
    if (/\\(frac|sum|int|sqrt|matrix|begin|prod)/.test(inner)) {
      return match;
    }
    let s = inner;
    s = s.replace(/\\text\{([^}]+)\}/g, '$1');
    s = s.replace(/\\times/g, '×');
    s = s.replace(/\^?\s*\\circ/g, '°');
    s = s.replace(/\^°/g, '°');
    s = s.replace(/\\sigma/g, 'σ');
    s = s.replace(/\\pi/g, 'π');
    s = s.replace(/\\alpha/g, 'α').replace(/\\beta/g, 'β').replace(/\\gamma/g, 'γ');
    s = s.replace(/\\Delta/g, 'Δ').replace(/\\theta/g, 'θ').replace(/\\mu/g, 'μ');
    s = s.replace(/\\approx/g, '≈').replace(/\\neq/g, '≠').replace(/\\leq?/g, '≤').replace(/\\geq?/g, '≥').replace(/\\pm/g, '±');
    s = s.replace(/\\(?:rightarrow|to)/g, '→').replace(/\\leftarrow/g, '←').replace(/\\cdot/g, '·');
    s = s.replace(/\\\s+/g, ' ');
    // Superscripts
    s = s.replace(/\^\{?([0-9nixy\+\-]+)\}?/g, (_: string, chars: string) =>
      chars.split('').map((c: string) => SUPERSCRIPTS[c] || c).join('')
    );
    // Subscripts
    s = s.replace(/_\{?([0-9a-z\+\-]+)\}?/g, (_: string, chars: string) =>
      chars.split('').map((c: string) => SUBSCRIPTS[c] || c).join('')
    );
    s = s.replace(/\\/g, '').trim();
    return s;
  });

  // Ensure any remaining KaTeX display math has line breaks around it
  processed = processed.replace(/([^\n])\s*\$\$([\s\S]+?)\$\$/g, '$1\n\n$$$2$$');
  processed = processed.replace(/\$\$([\s\S]+?)\$\$\s*([^\n])/g, '$$$1$$\n\n$2');

  return processed;
}

// Cache-Craft's signature Minimalist Titanium Neural Emblem (Subtle, Mature, Sophisticated)
function CacheCraftEmblem({ className = "w-11 h-11" }: { className?: string }) {
  return (
    <div className={`relative flex items-center justify-center shrink-0 ${className}`}>
      <div className="absolute inset-0 rounded-2xl bg-white/[0.04] blur-lg" />
      <div className="relative w-full h-full rounded-2xl bg-[#16161a] border border-white/[0.12] flex items-center justify-center shadow-lg ring-1 ring-white/5 will-change-transform">
        <svg 
          viewBox="0 0 24 24" 
          className="w-5 h-5 text-zinc-100" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          {/* Isometric Multi-Tier Cache Prism */}
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
          <path d="M2 12l10 5 10-5" />
          <circle cx="12" cy="12" r="1.2" fill="currentColor" />
        </svg>
      </div>
    </div>
  );
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  metadata?: {
    latency?: number;
    hit_type?: 'CACHE_HIT_L0' | 'CACHE_HIT_L1' | 'CACHE_HIT_L2' | 'CACHE_MISS';
    source?: string;
    similarity?: number;
    similarity_threshold?: number;
    query_hash?: string;
    feedback?: 'positive' | 'negative' | null;
    offline_mode?: boolean;
    fallback_triggered?: boolean;
    fallback_reason?: string | null;
    note?: string | null;
    routed_model?: string | null;
    router_category?: string | null;
    router_reason?: string | null;
  };
}

const SUGGESTIONS = [
  'What is Cache-Craft and how does it save LLM cost?',
  'Explain the difference between Redis L1 and pgvector L2 cache.',
  'How does dynamic cosine similarity thresholding work?'
];

// Subtle, Minimalist Offline GPU Transition Modal — Real Hardware Lifecycle (Non-Gimmick)
function OfflineTransitionModal({
  isOpen,
  targetModel = 'qwen2.5:7b',
  gpuTelemetry,
  onClose,
  onSuccess
}: {
  isOpen: boolean;
  targetModel?: string;
  gpuTelemetry?: any;
  onClose: () => void;
  onSuccess: (data: any) => void;
}) {
  const [step, setStep] = useState<'alert' | 'loading' | 'ready' | 'error'>('alert');
  const [mounted, setMounted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTask, setCurrentTask] = useState('Initializing pipeline...');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!isOpen) {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      setStep('alert');
      setProgress(0);
      setErrorMessage(null);
    }
  }, [isOpen]);

  const handleStartLoad = () => {
    setStep('loading');
    setProgress(15);
    setCurrentTask('Initializing offline model (Qwen 2.5)...');
    setErrorMessage(null);

    const baseUrl = getBaseUrl();
    const streamUrl = `${baseUrl}/api/models/preload-stream?model=${encodeURIComponent(targetModel)}`;

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    try {
      const es = new EventSource(streamUrl);
      eventSourceRef.current = es;

      es.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (typeof data.progress === 'number') {
            setProgress(data.progress);
          }
          if (data.task) {
            setCurrentTask(data.task.replace(/RTX 4060|CUDA|GPU VRAM|GPU/gi, 'Offline Model'));
          }

          if (data.phase === 'error' || data.error) {
            es.close();
            eventSourceRef.current = null;
            setStep('error');
            setProgress(0);
            setErrorMessage(data.error || 'Failed to initialize offline model');
          } else if (data.phase === 'ready' && data.vram_loaded) {
            es.close();
            eventSourceRef.current = null;
            setProgress(100);
            setStep('ready');
            setCurrentTask('Offline Model Ready · Qwen 2.5 (7B)');
            onSuccess(data);
            setTimeout(() => {
              onClose();
            }, 1400);
          }
        } catch (e) {
          console.error('SSE parse error:', e);
        }
      };

      es.onerror = async () => {
        es.close();
        eventSourceRef.current = null;
        setCurrentTask('Checking offline model readiness...');
        try {
          const res = await api.preloadModel(targetModel);
          if (res.status === 'ready' && res.vram_loaded) {
            setProgress(100);
            setStep('ready');
            setCurrentTask('Offline Model Ready · Qwen 2.5 (7B)');
            onSuccess(res);
            setTimeout(() => {
              onClose();
            }, 1400);
          } else {
            setStep('error');
            setProgress(0);
            setErrorMessage(res.message || 'Offline model initialization failed.');
          }
        } catch (err: any) {
          setStep('error');
          setProgress(0);
          setErrorMessage(err.message || 'Connection to backend failed.');
        }
      };
    } catch (err: any) {
      setStep('error');
      setProgress(0);
      setErrorMessage(err.message || 'Failed to initialize offline model.');
    }
  };

  if (!mounted) return null;

  return createPortal(
    <AnimatePresence>
      {isOpen && (
        <div id="offline-transition-modal" className="fixed inset-0 z-[9999] flex items-center justify-center p-4">
          {/* Deep matte backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => step === 'alert' && onClose()}
            className="absolute inset-0 bg-black/80 backdrop-blur-md"
          />

          {/* Refined Titanium Modal Card */}
          <motion.div
            initial={{ opacity: 0, scale: 0.94, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.94, y: 10 }}
            transition={{ type: 'spring', stiffness: 450, damping: 28 }}
            className="relative w-full max-w-md bg-[#101013] border border-white/[0.12] rounded-3xl p-6 shadow-2xl text-foreground overflow-hidden ring-1 ring-white/5 z-10"
          >
            {step === 'alert' ? (
              /* Step 1: Confirmation Alert Box */
              <div className="space-y-5 text-left relative z-10 select-none">
                <div className="flex items-center gap-3.5">
                  <div className="w-10 h-10 rounded-2xl bg-[#18181c] border border-white/[0.1] flex items-center justify-center text-zinc-100">
                    <Cpu className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-zinc-100 tracking-tight">
                      Switch to Offline Mode?
                    </h3>
                    <p className="text-xs text-zinc-400">
                      Private Local Inference · Zero Cloud Network
                    </p>
                  </div>
                </div>

                {/* Model Telemetry Card */}
                <div className="p-3.5 rounded-2xl bg-[#141417] border border-white/[0.08] space-y-2.5 text-xs">
                  <div className="flex items-center justify-between text-zinc-400">
                    <span>Offline Model:</span>
                    <span className="font-medium text-zinc-200 font-mono">Qwen 2.5 (7B)</span>
                  </div>
                  <div className="flex items-center justify-between text-zinc-400">
                    <span>Inference Type:</span>
                    <span className="font-medium text-zinc-200 font-mono">Local Private Execution</span>
                  </div>
                  <div className="flex items-center justify-between text-zinc-400">
                    <span>Model Status:</span>
                    <span className={`font-mono font-medium ${gpuTelemetry?.is_model_in_vram ? 'text-emerald-400' : 'text-amber-400'}`}>
                      {gpuTelemetry?.is_model_in_vram 
                        ? 'Offline Model Ready ✓'
                        : 'Initialization Required'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-zinc-400">
                    <span>Multi-Tier Cache:</span>
                    <span className="font-medium text-zinc-300">Redis L1 + Vector L2 Active</span>
                  </div>
                </div>

                <p className="text-xs text-zinc-400 leading-relaxed">
                  Confirming will initialize the offline model (Qwen 2.5 7B) locally. The system will verify offline model readiness before proceeding.
                </p>

                {/* Action Buttons */}
                <div className="flex items-center justify-end gap-2.5 pt-2">
                  <button
                    id="cancel-allocate-gpu-btn"
                    type="button"
                    onClick={onClose}
                    className="px-4 py-2 rounded-xl text-xs font-medium text-zinc-400 hover:text-zinc-200 bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] transition-colors"
                  >
                    Cancel
                  </button>
                  <motion.button
                    id="confirm-allocate-gpu-btn"
                    type="button"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={handleStartLoad}
                    className="px-4 py-2 rounded-xl text-xs font-semibold text-zinc-900 bg-zinc-100 hover:bg-white shadow-sm transition-all flex items-center gap-1.5"
                  >
                    <Cpu className="w-3.5 h-3.5 text-zinc-900" />
                    <span>Confirm &amp; Switch to Offline Model →</span>
                  </motion.button>
                </div>
              </div>
            ) : step === 'error' ? (
              /* Step 3: Error View */
              <div className="py-4 text-center space-y-4 relative z-10 select-none">
                <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mx-auto text-amber-400">
                  <AlertCircle className="w-7 h-7" />
                </div>

                <div className="space-y-1.5 px-3">
                  <h4 className="text-sm font-semibold text-zinc-100 tracking-tight">
                    Offline Model Unavailable
                  </h4>
                  <p className="text-xs text-zinc-400 leading-relaxed max-w-sm mx-auto">
                    {errorMessage || 'Could not verify offline model (Qwen 2.5) readiness.'}
                  </p>
                </div>

                <div className="flex items-center justify-center gap-2 pt-2">
                  <button
                    id="close-allocate-gpu-btn"
                    type="button"
                    onClick={onClose}
                    className="px-4 py-2 rounded-xl text-xs font-medium text-zinc-400 hover:text-zinc-200 bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] transition-colors"
                  >
                    Close
                  </button>
                  <button
                    id="retry-allocate-gpu-btn"
                    type="button"
                    onClick={handleStartLoad}
                    className="px-4 py-2 rounded-xl text-xs font-semibold text-zinc-900 bg-zinc-100 hover:bg-white shadow-sm transition-all"
                  >
                    Retry Initialization
                  </button>
                </div>
              </div>
            ) : (
              /* Step 2: Live Progress & Telemetry Loader */
              <div className="py-4 text-center space-y-5 relative z-10 select-none">
                {/* Rotating Rings */}
                <div className="relative w-24 h-24 mx-auto flex items-center justify-center">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                    className="absolute inset-0 rounded-full border border-dashed border-white/20"
                  />
                  <motion.div
                    animate={{ rotate: -360 }}
                    transition={{ duration: 1.8, repeat: Infinity, ease: 'linear' }}
                    className="absolute inset-2 rounded-full border-2 border-t-zinc-100 border-r-transparent border-b-zinc-400 border-l-transparent"
                  />
                  <div className="relative w-12 h-12 rounded-2xl bg-[#18181c] border border-white/10 flex items-center justify-center shadow-md">
                    {step === 'ready' ? (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: 'spring', stiffness: 400, damping: 20 }}
                      >
                        <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                      </motion.div>
                    ) : (
                      <Cpu className="w-6 h-6 text-zinc-200 animate-pulse" />
                    )}
                  </div>
                </div>

                <div className="space-y-1">
                  <h4 className="text-xs font-semibold tracking-wider uppercase text-zinc-300 font-mono">
                    {step === 'ready' ? 'OFFLINE MODEL READY · READY FOR USE' : 'INITIALIZING OFFLINE MODEL'}
                  </h4>
                  <p className="text-xs text-zinc-400 font-mono tracking-wide px-2 min-h-6 flex items-center justify-center">
                    {currentTask}
                  </p>
                </div>

                {/* Model Telemetry Card */}
                <div className="p-3 rounded-2xl bg-[#141417] border border-white/[0.08] space-y-2 text-left text-xs font-mono">
                  <div className="flex items-center justify-between text-zinc-400">
                    <span>Offline Model:</span>
                    <span className="text-zinc-200 font-medium">Qwen 2.5 (7B)</span>
                  </div>
                  <div className="flex items-center justify-between text-zinc-400">
                    <span>Status:</span>
                    <span className={step === 'ready' ? 'text-emerald-400 font-bold' : 'text-amber-400'}>
                      {step === 'ready' ? 'Offline Model Ready ✓' : 'Initializing model weights...'}
                    </span>
                  </div>
                </div>

                {/* Progress Bar with actual percentage */}
                <div className="space-y-1.5 px-2">
                  <div className="w-full h-2 rounded-full bg-white/[0.08] overflow-hidden p-0.5">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${progress}%` }}
                      transition={{ ease: 'easeOut', duration: 0.3 }}
                      className={`h-full rounded-full transition-all ${
                        step === 'ready' ? 'bg-emerald-400' : 'bg-zinc-200'
                      }`}
                    />
                  </div>
                  <div className="flex justify-between text-[11px] text-zinc-400 font-mono">
                    <span>Loading Progress</span>
                    <span className="font-semibold text-zinc-200">{progress}%</span>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>,
    document.body
  );
}

const CHAT_STORAGE_KEY = 'cache_craft_tab_messages';
const OFFLINE_STORAGE_KEY = 'cache_craft_tab_offline';

export default function ChatClient() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [isOffline, setIsOffline] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [gpuAccessAllowed, setGpuAccessAllowed] = useState(true);
  const [gpuTelemetry, setGpuTelemetry] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const fetchGpuTelemetry = useCallback(async () => {
    try {
      const data = await api.getGpuStatus('qwen2.5:7b');
      setGpuTelemetry(data);
    } catch {}
  }, []);

  useEffect(() => {
    fetchGpuTelemetry();
    const interval = setInterval(fetchGpuTelemetry, 6000);
    return () => clearInterval(interval);
  }, [fetchGpuTelemetry]);

  // Restore messages and offline mode from sessionStorage on mount (tab-scoped)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        const savedMessages = sessionStorage.getItem(CHAT_STORAGE_KEY);
        if (savedMessages) {
          const parsed = JSON.parse(savedMessages);
          if (Array.isArray(parsed) && parsed.length > 0) {
            setMessages(parsed);
          }
        }
        const savedOffline = sessionStorage.getItem(OFFLINE_STORAGE_KEY);
        if (savedOffline !== null) {
          setIsOffline(savedOffline === 'true');
        }
      } catch {}
    }
  }, []);

  // Save messages to sessionStorage whenever updated
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        if (messages.length > 0) {
          sessionStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
        } else {
          sessionStorage.removeItem(CHAT_STORAGE_KEY);
        }
      } catch {}
    }
  }, [messages]);

  // Save offline mode to sessionStorage whenever updated
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        sessionStorage.setItem(OFFLINE_STORAGE_KEY, String(isOffline));
      } catch {}
    }
  }, [isOffline]);

  // Automatically unload model weights when the browser tab is closed
  useEffect(() => {
    const handleTabUnload = () => {
      const isTabOffline = sessionStorage.getItem(OFFLINE_STORAGE_KEY) === 'true';
      if (isTabOffline) {
        const baseUrl = getBaseUrl();
        const payload = JSON.stringify({ model: 'qwen2.5:7b' });
        try {
          if (navigator.sendBeacon) {
            const blob = new Blob([payload], { type: 'application/json' });
            navigator.sendBeacon(`${baseUrl}/api/models/unload`, blob);
          } else {
            fetch(`${baseUrl}/api/models/unload`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: payload,
              keepalive: true
            });
          }
        } catch {}
      }
    };

    window.addEventListener('pagehide', handleTabUnload);
    window.addEventListener('beforeunload', handleTabUnload);
    return () => {
      window.removeEventListener('pagehide', handleTabUnload);
      window.removeEventListener('beforeunload', handleTabUnload);
    };
  }, []);

  // Terminal-style Prompt History (ArrowUp to recall last prompt for instant L0/L1 demo)
  const [promptHistory, setPromptHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState<number>(-1);
  const tempInputRef = useRef<string>('');

  useEffect(() => {
    const userPrompts = messages
      .filter((m) => m.role === 'user')
      .map((m) => m.content);
    if (userPrompts.length > 0) {
      setPromptHistory((prev) => {
        const merged = [...prev];
        for (const p of userPrompts) {
          if (!merged.includes(p)) merged.push(p);
        }
        return merged.length > 0 ? merged : userPrompts;
      });
    }
  }, [messages]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && input.trim()) {
        sendQuery(input);
      }
      return;
    }

    if (e.key === 'ArrowUp') {
      const target = e.currentTarget;
      const isAtStart = target.selectionStart === 0 && target.selectionEnd === 0;
      if (isAtStart || input.trim() === '') {
        if (promptHistory.length > 0) {
          e.preventDefault();
          if (historyIndex === -1) {
            tempInputRef.current = input;
            const newIndex = promptHistory.length - 1;
            setHistoryIndex(newIndex);
            setInput(promptHistory[newIndex]);
          } else if (historyIndex > 0) {
            const newIndex = historyIndex - 1;
            setHistoryIndex(newIndex);
            setInput(promptHistory[newIndex]);
          }
        }
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      if (historyIndex !== -1) {
        e.preventDefault();
        if (historyIndex < promptHistory.length - 1) {
          const newIndex = historyIndex + 1;
          setHistoryIndex(newIndex);
          setInput(promptHistory[newIndex]);
        } else {
          setHistoryIndex(-1);
          setInput(tempInputRef.current);
        }
      }
      return;
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    textareaRef.current?.focus();
    let isGuestMode = false;
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      // ONLY simulate guest mode if explicitly requested in URL (e.g. ?guest=1 for Viva demos)
      isGuestMode = urlParams.get('guest') === '1' || urlParams.get('simulate_guest') === 'true';

      if (isGuestMode) {
        setGpuAccessAllowed(false);
      } else {
        setGpuAccessAllowed(true);
      }
    }

    // Check GPU access with backend
    if (isGuestMode) {
      api.getGpuAccess(true)
        .then((res) => {
          setGpuAccessAllowed(res.gpu_access_allowed);
        })
        .catch(() => {
          setGpuAccessAllowed(false);
        });
    } else {
      // Default to allowed for creator!
      setGpuAccessAllowed(true);
      api.getGpuAccess(false)
        .then((res) => {
          if (res && res.gpu_access_allowed !== undefined) {
            setGpuAccessAllowed(res.gpu_access_allowed);
          }
        })
        .catch(() => {
          // Network hiccup? Never lock out creator!
          setGpuAccessAllowed(true);
        });
    }

    api.settings().catch(() => {});
  }, []);

  useEffect(() => {
    if (!isLoading) {
      textareaRef.current?.focus();
    }
  }, [isLoading]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleToggleClick = () => {
    if (!isOffline) {
      if (!gpuAccessAllowed) {
        toast.error("Offline mode is restricted in guest simulation", {
          description: "Remove ?guest=1 from URL to restore offline mode.",
          duration: 4000
        });
        return;
      }
      setShowModal(true);
    } else if (!gpuTelemetry?.is_model_in_vram) {
      // Offline model not warmed up -> open modal to initialize
      setShowModal(true);
    } else {
      setIsOffline(false);
      api.setOfflineMode(false).catch(() => {});
      api.unloadModel('qwen2.5:7b')
        .then(() => {
          fetchGpuTelemetry();
          toast.success('🌐 Online Mode Active: Cloud Gemini with Multi-Tier Cache');
        })
        .catch(() => {
          fetchGpuTelemetry();
          toast.success('🌐 Online Mode Active: Cloud Gemini with Multi-Tier Cache');
        });
    }
  };

  const handleOfflineSuccess = async (data: any) => {
    setIsOffline(true);
    await api.setOfflineMode(true, 'qwen2.5:7b').catch(() => {});
    setGpuTelemetry({
      is_model_in_vram: true,
      vram_size_formatted: data?.vram_size_formatted || '4.42 GB',
      vram_used_mb: data?.vram_used_mb || 4633,
      vram_total_mb: data?.vram_total_mb || 8188,
      gpu_name: 'Offline Model: Qwen 2.5 (7B)'
    });
    toast.success('⚡ Offline Mode Active: Qwen 2.5 (7B)');
  };

  const sendQuery = async (queryText: string) => {
    const trimmed = queryText.trim();
    if (!trimmed || isLoading) return;

    const userMessage: Message = { id: Date.now().toString(), role: 'user', content: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setHistoryIndex(-1);
    tempInputRef.current = '';
    setPromptHistory((prev) => (prev[prev.length - 1] === trimmed ? prev : [...prev, trimmed]));
    setIsLoading(true);

    const history = messages
      .filter((m) => !m.content.startsWith('⚠️'))
      .map((m) => ({ role: m.role, content: m.content }));
    history.push({ role: 'user', content: trimmed });

    // Determine target API endpoint
    // If on localhost or local Wi-Fi LAN IP (e.g. phone connecting to laptop), target the laptop directly
    const hostname = typeof window !== 'undefined' ? window.location.hostname : '';
    const isLocal =
      hostname === 'localhost' ||
      hostname === '127.0.0.1' ||
      /^192\.168\./.test(hostname) ||
      /^10\./.test(hostname) ||
      /^172\.(1[6-9]|2\d|3[01])\./.test(hostname);

    const apiUrl = getBaseUrl();
    const targetModel = isOffline ? 'qwen2.5:7b' : 'gemini-3.6-flash';

    try {
      const res = await fetch(`${apiUrl}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: trimmed,
          messages: history.slice(-20),
          model: targetModel,
          offline_mode: isOffline,
        }),
      });

      if (!res.ok) {
        const errorText = await res.text();
        let errMsg = `Server returned ${res.status}`;
        try {
          const errObj = JSON.parse(errorText);
          if (errObj.detail) errMsg = typeof errObj.detail === 'string' ? errObj.detail : JSON.stringify(errObj.detail);
        } catch {}
        throw new Error(errMsg);
      }

      const data = await res.json();
      let responseContent = data.response || 'No response returned.';

      if (isOffline && (responseContent.includes('Could not connect to Ollama') || responseContent.includes('port 11434 unreachable'))) {
        responseContent = `⚡ **Local LLM Notice**:\n\nCould not reach local Ollama on port 11434. Please ensure Ollama is running (\`ollama serve\` or launch Ollama from your Start menu).`;
      } else if (!isOffline && (responseContent.includes('429') || responseContent.toLowerCase().includes('quota'))) {
        responseContent = `⚠️ **Cloud Gemini Notice (Rate Limit / Quota Exceeded)**:\n\nGoogle Gemini returned **HTTP 429 (Rate Limit / Quota Exceeded)** on your current API key.\n\n**Quick Solutions:**\n• **Update API Key**: Generate a fresh free key at [Google AI Studio](https://aistudio.google.com/app/apikey) and add it to your environment variables (\`GEMINI_API_KEY\`).\n• **Use Offline Model**: Switch to **Offline Mode (Qwen 2.5 7B)** to run local inference with zero cloud API limits.`;
      }

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: responseContent,
        metadata: {
          latency: data.latency_ms,
          hit_type: data.status === 'CACHE_HIT' 
            ? (data.source?.includes('L0') ? 'CACHE_HIT_L0' : data.source?.includes('Redis') ? 'CACHE_HIT_L1' : 'CACHE_HIT_L2') 
            : 'CACHE_MISS',
          source: data.source,
          similarity: data.similarity_score,
          similarity_threshold: data.similarity_threshold,
          query_hash: data.query_hash,
          feedback: null,
          offline_mode: data.offline_mode,
          fallback_triggered: data.fallback_triggered,
          fallback_reason: data.fallback_reason,
          note: data.note,
          routed_model: data.routed_model,
          router_category: data.router_category,
          router_reason: data.router_reason,
        },
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      toast.error(`Query Failed: ${msg}`);

      // If user was on cloud Vercel and attempted Offline execution:
      const helpContent = (!isLocal && isOffline)
        ? `⚡ **Offline Model Routing**:\n\nTo execute queries with the offline model directly, open Cache-Craft at **[http://localhost:3000](http://localhost:3000)**!\n\n*(Your browser's security rules prevent cloud HTTPS domains like vercel.app from accessing local ports directly. Your local instance is available at [http://localhost:3000](http://localhost:3000)).*`
        : `⚠️ **Connection Error**: ${msg}\n\n*Check that the backend server is reachable.*`;

      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: helpContent,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleResetChat = () => {
    setMessages([]);
    setInput('');
    setHistoryIndex(-1);
    tempInputRef.current = '';
    if (typeof window !== 'undefined') {
      try {
        sessionStorage.removeItem(CHAT_STORAGE_KEY);
      } catch {}
    }
    textareaRef.current?.focus();
    toast.info('Started fresh session');
  };

  const handleFeedback = async (msgId: string, queryHash: string, isPositive: boolean) => {
    try {
      await api.feedback(queryHash, isPositive);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === msgId ? { ...m, metadata: { ...m.metadata, feedback: isPositive ? 'positive' : 'negative' } } : m
        )
      );
      toast.success(isPositive ? '👍 Feedback recorded' : '👎 Feedback recorded');
    } catch {
      toast.error('Failed to record feedback');
    }
  };

  const renderBadge = (msg: Message) => {
    const meta = msg.metadata;
    if (!meta) return null;
    
    const isL0 = meta.hit_type === 'CACHE_HIT_L0';
    const isL1 = meta.hit_type === 'CACHE_HIT_L1';
    const isL2 = meta.hit_type === 'CACHE_HIT_L2';

    const pillStyle = (isL0 || isL1)
      ? 'bg-white/[0.05] text-zinc-200 border-white/[0.1]' 
      : isL2
      ? 'bg-white/[0.04] text-zinc-300 border-white/[0.08]'
      : 'bg-white/[0.03] text-zinc-400 border-white/[0.06]';

    const dotColor = (isL0 || isL1)
      ? 'bg-emerald-400/80'
      : isL2
      ? 'bg-zinc-300'
      : 'bg-zinc-500';

    const Icon = (isL0 || isL1) ? Zap : isL2 ? Database : Server;

    const label = isL0
      ? 'L0 Exact Hit (RAM)'
      : isL1 
      ? 'L1 Cache Hit (Redis)' 
      : isL2
      ? `L2 Semantic Hit (${(meta.similarity! * 100).toFixed(1)}%)`
      : 'Cache Miss · Inference Generated';

    return (
      <motion.div 
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        className="space-y-2 mt-2 select-none"
      >
        <div className="flex items-center gap-2 flex-wrap text-xs">
          <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium border ${pillStyle}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
            <Icon className="w-3 h-3" />
            {label}
          </span>

          <span className="text-[11px] text-zinc-400 font-mono flex items-center gap-1">
            ⚡ {meta.latency !== undefined ? `${meta.latency.toFixed(1)}ms` : '—'}
          </span>

          {meta.offline_mode && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] border border-white/10 bg-white/[0.05] text-zinc-200 font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-zinc-300" />
              <Cpu className="w-2.5 h-2.5 text-zinc-400" />
              <span>Offline Model: Qwen 2.5 (7B)</span>
            </span>
          )}

          {meta.routed_model && meta.hit_type === 'CACHE_MISS' && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] border border-white/10 bg-white/[0.04] text-zinc-300">
              <Sparkles className="w-2.5 h-2.5 mr-0.5 text-zinc-400" />
              <span>Model: {meta.routed_model}</span>
            </span>
          )}

          {meta.query_hash && (
            <div className="flex items-center gap-1 ml-auto">
              <button
                onClick={() => handleCopy(msg.id, msg.content)}
                className="p-1 rounded-md text-zinc-500 hover:text-zinc-200 transition-colors"
                title="Copy response"
              >
                {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-zinc-200" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
              <button
                onClick={() => handleFeedback(msg.id, meta.query_hash!, true)}
                disabled={meta.feedback !== null && meta.feedback !== undefined}
                className={`p-1 rounded-md transition-colors ${
                  meta.feedback === 'positive' ? 'text-zinc-200' : 'text-zinc-500 hover:text-zinc-200'
                }`}
                title="Good answer"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => handleFeedback(msg.id, meta.query_hash!, false)}
                disabled={meta.feedback !== null && meta.feedback !== undefined}
                className={`p-1 rounded-md transition-colors ${
                  meta.feedback === 'negative' ? 'text-zinc-400' : 'text-zinc-500 hover:text-zinc-200'
                }`}
                title="Bad answer"
              >
                <ThumbsDown className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      </motion.div>
    );
  };

  const isChatEmpty = messages.length === 0;

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] w-full max-w-3xl mx-auto px-4 relative">
      {/* Alert & Model Loading Transition Modal */}
      <OfflineTransitionModal
        isOpen={showModal}
        targetModel="qwen2.5:7b"
        onClose={() => setShowModal(false)}
        onSuccess={handleOfflineSuccess}
      />

      {/* Top Header Toolbar (active chat) */}
      {!isChatEmpty && (
        <div className="flex items-center justify-between py-3 border-b border-white/[0.08] shrink-0">
          <motion.button
            type="button"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            onClick={handleResetChat}
            className="h-8 px-3 text-xs text-zinc-400 hover:text-zinc-200 rounded-lg flex items-center gap-1.5 transition-colors border border-white/[0.08] bg-[#121215]"
          >
            <RotateCcw className="w-3 h-3 text-zinc-400" />
            <span>New Session</span>
          </motion.button>

          {/* Unified 165Hz Online / Offline GPU Switch */}
          <motion.button
            id="offline-gpu-toggle-btn-header"
            type="button"
            whileHover={{ scale: 1.02, y: -1 }}
            whileTap={{ scale: 0.96 }}
            transition={{ type: 'spring', stiffness: 500, damping: 25 }}
            onClick={handleToggleClick}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl border text-xs font-medium transition-all shadow-sm select-none will-change-transform ${
              isOffline
                ? 'bg-[#18181d] border-white/[0.18] text-zinc-100 hover:border-white/30'
                : 'bg-[#141417] border-white/[0.1] text-zinc-200 hover:border-white/20'
            }`}
          >
            {isOffline ? (
              <>
                <span className={`w-2 h-2 rounded-full ${gpuTelemetry?.is_model_in_vram ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400 animate-pulse'}`} />
                <Cpu className="w-3.5 h-3.5 text-zinc-300" />
                <span className="font-semibold tracking-wide">
                  {gpuTelemetry?.is_model_in_vram
                    ? 'Offline Model: Qwen 2.5 (7B)'
                    : 'Offline Model: Qwen 2.5 (Click to Load)'}
                </span>
              </>
            ) : (
              <>
                <span className="w-2 h-2 rounded-full bg-emerald-400/80" />
                <Globe className="w-3.5 h-3.5 text-zinc-300" />
                <span className="font-semibold tracking-wide">Online · Cloud Gemini</span>
              </>
            )}
          </motion.button>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto min-h-0 py-4 space-y-6">
        {isChatEmpty ? (
          /* Cache-Craft Minimalist Neural Hero (Subtle & Refined 165Hz) */
          <div className="h-full flex flex-col items-center justify-center -mt-8 space-y-7 select-none">
            {/* Cache-Craft Emblem & Title */}
            <motion.div
              initial={{ scale: 0.94, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ type: 'spring', stiffness: 380, damping: 26 }}
              className="flex items-center gap-3.5"
            >
              <CacheCraftEmblem />
              <div className="text-left">
                <h1 className="text-2xl sm:text-3xl text-zinc-100 font-semibold tracking-tight">
                  Cache-Craft Neural Core
                </h1>
                <p className="text-xs text-zinc-400 font-normal tracking-wide mt-0.5">
                  Multi-Tier Semantic Memory · Redis L1 · pgvector L2 · Local &amp; Cloud Routing
                </p>
              </div>
            </motion.div>

            {/* Floating Matte Graphite Prompt Card */}
            <motion.div
              initial={{ y: 14, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ type: 'spring', stiffness: 380, damping: 26, delay: 0.05 }}
              className="w-full max-w-2xl bg-[#121215] border border-white/[0.08] hover:border-white/[0.16] focus-within:border-white/25 focus-within:shadow-[0_0_30px_rgba(255,255,255,0.03)] rounded-[22px] shadow-2xl p-3.5 sm:p-4.5 space-y-3 transition-all duration-300 will-change-transform"
            >
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  if (historyIndex !== -1) setHistoryIndex(-1);
                }}
                onKeyDown={handleKeyDown}
                rows={3}
                placeholder={isOffline ? "Query offline model (Qwen 2.5 7B) with semantic cache..." : "Ask anything or test semantic cache recall..."}
                className="w-full bg-transparent text-sm sm:text-base text-zinc-100 placeholder:text-zinc-500 resize-none outline-none leading-relaxed font-normal"
              />

              {/* Functional Controls Toolbar */}
              <div className="flex items-center justify-between pt-2 border-t border-white/[0.06]">
                {/* Active Cache Engine Indicator */}
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/[0.04] border border-white/[0.08] text-zinc-300 text-xs font-medium select-none">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  <span>Cache-Craft Active · L1 / L2</span>
                </div>

                {/* Right Controls: Unified 165Hz Online / Offline GPU Switch & Send Button */}
                <div className="flex items-center gap-2">
                  <motion.button
                    id="offline-gpu-toggle-btn"
                    type="button"
                    whileHover={{ scale: 1.02, y: -1 }}
                    whileTap={{ scale: 0.96 }}
                    transition={{ type: 'spring', stiffness: 500, damping: 25 }}
                    onClick={handleToggleClick}
                    className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl border text-xs font-medium transition-all shadow-sm select-none will-change-transform ${
                      isOffline
                        ? 'bg-[#18181d] border-white/[0.18] text-zinc-100 hover:border-white/30'
                        : 'bg-[#141417] border-white/[0.1] text-zinc-200 hover:border-white/20'
                    }`}
                  >
                    {isOffline ? (
                      <>
                        <span className={`w-2 h-2 rounded-full ${gpuTelemetry?.is_model_in_vram ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400 animate-pulse'}`} />
                        <Cpu className="w-3.5 h-3.5 text-zinc-300" />
                        <span className="font-semibold tracking-wide">
                          {gpuTelemetry?.is_model_in_vram
                            ? 'Offline Model: Qwen 2.5 (7B)'
                            : 'Offline Model: Qwen 2.5 (Click to Load)'}
                        </span>
                      </>
                    ) : (
                      <>
                        <span className="w-2 h-2 rounded-full bg-emerald-400/80" />
                        <Globe className="w-3.5 h-3.5 text-zinc-300" />
                        <span className="font-semibold tracking-wide">Online · Cloud Gemini</span>
                      </>
                    )}
                  </motion.button>

                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.94 }}
                    transition={{ type: 'spring', stiffness: 450, damping: 20 }}
                    onClick={() => sendQuery(input)}
                    disabled={!input.trim() || isLoading}
                    className="h-8 w-8 rounded-xl bg-zinc-100 hover:bg-white text-zinc-950 flex items-center justify-center transition-all disabled:opacity-20 disabled:pointer-events-none shadow-sm active:scale-95 will-change-transform"
                    title="Send query (Enter)"
                  >
                    <ArrowUp className="w-4 h-4 stroke-[2.5]" />
                  </motion.button>
                </div>
              </div>
            </motion.div>

            {/* Sleek Preset Query Pills */}
            <div className="w-full max-w-2xl flex flex-wrap gap-2 justify-center pt-1">
              {SUGGESTIONS.map((item, idx) => (
                <motion.button
                  key={idx}
                  whileHover={{ scale: 1.02, y: -1 }}
                  whileTap={{ scale: 0.97 }}
                  transition={{ type: 'spring', stiffness: 450, damping: 25 }}
                  onClick={() => sendQuery(item)}
                  className="text-xs text-zinc-400 hover:text-zinc-200 bg-[#141417] hover:bg-[#19191d] border border-white/[0.06] hover:border-white/[0.14] rounded-full px-3.5 py-1.5 transition-all text-left shadow-xs will-change-transform"
                >
                  {item}
                </motion.button>
              ))}
            </div>
          </div>
        ) : (
          /* Active Chat Stream */
          <div className="space-y-6 pb-28">
            <AnimatePresence initial={false}>
              {messages.map((msg) => {
                const isUser = msg.role === 'user';
                return (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ type: 'spring', stiffness: 420, damping: 28 }}
                    className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
                  >
                    {isUser ? (
                      <div className="bg-[#18181c] text-zinc-100 text-sm sm:text-base rounded-2xl rounded-tr-sm px-4 py-2.5 max-w-[85%] whitespace-pre-wrap leading-relaxed border border-white/[0.08] shadow-sm">
                        {msg.content}
                      </div>
                    ) : (
                      <div className="w-full space-y-2">
                        <div className="flex items-center gap-2 mb-1">
                          <Zap className="w-3.5 h-3.5 text-zinc-300" />
                          <span className="text-xs font-semibold text-zinc-200 tracking-wide">Cache-Craft</span>
                        </div>

                        <div className="prose prose-sm dark:prose-invert max-w-none text-zinc-200 leading-relaxed font-normal">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm, remarkMath]}
                            rehypePlugins={[[rehypeKatex, { throwOnError: false }]]}
                          >
                            {preprocessMathMarkdown(msg.content)}
                          </ReactMarkdown>
                        </div>

                        {renderBadge(msg)}
                      </div>
                    )}
                  </motion.div>
                );
              })}

              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-2 text-zinc-400 text-xs"
                >
                  <Zap className="w-4 h-4 text-zinc-300 animate-pulse" />
                  <span className="font-medium tracking-wide">
                    {isOffline ? "Routing query directly to offline model (Qwen 2.5)..." : "Routing through multi-tier cache & cloud..."}
                  </span>
                </motion.div>
              )}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Docked Floating Input Bar (when chat is active) */}
      {!isChatEmpty && (
        <div className="absolute bottom-4 left-4 right-4 max-w-3xl mx-auto">
          <div className="bg-[#121215]/95 border border-white/[0.1] hover:border-white/[0.18] focus-within:border-white/25 rounded-2xl shadow-2xl p-2.5 sm:p-3 space-y-2 backdrop-blur-2xl transition-all">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                if (historyIndex !== -1) setHistoryIndex(-1);
              }}
              onKeyDown={handleKeyDown}
              rows={2}
              placeholder="Ask a follow-up query to test context caching..."
              className="w-full bg-transparent text-sm text-zinc-100 placeholder:text-zinc-500 resize-none outline-none leading-relaxed"
            />

            <div className="flex items-center justify-between pt-1 border-t border-white/[0.06]">
              <div className="flex items-center gap-1.5 text-xs text-zinc-300 font-medium select-none">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span>Multi-Tier Active</span>
              </div>

              <div className="flex items-center gap-2">
                <motion.button
                  id="offline-gpu-toggle-btn-dock"
                  type="button"
                  whileHover={{ scale: 1.02, y: -1 }}
                  whileTap={{ scale: 0.96 }}
                  transition={{ type: 'spring', stiffness: 500, damping: 25 }}
                  onClick={handleToggleClick}
                  className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl border text-xs font-medium transition-all shadow-sm select-none will-change-transform ${
                    isOffline
                      ? 'bg-[#18181d] border-white/[0.18] text-zinc-100 hover:border-white/30'
                      : 'bg-[#141417] border-white/[0.1] text-zinc-200 hover:border-white/20'
                  }`}
                >
                  {isOffline ? (
                    <>
                      <span className={`w-2 h-2 rounded-full ${gpuTelemetry?.is_model_in_vram ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400 animate-pulse'}`} />
                      <Cpu className="w-3.5 h-3.5 text-zinc-300" />
                      <span className="font-semibold tracking-wide">
                        {gpuTelemetry?.is_model_in_vram
                          ? 'Offline Model: Qwen 2.5 (7B)'
                          : 'Offline Model: Qwen 2.5 (Click to Load)'}
                      </span>
                    </>
                  ) : (
                    <>
                      <span className="w-2 h-2 rounded-full bg-emerald-400/80" />
                      <Globe className="w-3.5 h-3.5 text-zinc-300" />
                      <span className="font-semibold tracking-wide">Online · Cloud Gemini</span>
                    </>
                  )}
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.94 }}
                  transition={{ type: 'spring', stiffness: 450, damping: 20 }}
                  onClick={() => sendQuery(input)}
                  disabled={!input.trim() || isLoading}
                  className="h-7 w-7 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 flex items-center justify-center transition-all disabled:opacity-20 disabled:pointer-events-none shadow-sm active:scale-95 will-change-transform"
                  title="Send message"
                >
                  <ArrowUp className="w-3.5 h-3.5 stroke-[2.5]" />
                </motion.button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
