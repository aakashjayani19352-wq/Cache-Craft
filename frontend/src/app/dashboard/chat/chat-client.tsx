'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { 
  Send, 
  Bot, 
  User, 
  Zap, 
  Database, 
  Server, 
  Copy, 
  Check, 
  Plus,
  Sparkles,
  ArrowRight,
  ArrowUp,
  ThumbsUp,
  ThumbsDown,
  Wifi,
  WifiOff,
  AlertTriangle,
  RotateCcw,
  SlidersHorizontal,
  ChevronRight,
  ChevronDown,
  ExternalLink
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { api, type ModelOption } from '@/lib/api';

// Claude signature terracotta asterisk/starburst icon
function ClaudeStar({ className = "w-9 h-9" }: { className?: string }) {
  return (
    <svg 
      className={className} 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2.2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    >
      <line x1="12" y1="2" x2="12" y2="22" />
      <line x1="2" y1="12" x2="22" y2="12" />
      <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
      <line x1="19.07" y1="4.93" x2="4.93" y2="19.07" />
    </svg>
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

// Claude-grade Model Selector Popover Component
function ClaudeModelMenu({
  selectedModel,
  onSelectModel,
  availableModels,
  align = 'right'
}: {
  selectedModel: string;
  onSelectModel: (id: string) => void;
  availableModels: ModelOption[];
  align?: 'left' | 'right';
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [showMore, setShowMore] = useState(false);
  const [effort, setEffort] = useState<'Fast' | 'Medium' | 'Deep'>('Medium');
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setShowMore(false);
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  // Model details mapping
  const modelMeta: Record<string, { title: string; subtitle: string; tag: string }> = {
    'gemini-3.8-flash': {
      title: 'Gemini 3.8 Flash',
      subtitle: 'Most efficient for simpler tasks & real-time cache',
      tag: 'Cloud'
    },
    'auto': {
      title: 'Auto-Router',
      subtitle: 'Prompt-aware dynamic routing (Qwen 7B / Llama 3B)',
      tag: 'Smart'
    },
    'qwen2.5:7b': {
      title: 'Qwen 2.5 7B',
      subtitle: 'Flagship reasoning, math & code on local GPU',
      tag: 'Local'
    },
    'llama3.2': {
      title: 'Llama 3.2 3B',
      subtitle: 'Ultra-fast low-latency conversational model',
      tag: 'Local'
    }
  };

  const currentMeta = modelMeta[selectedModel] || {
    title: selectedModel.replace('Google ', '').replace(' (Cloud)', ''),
    subtitle: 'Selected inference model',
    tag: 'Active'
  };

  const primaryModelId = 'gemini-3.8-flash';
  const primaryMeta = modelMeta[primaryModelId];

  return (
    <div className="relative inline-block" ref={menuRef}>
      {/* Claude Style Trigger Pill */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#272622] hover:bg-[#302e29] border border-[#3d3b34] text-foreground text-xs font-medium transition-all shadow-xs active:scale-98 select-none"
      >
        <span className="text-foreground/95 font-medium">{currentMeta.title}</span>
        <span className="text-muted-foreground/70 font-normal">{effort}</span>
      </button>

      {/* Claude Style Popover Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 6, scale: 0.98 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className={`absolute bottom-full mb-2 ${
              align === 'right' ? 'right-0' : 'left-0'
            } w-[285px] sm:w-[310px] rounded-2xl bg-[#1e1d1a] border border-[#383630] shadow-2xl p-1.5 space-y-1 z-50 text-foreground select-none backdrop-blur-2xl`}
          >
            {/* Primary Model Item */}
            <div
              onClick={() => {
                onSelectModel(primaryModelId);
                setIsOpen(false);
                setShowMore(false);
              }}
              className="p-2.5 rounded-xl hover:bg-[#2b2924] transition-colors cursor-pointer flex items-start justify-between group"
            >
              <div className="space-y-0.5 pr-2">
                <div className="text-sm font-medium text-foreground flex items-center gap-1.5">
                  <span>{primaryMeta.title}</span>
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-normal">
                    {primaryMeta.tag}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground/80 leading-relaxed font-normal">
                  {primaryMeta.subtitle}
                </p>
              </div>

              {selectedModel === primaryModelId && (
                <div className="text-blue-500 mt-1 shrink-0">
                  <Check className="w-4 h-4" />
                </div>
              )}
            </div>

            {/* Effort Row */}
            <div 
              onClick={() => {
                const next = effort === 'Fast' ? 'Medium' : effort === 'Medium' ? 'Deep' : 'Fast';
                setEffort(next);
                toast.info(`Effort set to ${next}`);
              }}
              className="px-2.5 py-2 rounded-xl hover:bg-[#2b2924] transition-colors cursor-pointer flex items-center justify-between text-xs text-foreground/90 font-medium"
            >
              <span>Effort</span>
              <div className="flex items-center gap-1 text-muted-foreground hover:text-foreground">
                <span>{effort}</span>
                <ChevronRight className="w-3.5 h-3.5 opacity-60" />
              </div>
            </div>

            {/* More Models Accordion */}
            <div className="space-y-1">
              <div
                onClick={() => setShowMore(!showMore)}
                className="px-2.5 py-2 rounded-xl hover:bg-[#2b2924] transition-colors cursor-pointer flex items-center justify-between text-xs text-foreground/90 font-medium"
              >
                <span>More models</span>
                <ChevronRight className={`w-3.5 h-3.5 text-muted-foreground transition-transform duration-200 ${showMore ? 'rotate-90' : ''}`} />
              </div>

              {showMore && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-0.5 pt-0.5 pl-1"
                >
                  {/* Auto Router */}
                  <div
                    onClick={() => {
                      onSelectModel('auto');
                      setIsOpen(false);
                    }}
                    className="p-2 rounded-lg hover:bg-[#2b2924] transition-colors cursor-pointer flex items-start justify-between"
                  >
                    <div>
                      <div className="text-xs font-medium text-foreground flex items-center gap-1">
                        <span>✨ Auto-Router (Prompt-Aware)</span>
                      </div>
                      <p className="text-[11px] text-muted-foreground/70">
                        Dynamic prompt-aware complexity routing
                      </p>
                    </div>
                    {selectedModel === 'auto' && <Check className="w-3.5 h-3.5 text-blue-500 mt-0.5" />}
                  </div>

                  {/* Qwen 7B */}
                  <div
                    onClick={() => {
                      onSelectModel('qwen2.5:7b');
                      setIsOpen(false);
                    }}
                    className="p-2 rounded-lg hover:bg-[#2b2924] transition-colors cursor-pointer flex items-start justify-between"
                  >
                    <div>
                      <div className="text-xs font-medium text-foreground">
                        💻 Qwen 2.5 7B (Local)
                      </div>
                      <p className="text-[11px] text-muted-foreground/70">
                        State-of-the-art coding &amp; math on RTX 4060
                      </p>
                    </div>
                    {selectedModel === 'qwen2.5:7b' && <Check className="w-3.5 h-3.5 text-blue-500 mt-0.5" />}
                  </div>

                  {/* Llama 3.2 3B */}
                  <div
                    onClick={() => {
                      onSelectModel('llama3.2');
                      setIsOpen(false);
                    }}
                    className="p-2 rounded-lg hover:bg-[#2b2924] transition-colors cursor-pointer flex items-start justify-between"
                  >
                    <div>
                      <div className="text-xs font-medium text-foreground">
                        ⚡ Llama 3.2 3B (Local)
                      </div>
                      <p className="text-[11px] text-muted-foreground/70">
                        Ultra-fast local chat &amp; greetings
                      </p>
                    </div>
                    {selectedModel === 'llama3.2' && <Check className="w-3.5 h-3.5 text-blue-500 mt-0.5" />}
                  </div>
                </motion.div>
              )}
            </div>

            {/* Subtle Divider */}
            <div className="border-t border-[#312f29] my-1" />

            {/* Bottom Claude-style footer info */}
            <div className="px-2.5 py-1.5 text-[11px] text-muted-foreground/60 leading-relaxed">
              <span>Cache-Craft multi-tier caching (Redis L1 &amp; pgvector L2) operates automatically across all selected models. </span>
              <span className="underline hover:text-muted-foreground cursor-pointer">Learn more</span>
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
  const [offlineMode, setOfflineMode] = useState(false);
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
      if (s.offline_mode) setOfflineMode(true);
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
    toast.success(`Active model: ${modelObj?.name || modelId}`);
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
          offline_mode: offlineMode,
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
      ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20' 
      : isL2
      ? 'bg-[#d97757]/10 text-[#d97757] border-[#d97757]/30'
      : 'bg-muted text-muted-foreground border-border/40';

    const dotColor = (isL0 || isL1)
      ? 'bg-emerald-500'
      : isL2
      ? 'bg-[#d97757]'
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
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] border border-purple-500/30 bg-purple-500/10 text-purple-600 dark:text-purple-400">
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
      {/* Top Header Toolbar (when in active chat) */}
      {!isChatEmpty && (
        <div className="flex items-center justify-between py-3 border-b border-border/40 shrink-0">
          <button
            type="button"
            onClick={handleResetChat}
            className="h-8 px-2.5 text-xs text-muted-foreground hover:text-foreground rounded-lg flex items-center gap-1.5 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            New chat
          </button>

          {/* Claude Model Selector Dropdown */}
          <ClaudeModelMenu
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
          /* Claude Welcoming Centered Hero */
          <div className="h-full flex flex-col items-center justify-center -mt-8 space-y-6 select-none">
            {/* Claude Terracotta Starburst */}
            <motion.div
              initial={{ scale: 0.85, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.4, ease: 'easeOut' }}
              className="flex items-center gap-3"
            >
              <div className="text-[#d97757]">
                <ClaudeStar className="w-10 h-10" />
              </div>
              <h1 className="font-serif text-3xl sm:text-4xl text-foreground font-normal tracking-tight">
                What shall we think through?
              </h1>
            </motion.div>

            {/* Claude-Style Floating Input Card */}
            <motion.div
              initial={{ y: 15, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="w-full max-w-2xl bg-card dark:bg-[#201f1c] border border-border/70 dark:border-[#34322d] rounded-2xl shadow-lg p-3 sm:p-4 space-y-3"
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
                placeholder="How can I help you today?"
                className="w-full bg-transparent text-sm sm:text-base text-foreground placeholder:text-muted-foreground/50 resize-none outline-none leading-relaxed"
              />

              {/* Bottom Card Toolbar */}
              <div className="flex items-center justify-between pt-1 border-t border-border/30">
                <div className="flex items-center gap-2">
                  <button 
                    type="button"
                    className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
                    title="Add context"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                  <span className="text-xs text-muted-foreground font-medium px-2 py-0.5 rounded-md bg-secondary/50">
                    ⚡ Cache-Craft Active
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  {/* Claude Model Selector Popover */}
                  <ClaudeModelMenu
                    selectedModel={selectedModel}
                    onSelectModel={handleModelChange}
                    availableModels={availableModels}
                    align="right"
                  />

                  {/* Send Button */}
                  <button
                    onClick={() => sendQuery(input)}
                    disabled={!input.trim() || isLoading}
                    className="h-8 w-8 rounded-lg bg-[#d97757] hover:bg-[#c86b4c] text-white flex items-center justify-center transition-all disabled:opacity-30 disabled:pointer-events-none active:scale-95 shadow-sm"
                    title="Send query"
                  >
                    <ArrowUp className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>

            {/* Suggestions below */}
            <div className="w-full max-w-2xl flex flex-wrap gap-2 justify-center pt-2">
              {SUGGESTIONS.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => sendQuery(item)}
                  className="text-xs text-muted-foreground hover:text-foreground bg-secondary/40 hover:bg-secondary/70 border border-border/40 rounded-full px-3.5 py-1.5 transition-all text-left"
                >
                  {item}
                </button>
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
                    transition={{ duration: 0.25 }}
                    className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
                  >
                    {isUser ? (
                      <div className="bg-secondary/80 text-foreground text-sm sm:text-base rounded-2xl rounded-tr-sm px-4 py-2.5 max-w-[85%] whitespace-pre-wrap leading-relaxed">
                        {msg.content}
                      </div>
                    ) : (
                      <div className="w-full space-y-2">
                        <div className="flex items-center gap-2 mb-1">
                          <div className="text-[#d97757]">
                            <ClaudeStar className="w-4 h-4" />
                          </div>
                          <span className="text-xs font-semibold text-foreground/80">Cache-Craft</span>
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
                  <div className="text-[#d97757] animate-spin">
                    <ClaudeStar className="w-4 h-4" />
                  </div>
                  <span>Thinking &amp; routing through cache...</span>
                </motion.div>
              )}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Docked Claude Floating Input (when chat has messages) */}
      {!isChatEmpty && (
        <div className="absolute bottom-4 left-4 right-4 max-w-3xl mx-auto">
          <div className="bg-card dark:bg-[#201f1c] border border-border/70 dark:border-[#34322d] rounded-2xl shadow-xl p-2.5 sm:p-3 space-y-2 backdrop-blur-xl">
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
              placeholder="Reply to Cache-Craft..."
              className="w-full bg-transparent text-sm text-foreground placeholder:text-muted-foreground/50 resize-none outline-none leading-relaxed"
            />

            <div className="flex items-center justify-between pt-1 border-t border-border/30">
              <div className="flex items-center gap-1.5">
                <span className="text-[11px] text-muted-foreground">
                  ⚡ Multi-Tier Cache Active
                </span>
              </div>

              <div className="flex items-center gap-2">
                {/* Claude Model Selector Popover */}
                <ClaudeModelMenu
                  selectedModel={selectedModel}
                  onSelectModel={handleModelChange}
                  availableModels={availableModels}
                  align="right"
                />

                <button
                  onClick={() => sendQuery(input)}
                  disabled={!input.trim() || isLoading}
                  className="h-7 w-7 rounded-lg bg-[#d97757] hover:bg-[#c86b4c] text-white flex items-center justify-center transition-all disabled:opacity-30 disabled:pointer-events-none active:scale-95 shadow-sm"
                  title="Send message"
                >
                  <ArrowUp className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
