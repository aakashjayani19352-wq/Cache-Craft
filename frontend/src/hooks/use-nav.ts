'use client';

import { useMemo } from 'react';
import type { NavItem, NavGroup } from '@/types';

/**
 * Simplified nav hook — no RBAC needed for Cache-Craft (no auth).
 * All nav items are always visible.
 */
export function useFilteredNavItems(items: NavItem[]) {
  return useMemo(() => items, [items]);
}

export function useFilteredNavGroups(groups: NavGroup[]) {
  return useMemo(() => groups.filter((g) => g.items.length > 0), [groups]);
}
