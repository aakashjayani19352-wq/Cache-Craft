'use client';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import Link from 'next/link';

export function UserNav() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={<Button variant='ghost' className='relative h-8 w-8 rounded-full' />}
      >
        <div className='bg-primary text-primary-foreground flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold'>
          CC
        </div>
      </DropdownMenuTrigger>
      <DropdownMenuContent className='w-56' align='end' sideOffset={10}>
        <DropdownMenuGroup>
          <DropdownMenuLabel className='font-normal'>
            <div className='flex flex-col space-y-1'>
              <p className='text-sm leading-none font-medium'>Cache-Craft v2.0</p>
              <p className='text-muted-foreground text-xs leading-none'>Autonomous Semantic RAG Router</p>
            </div>
          </DropdownMenuLabel>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem render={<Link href='/dashboard/settings' />}>
            Cluster Settings
          </DropdownMenuItem>
          <DropdownMenuItem render={<a href='https://github.com/aakashjayani19352-wq/Cache-Craft' target='_blank' rel='noopener noreferrer' />}>
            GitHub Repository
          </DropdownMenuItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
