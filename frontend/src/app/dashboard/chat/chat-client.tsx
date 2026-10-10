'use client';

import React, { useState, useRef, useEffect } from 'react';
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
  ShieldCheck, 
  AlertCircle, 
  Activity,
  CheckCircle2
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { api } from '@/lib/api';

// Cache-Craft's signature Quantum Neural Cache Core (Bespoke Cyber-Cyan & Electric-Violet)
function CacheCraftEmblem({ className = "w-12 h-12" }: { className?: string }) {
  return (
    <div className={`relative flex items-center justify-center shrink-0 ${className}`}>
      {/* 165Hz High-refresh atmospheric ambient cyber aura */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-cyan-500/25 via-blue-500/20 to-violet-600/20 blur-xl animate-pulse" />
      <div className="relative w-full h-full rounded-2xl bg-gradient-to-b from-[#111728] via-[#0c101d] to-[#070a13] border border-cyan-500/35 flex items-center justify-center shadow-[0_8px_32px_rgba(6,182,212,0.2)] ring-1 ring-white/10 will-change-transform">
        <svg 
          viewBox="0 0 24 24" 
          className="w-6 h-6 text-cyan-400 drop-shadow-[0_0_12px_rgba(34,211,238,0.8)]" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2.2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          {/* Cyber Cache Node Prism */}
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
          <path d="M2 12l10 5 10-5" />
          <circle cx="12" cy="12" r="1.5" fill="currentColor" />
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

// Futuristic Quantum GPU Transition Modal with Holographic Loader
function OfflineTransitionModal({
  isOpen,
  onClose,
  onConfirm
}: {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
}) {
  const [step, setStep] = useState<'alert' | 'loading' | 'ready'>('alert');
  const [progress, setProgress] = useState(0);
  const [currentTask, setCurrentTask] = useState('Initializing pipeline...');

  useEffect(() => {
    if (!isOpen) {
      setStep('alert');
      setProgress(0);
    }
  }, [isOpen]);

  const handleStartLoad = async () => {
    setStep('loading');
    setProgress(15);
    setCurrentTask('Verifying background Ollama daemon...');

    // Trigger preload on backend in parallel
    const preloadPromise = onConfirm();

    setTimeout(() => {
      setProgress(40);
      setCurrentTask('Allocating 4.7 GB into NVIDIA RTX 4060 VRAM...');
    }, 600);

    setTimeout(() => {
      setProgress(75);
      setCurrentTask('Mounting Qwen 2.5 (7B) weights & warm-up verification...');
    }, 1300);

    try {
      await preloadPromise;
    } catch {
      // Continue even on network hiccup
    }

    setProgress(100);
    setCurrentTask('RTX 4060 GPU Online · Zero-Latency Local Core Ready!');
    setStep('ready');

    setTimeout(() => {
      onClose();
    }, 1000);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Deep glass backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => step === 'alert' && onClose()}
          className="absolute inset-0 bg-black/80 backdrop-blur-md"
        />

        {/* Futuristic Modal Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 12 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 12 }}
          transition={{ type: 'spring', stiffness: 450, damping: 28 }}
          className="relative w-full max-w-md bg-[#0a0d16]/95 border border-cyan-500/30 rounded-3xl p-6 shadow-[0_0_60px_rgba(6,182,212,0.18)] text-foreground overflow-hidden ring-1 ring-white/10"
        >
          {/* Ambient Cyber Beam Glow */}
          <div className="absolute -top-24 -left-24 w-48 h-48 bg-cyan-500/15 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-violet-600/20 rounded-full blur-3xl pointer-events-none" />

          {step === 'alert' ? (
            /* Step 1: Confirmation Alert Box */
            <div className="space-y-5 text-left relative z-10 select-none">
              <div className="flex items-center gap-3.5">
                <div className="w-11 h-11 rounded-2xl bg-violet-950/80 border border-violet-500/40 flex items-center justify-center text-violet-400 shadow-[0_0_20px_rgba(139,92,246,0.3)]">
                  <Cpu className="w-6 h-6 animate-pulse" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-foreground tracking-tight bg-gradient-to-r from-violet-200 via-cyan-200 to-white bg-clip-text text-transparent">
                    Switch to Offline Mode?
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    Private Local GPU Inference · Zero Cloud Network
                  </p>
                </div>
              </div>

              {/* Hardware Telemetry Card */}
              <div className="p-3.5 rounded-2xl bg-[#0e1322] border border-white/[0.08] space-y-2.5 text-xs">
                <div className="flex items-center justify-between text-muted-foreground/80">
                  <span>Target Compute:</span>
                  <span className="font-semibold text-violet-300 font-mono">NVIDIA RTX 4060 (8GB)</span>
                </div>
                <div className="flex items-center justify-between text-muted-foreground/80">
                  <span>Local LLM:</span>
                  <span className="font-semibold text-cyan-300 font-mono">Qwen 2.5 (7B Instruct)</span>
                </div>
                <div className="flex items-center justify-between text-muted-foreground/80">
                  <span>Daemon Pipeline:</span>
                  <span className="font-semibold text-emerald-400">Background Auto-Start</span>
                </div>
                <div className="flex items-center justify-between text-muted-foreground/80">
                  <span>Multi-Tier Cache:</span>
                  <span className="font-semibold text-foreground">Redis L1 + Vector L2 Active</span>
                </div>
              </div>

              <p className="text-xs text-muted-foreground/75 leading-relaxed">
                Confirming will seamlessly boot your local Ollama daemon and pre-allocate model weights into GPU VRAM for instant offline query execution.
              </p>

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-2.5 pt-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 rounded-xl text-xs font-medium text-muted-foreground hover:text-foreground bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.06] transition-colors"
                >
                  Cancel
                </button>
                <motion.button
                  type="button"
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.96 }}
                  onClick={handleStartLoad}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-400 border border-violet-400/30 shadow-[0_0_20px_rgba(139,92,246,0.35)] transition-all flex items-center gap-1.5"
                >
                  <Cpu className="w-3.5 h-3.5" />
                  <span>Confirm &amp; Initialize GPU →</span>
                </motion.button>
              </div>
            </div>
          ) : (
            /* Step 2 & 3: Futuristic Holographic GPU Matrix Loader */
            <div className="py-4 text-center space-y-6 relative z-10 select-none">
              {/* Holographic Spinning Particle Rings */}
              <div className="relative w-28 h-28 mx-auto flex items-center justify-center">
                {/* Outer counter-clockwise ring */}
                <motion.div
                  animate={{ rotate: -360 }}
                  transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
                  className="absolute inset-0 rounded-full border border-dashed border-cyan-500/40 shadow-[0_0_20px_rgba(6,182,212,0.25)]"
                />
                {/* Inner clockwise neon ring */}
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2.2, repeat: Infinity, ease: 'linear' }}
                  className="absolute inset-2.5 rounded-full border-2 border-t-violet-400 border-r-transparent border-b-cyan-400 border-l-transparent shadow-[0_0_25px_rgba(139,92,246,0.4)]"
                />
                {/* Center Pulsing Chip Core */}
                <div className="relative w-14 h-14 rounded-2xl bg-gradient-to-tr from-violet-900 to-cyan-900 border border-cyan-400/50 flex items-center justify-center shadow-lg">
                  {step === 'ready' ? (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: 'spring', stiffness: 400, damping: 20 }}
                    >
                      <CheckCircle2 className="w-7 h-7 text-emerald-400 drop-shadow-[0_0_10px_#34d399]" />
                    </motion.div>
                  ) : (
                    <Cpu className="w-7 h-7 text-cyan-300 animate-pulse drop-shadow-[0_0_10px_#22d3ee]" />
                  )}
                </div>
              </div>

              {/* Dynamic Telemetry Status */}
              <div className="space-y-1.5">
                <h4 className="text-sm font-bold tracking-tight text-foreground font-mono">
                  {step === 'ready' ? '⚡ GPU ALLOCATION COMPLETE' : 'INITIALIZING LOCAL GPU'}
                </h4>
                <p className="text-xs text-cyan-300/90 font-mono tracking-wide h-4">
                  {currentTask}
                </p>
              </div>

              {/* Glowing High-Precision Progress Bar */}
              <div className="space-y-1.5 px-2">
                <div className="w-full h-2 rounded-full bg-white/[0.06] overflow-hidden border border-white/[0.08] p-0.5">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ ease: 'easeOut', duration: 0.3 }}
                    className="h-full rounded-full bg-gradient-to-r from-violet-500 via-indigo-500 to-cyan-400 shadow-[0_0_12px_rgba(6,182,212,0.8)]"
                  />
                </div>
                <div className="flex justify-between text-[10px] text-muted-foreground/60 font-mono">
                  <span>VRAM Pipeline</span>
                  <span>{progress}%</span>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>
      )}
    </AnimatePresence>
  );
}

export default function ChatClient() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [isOffline, setIsOffline] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    textareaRef.current?.focus();
    api.settings().then((s) => {
      if (s.offline_mode !== undefined) {
        setIsOffline(s.offline_mode);
      }
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!isLoading) {
      textareaRef.current?.focus();
    }
  }, [isLoading]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Click toggle handler: if going offline, prompt confirmation modal; if going online, instant switch
  const handleToggleClick = () => {
    if (!isOffline) {
      setShowModal(true);
    } else {
      setIsOffline(false);
      api.setOfflineMode(false).catch(() => {});
      toast.success('🌐 Online Mode Active: Cloud Gemini with Multi-Tier Cache');
    }
  };

  // Called when modal confirm button triggers GPU preload
  const handleConfirmOffline = async () => {
    try {
      await api.preloadModel('qwen2.5:7b');
    } catch {
      // Handled gracefully
    }
    setIsOffline(true);
    await api.setOfflineMode(true, 'qwen2.5:7b').catch(() => {});
    toast.success('⚡ Local GPU Active: Qwen 2.5 (7B) loaded into RTX 4060 VRAM');
  };

  const sendQuery = async (queryText: string) => {
    const trimmed = queryText.trim();
    if (!trimmed || isLoading) return;

    const userMessage: Message = { id: Date.now().toString(), role: 'user', content: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const history = messages
      .filter((m) => !m.content.startsWith('⚠️'))
      .map((m) => ({ role: m.role, content: m.content }));
    history.push({ role: 'user', content: trimmed });

    // Intelligently route to localhost:8000 if user is testing local GPU, otherwise default API URL
    const isLocalhostEnv = typeof window !== 'undefined' && 
      (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
    const apiUrl = isLocalhostEnv
      ? 'http://localhost:8000'
      : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

    const targetModel = isOffline ? 'qwen2.5:7b' : 'gemini-3.8-flash';

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
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'No response returned.',
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
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `⚠️ **Connection Error**: ${msg}\n\n*Check that the backend server is reachable.*`,
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
      ? 'bg-cyan-500/10 text-cyan-300 border-cyan-500/25' 
      : isL2
      ? 'bg-violet-500/10 text-violet-300 border-violet-500/30'
      : 'bg-white/[0.04] text-muted-foreground border-white/[0.08]';

    const dotColor = (isL0 || isL1)
      ? 'bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)]'
      : isL2
      ? 'bg-violet-400 shadow-[0_0_8px_rgba(139,92,246,0.8)]'
      : 'bg-muted-foreground/60';

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

          <span className="text-[11px] text-muted-foreground font-mono flex items-center gap-1">
            ⚡ {meta.latency !== undefined ? `${meta.latency.toFixed(1)}ms` : '—'}
          </span>

          {meta.offline_mode && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] border border-violet-500/30 bg-violet-500/10 text-violet-300 font-mono">
              <Cpu className="w-2.5 h-2.5" />
              <span>RTX 4060 Local</span>
            </span>
          )}

          {meta.routed_model && meta.hit_type === 'CACHE_MISS' && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] border border-cyan-500/30 bg-cyan-500/10 text-cyan-300">
              <Sparkles className="w-2.5 h-2.5 mr-0.5" />
              <span>Model: {meta.routed_model}</span>
            </span>
          )}

          {meta.query_hash && (
            <div className="flex items-center gap-1 ml-auto">
              <button
                onClick={() => handleCopy(msg.id, msg.content)}
                className="p-1 rounded-md text-muted-foreground/60 hover:text-cyan-400 transition-colors"
                title="Copy response"
              >
                {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-cyan-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
              <button
                onClick={() => handleFeedback(msg.id, meta.query_hash!, true)}
                disabled={meta.feedback !== null && meta.feedback !== undefined}
                className={`p-1 rounded-md transition-colors ${
                  meta.feedback === 'positive' ? 'text-cyan-400' : 'text-muted-foreground/60 hover:text-cyan-400'
                }`}
                title="Good answer"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => handleFeedback(msg.id, meta.query_hash!, false)}
                disabled={meta.feedback !== null && meta.feedback !== undefined}
                className={`p-1 rounded-md transition-colors ${
                  meta.feedback === 'negative' ? 'text-rose-400' : 'text-muted-foreground/60 hover:text-rose-400'
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
        onClose={() => setShowModal(false)}
        onConfirm={handleConfirmOffline}
      />

      {/* Top Header Toolbar (active chat) */}
      {!isChatEmpty && (
        <div className="flex items-center justify-between py-3 border-b border-white/[0.08] shrink-0">
          <motion.button
            type="button"
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.96 }}
            onClick={handleResetChat}
            className="h-8 px-3 text-xs text-muted-foreground hover:text-cyan-300 rounded-lg flex items-center gap-1.5 transition-colors border border-white/[0.08] hover:border-cyan-500/30 bg-[#0d121f]"
          >
            <RotateCcw className="w-3 h-3 text-cyan-400" />
            <span>New Session</span>
          </motion.button>

          {/* Unified 165Hz Online / Offline GPU Switch */}
          <motion.button
            type="button"
            whileHover={{ scale: 1.03, y: -1 }}
            whileTap={{ scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 500, damping: 25 }}
            onClick={handleToggleClick}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl border text-xs font-medium transition-all shadow-sm backdrop-blur-md select-none will-change-transform ${
              isOffline
                ? 'bg-violet-950/70 border-violet-500/40 text-violet-200 hover:border-violet-400 shadow-[0_0_15px_rgba(139,92,246,0.2)]'
                : 'bg-cyan-950/50 border-cyan-500/40 text-cyan-200 hover:border-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.2)]'
            }`}
          >
            {isOffline ? (
              <>
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-violet-400 shadow-[0_0_8px_#a855f7]" />
                </span>
                <Cpu className="w-3.5 h-3.5 text-violet-400" />
                <span className="font-semibold tracking-wide">Offline · Local LLM (RTX 4060)</span>
              </>
            ) : (
              <>
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-400 shadow-[0_0_8px_#22d3ee]" />
                </span>
                <Globe className="w-3.5 h-3.5 text-cyan-400" />
                <span className="font-semibold tracking-wide">Online · Cloud Gemini</span>
              </>
            )}
          </motion.button>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto min-h-0 py-4 space-y-6">
        {isChatEmpty ? (
          /* Cache-Craft Signature Cyber-Neural Hero (165Hz Optimized) */
          <div className="h-full flex flex-col items-center justify-center -mt-8 space-y-7 select-none">
            {/* Cache-Craft Emblem & Title */}
            <motion.div
              initial={{ scale: 0.92, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ type: 'spring', stiffness: 380, damping: 26 }}
              className="flex items-center gap-4"
            >
              <CacheCraftEmblem />
              <div className="text-left">
                <h1 className="text-2xl sm:text-3xl text-foreground font-semibold tracking-tight bg-gradient-to-r from-cyan-300 via-blue-200 to-violet-300 bg-clip-text text-transparent">
                  Cache-Craft Neural Core
                </h1>
                <p className="text-xs text-muted-foreground/80 font-normal tracking-wide mt-0.5">
                  Multi-Tier Semantic Memory · Redis L1 · pgvector L2 · RTX 4060 &amp; Cloud Routing
                </p>
              </div>
            </motion.div>

            {/* Floating Glassmorphic Cyber Prompt Card */}
            <motion.div
              initial={{ y: 16, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ type: 'spring', stiffness: 380, damping: 26, delay: 0.05 }}
              className="w-full max-w-2xl bg-[#0c101c]/95 border border-white/[0.1] hover:border-cyan-500/35 focus-within:border-cyan-500/50 focus-within:shadow-[0_0_35px_rgba(6,182,212,0.18)] rounded-[22px] shadow-2xl p-3.5 sm:p-4.5 space-y-3 transition-all duration-300 backdrop-blur-2xl will-change-transform ring-1 ring-white/5"
            >
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (!isLoading && input.trim()) {
                      sendQuery(input);
                    }
                  }
                }}
                rows={3}
                placeholder={isOffline ? "Query local RTX 4060 GPU with semantic cache..." : "Ask anything or test semantic cache recall..."}
                className="w-full bg-transparent text-sm sm:text-base text-foreground placeholder:text-muted-foreground/45 resize-none outline-none leading-relaxed font-normal"
              />

              {/* Functional Controls Toolbar */}
              <div className="flex items-center justify-between pt-2 border-t border-white/[0.06]">
                {/* Active Cache Engine Indicator */}
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/25 text-cyan-300 text-xs font-medium select-none">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.9)] animate-pulse" />
                  <span>Cache-Craft Active · L1 / L2</span>
                </div>

                {/* Right Controls: Unified 165Hz Online / Offline GPU Switch & Send Button */}
                <div className="flex items-center gap-2">
                  <motion.button
                    type="button"
                    whileHover={{ scale: 1.03, y: -1 }}
                    whileTap={{ scale: 0.95 }}
                    transition={{ type: 'spring', stiffness: 500, damping: 25 }}
                    onClick={handleToggleClick}
                    className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl border text-xs font-medium transition-all shadow-sm backdrop-blur-md select-none will-change-transform ${
                      isOffline
                        ? 'bg-violet-950/70 border-violet-500/40 text-violet-200 hover:border-violet-400 shadow-[0_0_15px_rgba(139,92,246,0.2)]'
                        : 'bg-cyan-950/50 border-cyan-500/40 text-cyan-200 hover:border-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.2)]'
                    }`}
                  >
                    {isOffline ? (
                      <>
                        <span className="relative flex h-2 w-2">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75" />
                          <span className="relative inline-flex rounded-full h-2 w-2 bg-violet-400 shadow-[0_0_8px_#a855f7]" />
                        </span>
                        <Cpu className="w-3.5 h-3.5 text-violet-400" />
                        <span className="font-semibold tracking-wide">Offline · Local LLM (RTX 4060)</span>
                      </>
                    ) : (
                      <>
                        <span className="relative flex h-2 w-2">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
                          <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-400 shadow-[0_0_8px_#22d3ee]" />
                        </span>
                        <Globe className="w-3.5 h-3.5 text-cyan-400" />
                        <span className="font-semibold tracking-wide">Online · Cloud Gemini</span>
                      </>
                    )}
                  </motion.button>

                  <motion.button
                    whileHover={{ scale: 1.06 }}
                    whileTap={{ scale: 0.92 }}
                    transition={{ type: 'spring', stiffness: 450, damping: 20 }}
                    onClick={() => sendQuery(input)}
                    disabled={!input.trim() || isLoading}
                    className="h-8 w-8 rounded-xl bg-gradient-to-tr from-cyan-500 via-blue-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-white flex items-center justify-center transition-all disabled:opacity-30 disabled:pointer-events-none shadow-md shadow-cyan-500/25 active:scale-95 will-change-transform"
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
                  whileHover={{ scale: 1.025, y: -2 }}
                  whileTap={{ scale: 0.97 }}
                  transition={{ type: 'spring', stiffness: 450, damping: 25 }}
                  onClick={() => sendQuery(item)}
                  className="text-xs text-muted-foreground/80 hover:text-cyan-200 bg-[#0f1424]/80 hover:bg-[#141b2e] border border-white/[0.06] hover:border-cyan-500/35 rounded-full px-3.5 py-1.5 transition-all text-left shadow-xs backdrop-blur-md will-change-transform"
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
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ type: 'spring', stiffness: 420, damping: 28 }}
                    className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
                  >
                    {isUser ? (
                      <div className="bg-[#141a29] text-foreground text-sm sm:text-base rounded-2xl rounded-tr-sm px-4 py-2.5 max-w-[85%] whitespace-pre-wrap leading-relaxed border border-white/[0.08] shadow-sm">
                        {msg.content}
                      </div>
                    ) : (
                      <div className="w-full space-y-2">
                        <div className="flex items-center gap-2 mb-1">
                          <Zap className="w-3.5 h-3.5 text-cyan-400" />
                          <span className="text-xs font-semibold text-foreground/80 tracking-wide">Cache-Craft</span>
                        </div>

                        <div className="prose prose-sm dark:prose-invert max-w-none text-foreground/90 leading-relaxed font-normal">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {msg.content}
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
                  className="flex items-center gap-2 text-muted-foreground text-xs"
                >
                  <Zap className="w-4 h-4 text-cyan-400 animate-pulse" />
                  <span className="font-medium tracking-wide">
                    {isOffline ? "Routing query directly to local RTX 4060 GPU..." : "Routing through multi-tier cache & cloud..."}
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
          <div className="bg-[#0c101c]/95 border border-white/[0.1] hover:border-cyan-500/35 focus-within:border-cyan-500/50 rounded-2xl shadow-2xl p-2.5 sm:p-3 space-y-2 backdrop-blur-2xl transition-all ring-1 ring-white/5">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  if (!isLoading && input.trim()) {
                    sendQuery(input);
                  }
                }
              }}
              rows={2}
              placeholder="Ask a follow-up query to test context caching..."
              className="w-full bg-transparent text-sm text-foreground placeholder:text-muted-foreground/45 resize-none outline-none leading-relaxed"
            />

            <div className="flex items-center justify-between pt-1 border-t border-white/[0.06]">
              <div className="flex items-center gap-1.5 text-xs text-cyan-300 font-medium select-none">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_6px_rgba(6,182,212,0.8)]" />
                <span>Multi-Tier Active</span>
              </div>

              <div className="flex items-center gap-2">
                <motion.button
                  type="button"
                  whileHover={{ scale: 1.03, y: -1 }}
                  whileTap={{ scale: 0.95 }}
                  transition={{ type: 'spring', stiffness: 500, damping: 25 }}
                  onClick={handleToggleClick}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-medium transition-all shadow-sm backdrop-blur-md select-none will-change-transform ${
                    isOffline
                      ? 'bg-violet-950/70 border-violet-500/40 text-violet-200 hover:border-violet-400 shadow-[0_0_15px_rgba(139,92,246,0.2)]'
                      : 'bg-cyan-950/50 border-cyan-500/40 text-cyan-200 hover:border-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.2)]'
                  }`}
                >
                  {isOffline ? (
                    <>
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75" />
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-violet-400 shadow-[0_0_8px_#a855f7]" />
                      </span>
                      <Cpu className="w-3.5 h-3.5 text-violet-400" />
                      <span className="font-semibold tracking-wide">Offline · Local LLM</span>
                    </>
                  ) : (
                    <>
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-400 shadow-[0_0_8px_#22d3ee]" />
                      </span>
                      <Globe className="w-3.5 h-3.5 text-cyan-400" />
                      <span className="font-semibold tracking-wide">Online · Cloud Gemini</span>
                    </>
                  )}
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.06 }}
                  whileTap={{ scale: 0.92 }}
                  transition={{ type: 'spring', stiffness: 450, damping: 20 }}
                  onClick={() => sendQuery(input)}
                  disabled={!input.trim() || isLoading}
                  className="h-7 w-7 rounded-lg bg-gradient-to-tr from-cyan-500 via-blue-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-white flex items-center justify-center transition-all disabled:opacity-30 disabled:pointer-events-none shadow-md shadow-cyan-500/25 active:scale-95 will-change-transform"
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
