import { createFileRoute, useNavigate } from '@tanstack/react-router'
// Assuming these are your components
import DataAnalytics from '@/components/DataAnalytics'
import FloodForecastModal from '@/components/FloodForecastModal'
import { analyticsSearchSchema } from '@/utils/route-schemas' 

// Configure the route with the search schema
export const Route = createFileRoute('/(dashboard)/analytics')({
  validateSearch: analyticsSearchSchema,
  component: RouteComponent,
})

function RouteComponent() {
  // 1. Get the current search parameters
  const { forecastLocation } = Route.useSearch()
  const navigate = useNavigate({ from: Route.id })

  // 2. Define the handler to close the modal
  const handleCloseModal = () => {
    // Navigate to the same route, removing the forecastLocation param from the URL
    navigate({ search: (prev) => ({ ...prev, forecastLocation: undefined }) })
  }
  
  // 3. Define the handler to open the modal (passed to DataAnalytics)
  const handleOpenForecast = (location: string) => {
    // Navigate to the same route, setting the forecastLocation param in the URL
    navigate({ search: (prev) => ({ ...prev, forecastLocation: location }) });
  }

  const isModalOpen = !!forecastLocation

  return (
    <main className="flex-1">
      {/* 4. Render the main page content, passing the handler */}
      <DataAnalytics onForecastClick={handleOpenForecast} />
      
      {/* 5. Conditionally render the modal based on the URL search parameter */}
      {isModalOpen && (
        <FloodForecastModal
          // We assert the type here because 'isModalOpen' guarantees it's defined.
          location={forecastLocation as string} 
          open={isModalOpen} 
          onClose={handleCloseModal}
        />
      )}
    </main>
  )
}