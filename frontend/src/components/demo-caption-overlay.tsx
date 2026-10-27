'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export interface CaptionData {
  tag?: string;
  title: string;
  text: string;
  color?: string;
  step?: string;
  visible?: boolean;
}

export default function DemoCaptionOverlay() {
  const [caption, setCaption] = useState<CaptionData | null>(null);

  useEffect(() => {
    (window as any).setCaption = (
      tag: string,
      title: string,
      text: string,
      color: string = '#58A6FF',
      step: string = ''
    ) => {
      setCaption({
        tag,
        title,
        text,
        color,
        step,
        visible: true
      });
    };

    (window as any).hideCaption = () => {
      setCaption(null);
    };

    const handleCustomEvent = (e: any) => {
      if (e.detail) {
        setCaption({ ...e.detail, visible: true });
      }
    };

    window.addEventListener('cache-craft-caption', handleCustomEvent);
    return () => {
      window.removeEventListener('cache-craft-caption', handleCustomEvent);
      delete (window as any).setCaption;
      delete (window as any).hideCaption;
    };
  }, []);

  if (!caption || !caption.visible) return null;

  const accentColor = caption.color || '#58A6FF';

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 20, scale: 0.95 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
        className="fixed bottom-7 left-1/2 -translate-x-1/2 z-[99999] pointer-events-none w-[90%] max-w-4xl"
      >
        <div
          className="relative px-6 py-4 rounded-xl shadow-2xl backdrop-blur-xl border flex flex-col gap-1.5 transition-all"
          style={{
            backgroundColor: 'rgba(13, 17, 23, 0.95)',
            borderColor: `${accentColor}55`,
            boxShadow: `0 12px 40px rgba(0, 0, 0, 0.85), 0 0 24px ${accentColor}30`
          }}
        >
          {/* Top Tag and Step Bar */}
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span
                className="px-2.5 py-0.5 rounded text-[11px] font-bold tracking-wider uppercase font-mono shadow-sm"
                style={{
                  backgroundColor: `${accentColor}25`,
                  color: accentColor,
                  border: `1px solid ${accentColor}60`
                }}
              >
                {caption.tag || 'FEATURE OVERVIEW'}
              </span>
              <span className="text-zinc-400 text-xs font-mono">
                Cache-Craft Interactive Walkthrough
              </span>
            </div>
            {caption.step && (
              <span
                className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded bg-zinc-800/80 text-zinc-300 border border-zinc-700/60"
              >
                {caption.step}
              </span>
            )}
          </div>

          {/* Title */}
          <h4 className="text-base sm:text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <span
              className="w-2.5 h-2.5 rounded-full animate-pulse"
              style={{ backgroundColor: accentColor }}
            />
            {caption.title}
          </h4>

          {/* Caption text */}
          <p className="text-xs sm:text-sm text-zinc-200 leading-relaxed font-sans font-normal">
            {caption.text}
          </p>

          {/* Bottom subtle progress line */}
          <div
            className="absolute bottom-0 left-0 right-0 h-[3px] rounded-b-xl"
            style={{
              background: `linear-gradient(90deg, transparent, ${accentColor}, transparent)`
            }}
          />
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
