import { Outlet } from '@tanstack/react-router'
import { GovSidebar } from '@/features/shell/components/GovSidebar'
import { GovTopBar } from '@/features/shell/components/GovTopBar'

export function GovLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Desktop sidebar; mobile uses the Sheet drawer in GovTopBar */}
      <div className="hidden md:block">
        <GovSidebar />
      </div>
      <div className="flex flex-1 flex-col overflow-hidden">
        <GovTopBar />
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default GovLayout
