import { createFileRoute } from '@tanstack/react-router'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export const Route = createFileRoute('/(dashboard)/team')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className="py-16 px-4 space-y-16">
      {/* Header */}
      <section className="py-16">
        <div className="container mx-auto text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-6">
            Collaboration & Partnerships
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            We seek partnerships with governments, NGOs, and academic institutions to integrate
            AI4SIDS into disaster management systems across Small Island Developing States.
          </p>
        </div>
      </section>

      {/* Partnership Opportunities */}
      <section className="">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Partnership Opportunities
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-xl text-blue-600">Community-Based Early Warning Networks</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  Training local responders and building community capacity for AI-powered early warning systems.
                  Empower communities with tools and knowledge for rapid disaster response.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-xl text-green-600">AI-Powered Resilience Training</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  Workshops and educational programs on AI-driven climate adaptation strategies.
                  Building technical expertise and institutional capacity across SIDS.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-xl text-purple-600">Public-Private Partnerships</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  Supporting smart infrastructure development and technology integration.
                  Collaborative funding and implementation of AI disaster management solutions.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-xl text-orange-600">Knowledge-Sharing Consortium</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  Establishing a SIDS-wide AI disaster network for sharing best practices,
                  research findings, and collaborative development of climate resilience solutions.
                </CardDescription>
              </CardContent>
            </Card>
          </div>

          {/* Target Partners */}
          <div className="bg-white rounded-xl p-8 shadow-lg">
            <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">Target Partner Organizations</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <h4 className="text-xl font-semibold text-blue-600 mb-4">Government Agencies</h4>
                <ul className="space-y-2 text-gray-600">
                  <li>• National Disaster Management Offices</li>
                  <li>• Meteorological Services</li>
                  <li>• Environmental Protection Agencies</li>
                  <li>• Emergency Response Teams</li>
                </ul>
              </div>

              <div className="text-center">
                <h4 className="text-xl font-semibold text-green-600 mb-4">NGOs & International</h4>
                <ul className="space-y-2 text-gray-600">
                  <li>• UN Office for Disaster Risk Reduction</li>
                  <li>• Caribbean Disaster Emergency Management</li>
                  <li>• Pacific Disaster Center</li>
                  <li>• Climate Resilience Organizations</li>
                </ul>
              </div>

              <div className="text-center">
                <h4 className="text-xl font-semibold text-purple-600 mb-4">Academic Institutions</h4>
                <ul className="space-y-2 text-gray-600">
                  <li>• University of the West Indies</li>
                  <li>• Pacific Universities Network</li>
                  <li>• Climate Research Centers</li>
                  <li>• AI & Data Science Programs</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
