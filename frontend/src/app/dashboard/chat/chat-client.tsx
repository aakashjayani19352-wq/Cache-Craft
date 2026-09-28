'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar } from '@/components/ui/avatar';
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
  RotateCcw,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  metadata?: {
    latency?: number;
    hit_type?: 'CACHE_HIT_L1' | 'CACHE_HIT_L2' | 'CACHE_MISS';
    similarity?: number;
  };
}

const SUGGESTIONS = [
  'What is the difference between L1 Redis and L2 pgvector?',
  'Explain cosine similarity thresholding in vector search.',
  'How does Cache-Craft reduce LLM latency and API cost?'
];

export default function ChatClient() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: '### Welcome to Cache-Craft AI\n\nExperience our high-performance **multi-tier semantic cache**. Ask any question to observe real-time caching dynamics:\n\n- **L1 Cache (Redis)**: Sub-millisecond exact match lookup\n- **L2 Cache (pgvector)**: Fast semantic cosine similarity retrieval\n- **L3 Fallback (Ollama)**: Local LLM generation when cache misses\n\n*Tip: Repeat or rephrase a query to witness instantaneous cache hits!*',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    if (!isLoading) {
      inputRef.current?.focus();
    }
  }, [isLoading]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const sendQuery = async (queryText: string) => {
    const trimmed = queryText.trim();
    if (!trimmed || isLoading) return;

    const userMessage: Message = { id: Date.now().toString(), role: 'user', content: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Keep focus active in the input immediately
    requestAnimationFrame(() => {
      inputRef.current?.focus();
    });

    const history = messages
      .filter((m) => !m.id.startsWith('welcome') && !m.content.startsWith('⚠️'))
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
        }),
      });
      const data = await res.json();
      
      let hitType: 'CACHE_MISS' | 'CACHE_HIT_L1' | 'CACHE_HIT_L2' = 'CACHE_MISS';
      if (data.status === 'CACHE_HIT') {
        hitType = data.match_type === 'EXACT' ? 'CACHE_HIT_L1' : 'CACHE_HIT_L2';
      }

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'No response received from cache or model.',
        metadata: {
          latency: data.latency_ms,
          hit_type: hitType,
          similarity: data.similarity_score,
        },
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: `⚠️ **Connection Error**: Unable to reach backend at \`${apiUrl}\`. Please verify the API server is active.`,
        },
      ]);
    } finally {
      setIsLoading(false);
      requestAnimationFrame(() => {
        inputRef.current?.focus();
      });
    }
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) return;
    sendQuery(input);
    inputRef.current?.focus();
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleResetChat = () => {
    setMessages([
      {
        id: 'welcome-' + Date.now(),
        role: 'assistant',
        content: '### Cache-Craft AI Reset\n\nChat session cleared. Send a query or pick a prompt below to test cache retrieval.',
      },
    ]);
    toast.info('Chat session cleared');
    inputRef.current?.focus();
  };

  const renderBadge = (meta: Message['metadata']) => {
    if (!meta) return null;
    
    const isL1 = meta.hit_type === 'CACHE_HIT_L1';
    const isL2 = meta.hit_type === 'CACHE_HIT_L2';

    const pillStyle = isL1 
      ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20 shadow-emerald-500/5' 
      : isL2
      ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20 shadow-blue-500/5'
      : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20 shadow-amber-500/5';

    const dotColor = isL1
      ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]'
      : isL2
      ? 'bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]'
      : 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.8)]';

    const Icon = isL1 ? Zap : isL2 ? Database : Server;

    const label = isL1 
      ? 'L1 Cache Hit (Redis)' 
      : isL2
      ? `L2 Semantic Hit (${(meta.similarity! * 100).toFixed(1)}%)`
      : 'Cache Miss (Ollama LLM)';

    return (
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.2 }}
        className="flex items-center gap-2 mt-2 select-none"
      >
        <Badge variant="outline" className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-medium border backdrop-blur-md shadow-sm transition-all ${pillStyle}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
          <Icon className="w-3 h-3" />
          {label}
        </Badge>
        <span className="text-[11px] text-muted-foreground/75 font-mono flex items-center gap-1">
          ⚡ {meta.latency !== undefined ? `${meta.latency.toFixed(1)}ms` : '—'}
        </span>
      </motion.div>
    );
  };

  const isOnlyWelcome = messages.length <= 1;

  return (
    <div className="flex flex-col h-[calc(100vh-7.5rem)] w-full max-w-4xl mx-auto p-2 sm:p-4 space-y-3">
      {/* Apple-grade Header */}
      <div className="flex items-center justify-between px-2 pb-2">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-foreground via-foreground/90 to-foreground/70 bg-clip-text text-transparent">
              AI Playground
            </h1>
            <Badge variant="secondary" className="rounded-full text-[10px] px-2 py-0.5 font-normal tracking-wide text-muted-foreground bg-muted/60 border border-border/40">
              Multi-Tier Cache
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground">
            Ultra-low latency retrieval powered by Redis, pgvector & Ollama
          </p>
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={handleResetChat}
          className="rounded-full h-8 px-3 text-xs text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-all active:scale-95"
          title="Reset conversation"
        >
          <RotateCcw className="w-3.5 h-3.5 mr-1.5" />
          Clear
        </Button>
      </div>

      {/* Main Glass Chat Canvas */}
      <div className="flex-1 flex flex-col min-h-0 rounded-3xl border border-black/[0.06] dark:border-white/[0.08] shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.2)] bg-card/60 backdrop-blur-2xl relative overflow-hidden">
        {/* Messages Stream */}
        <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 min-h-0 space-y-6">
          <AnimatePresence initial={false}>
            {messages.map((msg) => {
              const isUser = msg.role === 'user';
              return (
                <motion.div
                  layout
                  initial={{ opacity: 0, y: 16, scale: 0.96 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ type: 'spring', stiffness: 350, damping: 28 }}
                  key={msg.id}
                  className={`flex gap-3.5 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  {/* Avatar */}
                  <Avatar className={`w-8 h-8 shrink-0 rounded-2xl flex items-center justify-center border shadow-sm ${
                    isUser 
                      ? 'bg-blue-600 text-white border-blue-500/30' 
                      : 'bg-zinc-100 dark:bg-zinc-800 text-foreground border-border/50'
                  }`}>
                    {isUser ? (
                      <User className="w-4 h-4 text-white" />
                    ) : (
                      <Bot className="w-4 h-4 text-foreground/80" />
                    )}
                  </Avatar>

                  {/* Message Bubble & Metadata */}
                  <div className={`flex flex-col max-w-[82%] sm:max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
                    <div
                      className={`relative group px-5 py-3.5 text-sm transition-all duration-300 ${
                        isUser
                          ? 'bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-3xl rounded-tr-md shadow-[0_4px_16px_rgba(37,99,235,0.25)] font-normal leading-relaxed'
                          : 'bg-card/90 dark:bg-zinc-900/90 text-card-foreground border border-black/[0.05] dark:border-white/[0.08] rounded-3xl rounded-tl-md shadow-[0_4px_20px_rgba(0,0,0,0.03)] dark:shadow-[0_4px_20px_rgba(0,0,0,0.2)] backdrop-blur-xl leading-relaxed'
                      }`}
                    >
                      {isUser ? (
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      ) : (
                        <div className="prose prose-sm dark:prose-invert max-w-none text-foreground/90 leading-relaxed font-normal">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {msg.content}
                          </ReactMarkdown>
                        </div>
                      )}

                      {/* Apple-style floating Copy action */}
                      {!isUser && (
                        <button
                          onClick={() => handleCopy(msg.id, msg.content)}
                          className="absolute -bottom-2 -right-2 opacity-0 group-hover:opacity-100 transition-all duration-200 p-1.5 rounded-full bg-background border border-border/80 shadow-md hover:scale-110 active:scale-95 text-muted-foreground hover:text-foreground"
                          title="Copy response"
                        >
                          {copiedId === msg.id ? (
                            <Check className="w-3.5 h-3.5 text-emerald-500" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>
                      )}
                    </div>

                    {/* Metadata telemetry */}
                    {renderBadge(msg.metadata)}
                  </div>
                </motion.div>
              );
            })}

            {/* Apple fluid typing indicator */}
            {isLoading && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 12 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: -12 }}
                transition={{ type: 'spring', stiffness: 350, damping: 28 }}
                className="flex gap-3.5 items-end"
              >
                <Avatar className="w-8 h-8 shrink-0 rounded-2xl flex items-center justify-center bg-zinc-100 dark:bg-zinc-800 border border-border/50 shadow-sm">
                  <Bot className="w-4 h-4 text-foreground/80" />
                </Avatar>
                <div className="px-5 py-3.5 rounded-3xl rounded-tl-md bg-card/90 dark:bg-zinc-900/90 border border-black/[0.05] dark:border-white/[0.08] flex items-center gap-2 shadow-[0_4px_20px_rgba(0,0,0,0.04)] backdrop-blur-xl">
                  <motion.span
                    animate={{ y: [0, -5, 0], opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 0.8, repeat: Infinity, ease: 'easeInOut' }}
                    className="w-2 h-2 bg-blue-500 rounded-full"
                  />
                  <motion.span
                    animate={{ y: [0, -5, 0], opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 0.8, repeat: Infinity, ease: 'easeInOut', delay: 0.15 }}
                    className="w-2 h-2 bg-indigo-500 rounded-full"
                  />
                  <motion.span
                    animate={{ y: [0, -5, 0], opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 0.8, repeat: Infinity, ease: 'easeInOut', delay: 0.3 }}
                    className="w-2 h-2 bg-emerald-500 rounded-full"
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Quick Suggestions for Empty/Initial State */}
          {isOnlyWelcome && !isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.4 }}
              className="pt-4 space-y-2.5"
            >
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-medium px-1">
                <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                <span>Suggested queries to test cache layers:</span>
              </div>
              <div className="grid gap-2 sm:grid-cols-3">
                {SUGGESTIONS.map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      sendQuery(item);
                      inputRef.current?.focus();
                    }}
                    className="group text-left p-3 rounded-2xl border border-black/[0.06] dark:border-white/[0.08] bg-background/50 hover:bg-background/90 hover:border-blue-500/40 transition-all duration-200 shadow-sm hover:shadow-md flex flex-col justify-between"
                  >
                    <span className="text-xs text-foreground/80 group-hover:text-blue-600 dark:group-hover:text-blue-400 font-medium leading-snug line-clamp-2">
                      {item}
                    </span>
                    <div className="mt-2 flex items-center text-[10px] text-muted-foreground group-hover:text-blue-500 transition-colors">
                      <span>Test query</span>
                      <ArrowRight className="w-3 h-3 ml-1 group-hover:translate-x-0.5 transition-transform" />
                    </div>
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Floating Cupertino Message Composer Bar */}
        <div className="p-3 sm:p-4 bg-background/40 backdrop-blur-xl border-t border-border/40">
          <form onSubmit={handleSend} className="relative flex items-center">
            <div className="relative w-full group">
              <Input
                ref={inputRef}
                autoFocus
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
                placeholder={isLoading ? "LLM generating... (you can keep typing)" : "Ask anything or test cache recall..."}
                className="w-full pr-14 pl-5 py-6 rounded-2xl bg-background/80 dark:bg-zinc-900/80 border border-black/[0.08] dark:border-white/[0.1] shadow-[0_2px_12px_rgba(0,0,0,0.03)] focus-visible:ring-2 focus-visible:ring-blue-500/30 focus-visible:border-blue-500/50 transition-all text-sm placeholder:text-muted-foreground/60"
              />
              <motion.div
                className="absolute right-2.5 top-1/2 -translate-y-1/2"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.92 }}
              >
                <Button
                  type="submit"
                  size="icon"
                  disabled={!input.trim() || isLoading}
                  className="h-9 w-9 rounded-xl bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-500/20 disabled:opacity-30 disabled:pointer-events-none transition-all"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </motion.div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
