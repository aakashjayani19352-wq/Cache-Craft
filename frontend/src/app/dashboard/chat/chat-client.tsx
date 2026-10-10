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
  ChevronDown,
  Layers,
  Cpu,
  Globe
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { api, type ModelOption } from '@/lib/api';

// Cache-Craft's signature isometric neural cache emblem (100% bespoke, zero Claude iconography)
function CacheCraftEmblem({ className = "w-12 h-12" }: { className?: string }) {
  return (
    <div className={`relative flex items-center justify-center shrink-0 ${className}`}>
      {/* High-refresh ambient radiant aura */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-amber-500/25 via-orange-500/20 to-amber-600/10 blur-xl animate-pulse" />
      <div className="relative w-full h-full rounded-2xl bg-gradient-to-b from-[#24211a] via-[#1a1813] to-[#12110e] border border-amber-500/35 flex items-center justify-center shadow-[0_8px_30px_rgba(245,158,11,0.18)] ring-1 ring-white/10 will-change-transform">
        <svg 
          viewBox="0 0 24 24" 
          className="w-6 h-6 text-amber-400 drop-shadow-[0_0_10px_rgba(245,158,11,0.7)]" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2.2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          {/* Multi-tier layered cache prism */}
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
          <path d="M2 12l10 5 10-5" />
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

// Ultra-smooth 165Hz-grade Functional Model Selector Popover
function ModelSelectorMenu({
  selectedModel,
  onSelectModel,
  align = 'right'
}: {
  selectedModel: string;
  onSelectModel: (id: string) => void;
  availableModels: ModelOption[];
  align?: 'left' | 'right';
}) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  // Catalog of functional models with clear architecture badges
  const models = [
    {
      id: 'gemini-3.8-flash',
      title: 'Gemini 3.8 Flash',
      subtitle: 'Primary high-speed cloud LLM with instant vector caching',
      tag: 'Cloud Primary',
      tagColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/25',
      icon: Globe
    },
    {
      id: 'auto',
      title: 'Auto-Router',
      subtitle: 'Dynamic prompt intent & complexity classifier (Qwen / Llama)',
      tag: 'Smart Hybrid',
      tagColor: 'text-amber-400 bg-amber-500/10 border-amber-500/25',
      icon: Sparkles
    },
    {
      id: 'qwen2.5:7b',
      title: 'Qwen 2.5 7B',
      subtitle: 'Deep reasoning, math & code on local RTX 4060 GPU',
      tag: 'Local 7B',
      tagColor: 'text-blue-400 bg-blue-500/10 border-blue-500/25',
      icon: Cpu
    },
    {
      id: 'llama3.2',
      title: 'Llama 3.2 3B',
      subtitle: 'Ultra-fast low-latency local conversational engine',
      tag: 'Local 3B',
      tagColor: 'text-purple-400 bg-purple-500/10 border-purple-500/25',
      icon: Zap
    }
  ];

  const currentModel = models.find((m) => m.id === selectedModel) || {
    id: selectedModel,
    title: selectedModel.replace('Google ', '').replace(' (Cloud)', ''),
    subtitle: 'Selected inference model',
    tag: 'Active',
    tagColor: 'text-amber-400 bg-amber-500/10 border-amber-500/25',
    icon: Layers
  };

  return (
    <div className="relative inline-block" ref={menuRef}>
      {/* 165Hz Hardware-Accelerated Trigger Button */}
      <motion.button
        type="button"
        whileHover={{ scale: 1.02, y: -1 }}
        whileTap={{ scale: 0.97 }}
        transition={{ type: 'spring', stiffness: 450, damping: 25 }}
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#22201b]/90 hover:bg-[#2c2a23] border border-white/[0.08] hover:border-amber-500/35 text-foreground text-xs font-medium transition-all shadow-xs select-none backdrop-blur-md will-change-transform"
      >
        <span className="text-foreground/95 font-medium">{currentModel.title}</span>
        <ChevronDown className={`w-3.5 h-3.5 text-muted-foreground/70 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </motion.button>

      {/* Floating Popover Card */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 6, scale: 0.97 }}
            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
            className={`absolute bottom-full mb-2 ${
              align === 'right' ? 'right-0' : 'left-0'
            } w-[300px] sm:w-[330px] rounded-2xl bg-[#1b1a16]/95 border border-white/[0.1] shadow-2xl p-2 space-y-1.5 z-50 text-foreground select-none backdrop-blur-2xl will-change-transform ring-1 ring-white/5`}
          >
            <div className="px-2.5 py-1.5 flex items-center justify-between border-b border-white/[0.06]">
              <span className="text-[11px] font-semibold text-muted-foreground tracking-wider uppercase">
                Inference Routing Engine
              </span>
              <span className="text-[10px] text-amber-400 font-mono">
                L1 + L2 Active
              </span>
            </div>

            {/* List of 100% Functional Models */}
            <div className="space-y-1 pt-1">
              {models.map((model) => {
                const isSelected = selectedModel === model.id;
                const IconComponent = model.icon;
                return (
                  <motion.div
                    key={model.id}
                    whileHover={{ scale: 1.01, x: 2 }}
                    whileTap={{ scale: 0.98 }}
                    transition={{ type: 'spring', stiffness: 450, damping: 25 }}
                    onClick={() => {
                      onSelectModel(model.id);
                      setIsOpen(false);
                    }}
                    className={`p-2.5 rounded-xl cursor-pointer flex items-start justify-between transition-colors ${
                      isSelected 
                        ? 'bg-[#27241e] border border-amber-500/30 shadow-xs' 
                        : 'hover:bg-[#24221c] border border-transparent'
                    }`}
                  >
                    <div className="flex items-start gap-2.5 pr-2">
                      <div className={`mt-0.5 p-1.5 rounded-lg ${isSelected ? 'bg-amber-500/20 text-amber-400' : 'bg-white/5 text-muted-foreground'}`}>
                        <IconComponent className="w-3.5 h-3.5" />
                      </div>
                      <div className="space-y-0.5">
                        <div className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                          <span>{model.title}</span>
                          <span className={`text-[9px] px-1.5 py-0.2 rounded-full border font-normal ${model.tagColor}`}>
                            {model.tag}
                          </span>
                        </div>
                        <p className="text-[11px] text-muted-foreground/75 leading-relaxed font-normal">
                          {model.subtitle}
                        </p>
                      </div>
                    </div>

                    {isSelected && (
                      <div className="text-amber-400 mt-1 shrink-0 drop-shadow-[0_0_6px_rgba(245,158,11,0.6)]">
                        <Check className="w-4 h-4" />
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>

            <div className="border-t border-white/[0.06] pt-2 px-2 pb-1 text-[11px] text-muted-foreground/60 leading-relaxed font-normal">
              <span>All requests automatically query Redis L1 and pgvector L2 before reaching inference.</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function ChatClient() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('gemini-3.8-flash');
  const [availableModels, setAvailableModels] = useState<ModelOption[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    textareaRef.current?.focus();
    api.settings().then((s) => {
      if (s.available_models) {
        setAvailableModels(s.available_models);
        const validIds = s.available_models.map((m) => m.id);
        if (s.active_model && validIds.includes(s.active_model)) {
          setSelectedModel(s.active_model);
        } else {
          setSelectedModel('gemini-3.8-flash');
        }
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

  const handleModelChange = (modelId: string) => {
    setSelectedModel(modelId);
    api.setModel(modelId).catch(() => {});
    const modelObj = availableModels.find((m) => m.id === modelId);
    toast.success(`Active engine: ${modelObj?.name || modelId}`);
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

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    try {
      const res = await fetch(`${apiUrl}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: trimmed,
          messages: history.slice(-20),
          model: selectedModel,
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
    toast.info('Started fresh conversation');
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
      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25' 
      : isL2
      ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
      : 'bg-white/[0.04] text-muted-foreground border-white/[0.08]';

    const dotColor = (isL0 || isL1)
      ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]'
      : isL2
      ? 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.8)]'
      : 'bg-muted-foreground/60';

    const Icon = (isL0 || isL1) ? Zap : isL2 ? Database : Server;

    const label = isL0
      ? 'L0 Exact Hit (Memory)'
      : isL1 
      ? 'L1 Cache Hit (Redis)' 
      : isL2
      ? `L2 Semantic Hit (${(meta.similarity! * 100).toFixed(1)}%)`
      : 'Cache Miss · LLM Generated';

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

          {meta.routed_model && meta.hit_type === 'CACHE_MISS' && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] border border-purple-500/30 bg-purple-500/10 text-purple-400">
              <Sparkles className="w-2.5 h-2.5 mr-0.5" />
              <span>Routed: {meta.routed_model}</span>
            </span>
          )}

          {meta.query_hash && (
            <div className="flex items-center gap-1 ml-auto">
              <button
                onClick={() => handleCopy(msg.id, msg.content)}
                className="p-1 rounded-md text-muted-foreground/60 hover:text-foreground transition-colors"
                title="Copy response"
              >
                {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
              <button
                onClick={() => handleFeedback(msg.id, meta.query_hash!, true)}
                disabled={meta.feedback !== null && meta.feedback !== undefined}
                className={`p-1 rounded-md transition-colors ${
                  meta.feedback === 'positive' ? 'text-emerald-500' : 'text-muted-foreground/60 hover:text-emerald-500'
                }`}
                title="Good answer"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => handleFeedback(msg.id, meta.query_hash!, false)}
                disabled={meta.feedback !== null && meta.feedback !== undefined}
                className={`p-1 rounded-md transition-colors ${
                  meta.feedback === 'negative' ? 'text-red-500' : 'text-muted-foreground/60 hover:text-red-500'
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
      {/* Top Header Toolbar (active chat) */}
      {!isChatEmpty && (
        <div className="flex items-center justify-between py-3 border-b border-white/[0.08] shrink-0">
          <motion.button
            type="button"
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.96 }}
            onClick={handleResetChat}
            className="h-8 px-3 text-xs text-muted-foreground hover:text-foreground rounded-lg flex items-center gap-1.5 transition-colors border border-white/[0.06] hover:border-white/[0.12] bg-[#1e1d1a]"
          >
            <RotateCcw className="w-3 h-3 text-amber-400" />
            <span>New Session</span>
          </motion.button>

          <ModelSelectorMenu
            selectedModel={selectedModel}
            onSelectModel={handleModelChange}
            availableModels={availableModels}
            align="right"
          />
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto min-h-0 py-4 space-y-6">
        {isChatEmpty ? (
          /* Cache-Craft Signature Neural Hero (165Hz Optimized) */
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
                <h1 className="text-2xl sm:text-3xl text-foreground font-semibold tracking-tight bg-gradient-to-r from-foreground via-foreground/95 to-foreground/80 bg-clip-text">
                  Accelerate your intelligence.
                </h1>
                <p className="text-xs text-muted-foreground/75 font-normal tracking-wide mt-0.5">
                  Autonomous Multi-Tier Semantic Cache · Redis L1 · pgvector L2 · Gemini Cloud
                </p>
              </div>
            </motion.div>

            {/* Floating Glassmorphic Prompt Card */}
            <motion.div
              initial={{ y: 16, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ type: 'spring', stiffness: 380, damping: 26, delay: 0.05 }}
              className="w-full max-w-2xl bg-[#171612]/95 border border-white/[0.1] hover:border-amber-500/35 focus-within:border-amber-500/50 focus-within:shadow-[0_0_35px_rgba(245,158,11,0.14)] rounded-[22px] shadow-2xl p-3.5 sm:p-4.5 space-y-3 transition-all duration-300 backdrop-blur-2xl will-change-transform ring-1 ring-white/5"
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
                placeholder="Ask anything or test semantic cache recall..."
                className="w-full bg-transparent text-sm sm:text-base text-foreground placeholder:text-muted-foreground/45 resize-none outline-none leading-relaxed font-normal"
              />

              {/* Functional Controls Toolbar (Zero Mock/Dummy Icons) */}
              <div className="flex items-center justify-between pt-2 border-t border-white/[0.06]">
                {/* Active Cache Engine Indicator */}
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/25 text-amber-400 text-xs font-medium select-none">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 shadow-[0_0_8px_rgba(245,158,11,0.9)] animate-pulse" />
                  <span>Cache-Craft Active</span>
                </div>

                {/* Right Controls: Model Selector & Functional Send Button */}
                <div className="flex items-center gap-2">
                  <ModelSelectorMenu
                    selectedModel={selectedModel}
                    onSelectModel={handleModelChange}
                    availableModels={availableModels}
                    align="right"
                  />

                  <motion.button
                    whileHover={{ scale: 1.06 }}
                    whileTap={{ scale: 0.92 }}
                    transition={{ type: 'spring', stiffness: 450, damping: 20 }}
                    onClick={() => sendQuery(input)}
                    disabled={!input.trim() || isLoading}
                    className="h-8 w-8 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-white flex items-center justify-center transition-all disabled:opacity-30 disabled:pointer-events-none shadow-md shadow-amber-500/25 active:scale-95 will-change-transform"
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
                  className="text-xs text-muted-foreground/80 hover:text-foreground bg-[#1d1b16]/80 hover:bg-[#26241d] border border-white/[0.06] hover:border-amber-500/35 rounded-full px-3.5 py-1.5 transition-all text-left shadow-xs backdrop-blur-md will-change-transform"
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
                      <div className="bg-[#2a2721] text-foreground text-sm sm:text-base rounded-2xl rounded-tr-sm px-4 py-2.5 max-w-[85%] whitespace-pre-wrap leading-relaxed border border-white/[0.08] shadow-sm">
                        {msg.content}
                      </div>
                    ) : (
                      <div className="w-full space-y-2">
                        <div className="flex items-center gap-2 mb-1">
                          <Zap className="w-3.5 h-3.5 text-amber-400" />
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
                  <Zap className="w-4 h-4 text-amber-400 animate-pulse" />
                  <span className="font-medium tracking-wide">Routing through multi-tier cache...</span>
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
          <div className="bg-[#171612]/95 border border-white/[0.1] hover:border-amber-500/35 focus-within:border-amber-500/50 rounded-2xl shadow-2xl p-2.5 sm:p-3 space-y-2 backdrop-blur-2xl transition-all ring-1 ring-white/5">
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
              <div className="flex items-center gap-1.5 text-xs text-amber-400/90 font-medium select-none">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 shadow-[0_0_6px_rgba(245,158,11,0.8)]" />
                <span>Multi-Tier Active</span>
              </div>

              <div className="flex items-center gap-2">
                <ModelSelectorMenu
                  selectedModel={selectedModel}
                  onSelectModel={handleModelChange}
                  availableModels={availableModels}
                  align="right"
                />

                <motion.button
                  whileHover={{ scale: 1.06 }}
                  whileTap={{ scale: 0.92 }}
                  transition={{ type: 'spring', stiffness: 450, damping: 20 }}
                  onClick={() => sendQuery(input)}
                  disabled={!input.trim() || isLoading}
                  className="h-7 w-7 rounded-lg bg-gradient-to-tr from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-white flex items-center justify-center transition-all disabled:opacity-30 disabled:pointer-events-none shadow-md shadow-amber-500/25 active:scale-95 will-change-transform"
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
