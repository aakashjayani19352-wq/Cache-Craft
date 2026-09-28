import { NavGroup } from '@/types';

export const navGroups: NavGroup[] = [
  {
    label: 'Cache-Craft',
    items: [
      {
        title: 'Analytics Overview',
        url: '/dashboard/overview',
        icon: 'dashboard',
        isActive: false,
        shortcut: ['o', 'o'],
        items: []
      },
      {
        title: 'Chat Playground',
        url: '/dashboard/chat',
        icon: 'sparkles',
        isActive: false,
        shortcut: ['c', 'c'],
        items: []
      },
      {
        title: 'Cache Explorer',
        url: '/dashboard/cache',
        icon: 'database',
        isActive: false,
        shortcut: ['e', 'e'],
        items: []
      }
    ]
  },
  {
    label: 'Configuration',
    items: [
      {
        title: 'Settings',
        url: '/dashboard/settings',
        icon: 'settings',
        shortcut: ['s', 's'],
        isActive: false,
        items: []
      }
    ]
  }
];
