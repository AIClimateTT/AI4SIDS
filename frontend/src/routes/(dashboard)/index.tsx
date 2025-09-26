import { createFileRoute, Link } from '@tanstack/react-router'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export const Route = createFileRoute('/(dashboard)/')({
  component: App,
})

function App() {
  return (
    <div className="">
      {/* Hero Section - positioned to start under the navbar */}
      <div className="relative min-h-screen w-full bg-[url('/event.jpeg')] bg-cover bg-no-repeat -mt-16 pt-16">
        <div className="absolute inset-0 h-full w-full bg-gray-900/60" />
        <div className="grid min-h-screen px-8">
          <div className="container relative z-10 my-auto mx-auto grid place-items-center text-center">
            <section className="py-20 px-4">
              <div className="container mx-auto text-center text-white">
                <h1 className="text-5xl font-bold  mb-6">
                  AI4SIDS
                </h1>
                <p className="text-xl  mb-8 max-w-3xl mx-auto">
                  AI-driven disaster resilience platform designed to enhance climate risk management
                  for Small Island Developing States through predictive analytics and real-time data integration.
                </p>
                <Link to="/map">
                <div className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors">
                  Starting with Trinidad • Scaling Across SIDS
                </div>
                </Link>
              </div>
            </section>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <section className="container mx-auto py-16 px-4 space-y-16">
        <div className="space-y-16">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Platform Capabilities
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg">Real-time Data</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Satellite imagery, IoT sensors, weather data, and citizen reports for comprehensive monitoring.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg">AI Risk Mapping</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Predictive analytics for flood detection, hurricane tracking, and climate risk assessment.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg">Automated Alerts</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Real-time notifications and early warning systems for rapid disaster response.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg">Post-Disaster Analytics</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Impact assessments for insurance, relief planning, and policy development with AI insights.
                </CardDescription>
              </CardContent>
            </Card>
          </div>

          {/* Impact Metrics */}
          <div className="bg-white rounded-xl p-8 shadow-lg">
            <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">Implementation Impact</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">Faster Response</div>
                <p className="text-gray-600">AI-driven insights reduce delays in emergency actions</p>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">Efficient Resources</div>
                <p className="text-gray-600">AI optimizes disaster relief allocation and deployment</p>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">Scalable Solution</div>
                <p className="text-gray-600">Designed for replication across SIDS for multiple climate risks</p>
              </div>
            </div>
          </div>
        </div>
      </section>


    </div>
  )
}
