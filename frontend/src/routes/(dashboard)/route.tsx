import { createFileRoute, Outlet } from '@tanstack/react-router'
import Navbar from '@/components/Header'

import { Footer } from '@/components/Footer'

export const Route = createFileRoute('/(dashboard)')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className="min-h-screen">
      <Navbar />
      {/* Add top padding to account for fixed navbar */}
      <main className='flex-1 bg-gradient-to-br from-blue-50 to-green-50'>
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
