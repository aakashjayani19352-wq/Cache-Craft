'use client';
import { Button } from '@/components/ui/button';
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem
} from '@/components/ui/sidebar';
import { Icons } from './icons';
import Link from 'next/link';

export function OrgSwitcher() {
  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <SidebarMenuButton size='lg' render={<Link href='/dashboard/overview' />}>
          <div className='bg-primary text-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg'>
            <Icons.logo className='size-4' />
          </div>
          <div className='grid flex-1 text-left text-sm leading-tight'>
            <span className='truncate font-semibold'>Cache-Craft</span>
            <span className='truncate text-xs text-muted-foreground'>Semantic Cache</span>
          </div>
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
