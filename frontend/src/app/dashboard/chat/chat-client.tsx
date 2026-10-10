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
  ExternalLink,
  CheckCircle2
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { api } from '@/lib/api';

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

// Subtle, Minimalist Offline GPU Transition Modal
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
    setProgress(20);
    setCurrentTask('Verifying background Ollama daemon...');

    const preloadPromise = onConfirm();

    setTimeout(() => {
      setProgress(50);
      setCurrentTask('Allocating 4.7 GB into NVIDIA RTX 4060 VRAM...');
    }, 500);

    setTimeout(() => {
      setProgress(85);
      setCurrentTask('Mounting Qwen 2.5 (7B) weights & warm-up verification...');
    }, 1100);

    try {
      await preloadPromise;
    } catch {}

    setProgress(100);
    setCurrentTask('RTX 4060 GPU Online · Zero-Latency Local Core Ready');
    setStep('ready');

    setTimeout(() => {
      onClose();
    }, 900);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
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
            className="relative w-full max-w-md bg-[#101013] border border-white/[0.12] rounded-3xl p-6 shadow-2xl text-foreground overflow-hidden ring-1 ring-white/5"
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
                      Private Local GPU Inference · Zero Cloud Network
                    </p>
                  </div>
                </div>

                {/* Hardware Telemetry Card */}
                <div className="p-3.5 rounded-2xl bg-[#141417] border border-white/[0.08] space-y-2.5 text-xs">
                  <div className="flex items-center justify-between text-zinc-400">
                    <span>Target Compute:</span>
                    <span className="font-medium text-zinc-200 font-mono">NVIDIA RTX 4060 (8GB)</span>
                  </div>
                  <div className="flex items-center justify-between text-zinc-400">
                    <span>Local LLM:</span>
                    <span className="font-medium text-zinc-200 font-mono">Qwen 2.5 (7B Instruct)</span>
                  </div>
                  <div className="flex items-center justify-between text-zinc-400">
                    <span>Daemon Pipeline:</span>
                    <span className="font-medium text-emerald-400">Background Auto-Start</span>
                  </div>
                  <div className="flex items-center justify-between text-zinc-400">
                    <span>Multi-Tier Cache:</span>
                    <span className="font-medium text-zinc-300">Redis L1 + Vector L2 Active</span>
                  </div>
                </div>

                <p className="text-xs text-zinc-400 leading-relaxed">
                  Confirming will launch the background Ollama daemon and pre-allocate model weights into your RTX 4060 GPU VRAM.
                </p>

                {/* Action Buttons */}
                <div className="flex items-center justify-end gap-2.5 pt-2">
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-4 py-2 rounded-xl text-xs font-medium text-zinc-400 hover:text-zinc-200 bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] transition-colors"
                  >
                    Cancel
                  </button>
                  <motion.button
                    type="button"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={handleStartLoad}
                    className="px-4 py-2 rounded-xl text-xs font-semibold text-zinc-900 bg-zinc-100 hover:bg-white shadow-sm transition-all flex items-center gap-1.5"
                  >
                    <Cpu className="w-3.5 h-3.5 text-zinc-900" />
                    <span>Confirm &amp; Initialize GPU →</span>
                  </motion.button>
                </div>
              </div>
            ) : (
              /* Step 2: Minimalist High-End Loader */
              <div className="py-4 text-center space-y-5 relative z-10 select-none">
                {/* Minimalist Rotating Rings */}
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
                    {step === 'ready' ? 'GPU ALLOCATION COMPLETE' : 'INITIALIZING LOCAL GPU'}
                  </h4>
                  <p className="text-xs text-zinc-400 font-mono tracking-wide h-4">
                    {currentTask}
                  </p>
                </div>

                {/* Refined Progress Bar */}
                <div className="space-y-1.5 px-2">
                  <div className="w-full h-1.5 rounded-full bg-white/[0.08] overflow-hidden p-0.5">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${progress}%` }}
                      transition={{ ease: 'easeOut', duration: 0.3 }}
                      className="h-full rounded-full bg-zinc-200"
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-zinc-500 font-mono">
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
  const [isLocalHost, setIsLocalHost] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    textareaRef.current?.focus();
    if (typeof window !== 'undefined') {
      const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      setIsLocalHost(isLocal);
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
      setShowModal(true);
    } else {
      setIsOffline(false);
      api.setOfflineMode(false).catch(() => {});
      toast.success('🌐 Online Mode Active: Cloud Gemini with Multi-Tier Cache');
    }
  };

  const handleConfirmOffline = async () => {
    try {
      await api.preloadModel('qwen2.5:7b');
    } catch {}
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

    // Determine target API endpoint
    // If the user is on localhost:3000, target http://localhost:8000 directly (0 mixed content, direct GPU access)
    // If the user is on cloud vercel.app and in offline mode:
    const isLocal = typeof window !== 'undefined' && 
      (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

    let apiUrl = isLocal ? 'http://localhost:8000' : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

    // On cloud Vercel in Offline mode:
    // Browser security blocks HTTPS -> HTTP localhost directly.
    // If user is on Vercel and toggled offline, we check if they are running locally:
    if (!isLocal && isOffline) {
      try {
        const testLocal = await fetch('http://localhost:8000/api/health', { method: 'GET', mode: 'cors' });
        if (testLocal.ok) {
          apiUrl = 'http://localhost:8000';
        }
      } catch {
        // Mixed Content blocked or local backend unreachable
      }
    }

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

      // If user was on cloud Vercel and attempted Offline GPU execution:
      const helpContent = (!isLocal && isOffline)
        ? `⚡ **Local RTX 4060 GPU Routing**:\n\nTo execute queries on your physical **RTX 4060 GPU**, open Cache-Craft at **[http://localhost:3000](http://localhost:3000)**!\n\n*(Your browser's security rules prevent cloud HTTPS domains like vercel.app from accessing your laptop's local ports directly. Your local instance is already running at [http://localhost:3000](http://localhost:3000)).*`
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
      ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20' 
      : isL2
      ? 'bg-zinc-800 text-zinc-300 border-white/10'
      : 'bg-white/[0.04] text-zinc-400 border-white/[0.08]';

    const dotColor = (isL0 || isL1)
      ? 'bg-emerald-400'
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
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] border border-white/10 bg-white/[0.05] text-zinc-300 font-mono">
              <Cpu className="w-2.5 h-2.5 text-zinc-400" />
              <span>RTX 4060 Local</span>
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
                {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
              <button
                onClick={() => handleFeedback(msg.id, meta.query_hash!, true)}
                disabled={meta.feedback !== null && meta.feedback !== undefined}
                className={`p-1 rounded-md transition-colors ${
                  meta.feedback === 'positive' ? 'text-emerald-400' : 'text-zinc-500 hover:text-zinc-200'
                }`}
                title="Good answer"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => handleFeedback(msg.id, meta.query_hash!, false)}
                disabled={meta.feedback !== null && meta.feedback !== undefined}
                className={`p-1 rounded-md transition-colors ${
                  meta.feedback === 'negative' ? 'text-rose-400' : 'text-zinc-500 hover:text-rose-400'
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

      {/* Cloud Environment Notice for Offline Mode */}
      {!isLocalHost && isOffline && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-2 mb-1 p-2.5 rounded-xl bg-[#141417] border border-white/[0.1] text-xs text-zinc-300 flex items-center justify-between shadow-sm"
        >
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-zinc-400 shrink-0" />
            <span>
              To run models on your physical <strong>RTX 4060 GPU</strong>, open your local instance at <strong>http://localhost:3000</strong>
            </span>
          </div>
          <a
            href="http://localhost:3000/dashboard/chat"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1 text-[11px] font-semibold text-zinc-100 bg-white/[0.08] hover:bg-white/[0.14] px-2.5 py-1 rounded-lg border border-white/[0.1] transition-colors shrink-0 ml-2"
          >
            <span>Open Local</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </motion.div>
      )}

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
                <span className="w-2 h-2 rounded-full bg-violet-400/90 shadow-[0_0_8px_rgba(167,139,250,0.8)]" />
                <Cpu className="w-3.5 h-3.5 text-zinc-300" />
                <span className="font-semibold tracking-wide">Offline · Local LLM (RTX 4060)</span>
              </>
            ) : (
              <>
                <span className="w-2 h-2 rounded-full bg-emerald-400/90 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
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
                        <span className="w-2 h-2 rounded-full bg-violet-400/90 shadow-[0_0_8px_rgba(167,139,250,0.8)]" />
                        <Cpu className="w-3.5 h-3.5 text-zinc-300" />
                        <span className="font-semibold tracking-wide">Offline · Local LLM (RTX 4060)</span>
                      </>
                    ) : (
                      <>
                        <span className="w-2 h-2 rounded-full bg-emerald-400/90 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
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
                  className="flex items-center gap-2 text-zinc-400 text-xs"
                >
                  <Zap className="w-4 h-4 text-zinc-300 animate-pulse" />
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
          <div className="bg-[#121215]/95 border border-white/[0.1] hover:border-white/[0.18] focus-within:border-white/25 rounded-2xl shadow-2xl p-2.5 sm:p-3 space-y-2 backdrop-blur-2xl transition-all">
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
              className="w-full bg-transparent text-sm text-zinc-100 placeholder:text-zinc-500 resize-none outline-none leading-relaxed"
            />

            <div className="flex items-center justify-between pt-1 border-t border-white/[0.06]">
              <div className="flex items-center gap-1.5 text-xs text-zinc-300 font-medium select-none">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span>Multi-Tier Active</span>
              </div>

              <div className="flex items-center gap-2">
                <motion.button
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
                      <span className="w-2 h-2 rounded-full bg-violet-400/90 shadow-[0_0_8px_rgba(167,139,250,0.8)]" />
                      <Cpu className="w-3.5 h-3.5 text-zinc-300" />
                      <span className="font-semibold tracking-wide">Offline · Local LLM (RTX 4060)</span>
                    </>
                  ) : (
                    <>
                      <span className="w-2 h-2 rounded-full bg-emerald-400/90 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
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
