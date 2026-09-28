import React from 'react';
import { SidebarTrigger } from '../ui/sidebar';
import { Separator } from '../ui/separator';
import { Breadcrumbs } from '../breadcrumbs';
import { ThemeModeToggle } from '../themes/theme-mode-toggle';

export default function Header() {
  return (
    <header className='bg-background/70 sticky top-0 z-20 flex h-14 shrink-0 items-center justify-between gap-2 backdrop-blur-xl border-b border-black/[0.05] dark:border-white/[0.08] transition-all'>
      <div className='flex items-center gap-2 px-4'>
        <SidebarTrigger className='-ml-1 rounded-lg hover:bg-muted/60 transition-colors' />
        <Separator orientation='vertical' className='mr-2 h-4 data-vertical:self-center opacity-40' />
        <Breadcrumbs />
      </div>

      <div className='flex items-center gap-2 px-4'>
        <ThemeModeToggle />
      </div>
    </header>
  );
}
