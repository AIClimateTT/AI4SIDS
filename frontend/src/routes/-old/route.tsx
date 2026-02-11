import { createFileRoute, Outlet } from '@tanstack/react-router'
import Header from '@/components/Header'

import Footer  from '@/components/Footer'



function RouteComponent() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      {/* Add top padding to account for fixed navbar */}
      <main className='flex-1 '>
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
