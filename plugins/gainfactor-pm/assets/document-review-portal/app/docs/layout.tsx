import { DocsLayout } from 'fumadocs-ui/layouts/notebook';
import { baseOptions } from '@/lib/layout.shared';
import { source } from '@/lib/source';
import { FullSearchTrigger } from 'fumadocs-ui/layouts/shared/slots/search-trigger';
import { DocsHeader } from '@/components/docs-header';

export default function Layout({ children }: LayoutProps<'/docs'>) {
  return (
    <DocsLayout tree={source.getPageTree()} {...baseOptions()} containerProps={{ className: 'gainfactor-docs-layout' }} sidebar={{ banner: <FullSearchTrigger className="sidebar-search" /> }} slots={{ header: DocsHeader }}>
        {children}
    </DocsLayout>
  );
}
