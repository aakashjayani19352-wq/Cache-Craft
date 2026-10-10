'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
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
  ChevronDown
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

export default function ChatClient() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [offlineMode, setOfflineMode] = useState(false);
  const [selectedModel, setSelectedModel] = useState<string>('auto');
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
          setSelectedModel('auto');
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

  const handleToggleOfflineMode = () => {
    const next = !offlineMode;
    setOfflineMode(next);
    api.setOfflineMode(next).catch(() => {});
    toast.info(next ? 'Switched to Offline Mode (100% Local LLM)' : 'Switched to Cloud Mode (Gemini Active)');
  };

  const handleModelChange = (modelId: string) => {
    setSelectedModel(modelId);
    api.setModel(modelId).catch(() => {});
    const modelObj = availableModels.find((m) => m.id === modelId);
    toast.success(`Model switched: ${modelObj?.name || modelId}`);
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

  const activeModelObj = availableModels.find((m) => m.id === selectedModel);
  const activeModelDisplay = selectedModel === 'auto' 
    ? 'Auto-Router' 
    : (activeModelObj?.name?.replace('Google ', '')?.replace(' (Cloud)', '') || selectedModel);

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
          <Badge variant="outline" className={`flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium border ${pillStyle}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
            <Icon className="w-3 h-3" />
            {label}
          </Badge>

          <span className="text-[11px] text-muted-foreground font-mono flex items-center gap-1">
            ⚡ {meta.latency !== undefined ? `${meta.latency.toFixed(1)}ms` : '—'}
          </span>

          {meta.routed_model && meta.hit_type === 'CACHE_MISS' && (
            <Badge variant="outline" className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] border border-purple-500/30 bg-purple-500/10 text-purple-600 dark:text-purple-400">
              <Sparkles className="w-2.5 h-2.5 mr-0.5" />
              <span>Routed: {meta.routed_model}</span>
            </Badge>
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
      {/* Top Header Toolbar */}
      {!isChatEmpty && (
        <div className="flex items-center justify-between py-3 border-b border-border/40 shrink-0">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleResetChat}
            className="h-8 px-2.5 text-xs text-muted-foreground hover:text-foreground rounded-lg gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            New chat
          </Button>

          <div className="flex items-center gap-2">
            <div className="relative">
              <select
                value={selectedModel}
                onChange={(e) => handleModelChange(e.target.value)}
                className="appearance-none bg-secondary/60 hover:bg-secondary text-foreground text-xs font-medium rounded-lg pl-2.5 pr-6 py-1.5 cursor-pointer outline-none transition-all"
              >
                <option value="auto">✨ Auto-Router</option>
                {availableModels.filter(m => m.id !== 'auto').map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3 h-3 text-muted-foreground pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 opacity-70" />
            </div>
          </div>
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
                  {/* Model Selector Pill */}
                  <div className="relative">
                    <select
                      value={selectedModel}
                      onChange={(e) => handleModelChange(e.target.value)}
                      className="appearance-none bg-secondary/50 hover:bg-secondary text-foreground text-xs font-medium rounded-lg pl-2.5 pr-6 py-1 cursor-pointer outline-none transition-all"
                    >
                      <option value="auto">Auto-Router</option>
                      {availableModels.filter(m => m.id !== 'auto').map((m) => (
                        <option key={m.id} value={m.id}>
                          {m.name.replace('Google ', '').replace(' (Cloud)', '')}
                        </option>
                      ))}
                    </select>
                    <ChevronDown className="w-3 h-3 text-muted-foreground pointer-events-none absolute right-1.5 top-1/2 -translate-y-1/2 opacity-70" />
                  </div>

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
                  Model: <span className="text-foreground font-medium">{activeModelDisplay}</span>
                </span>
              </div>

              <div className="flex items-center gap-2">
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
