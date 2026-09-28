import PageContainer from '@/components/layout/page-container';
import { api } from '@/lib/api';
import SettingsClient from './settings-client';

export default async function SettingsPage() {
  const settings = await api.settings();
  return (
    <PageContainer>
      <SettingsClient settings={settings} />
    </PageContainer>
  );
}
