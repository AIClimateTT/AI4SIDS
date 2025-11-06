import { createFileRoute, ClientOnly, Link } from '@tanstack/react-router'
import { lazy, Suspense } from 'react'
import Header from '@/components/Header'
import Hero from '@/components/Hero'
const RiskMap = lazy(() => import('@/components/RiskMap'))
import ForecastPanel from '@/components/ForecastPanel'
import AlertsSection from '@/components/AlertsSection'
import AIChatbot from '@/components/AIChatbot'
import Footer from '@/components/Footer'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Mail, Lock, Users } from 'lucide-react'

export const Route = createFileRoute('/')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <Hero />
        <section id="dashboard">
          <ClientOnly
            fallback={
              <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                <div className="text-gray-600">Loading map...</div>
              </div>
            }
          >
            <Suspense
              fallback={
                <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                  <div className="text-gray-600">Loading map...</div>
                </div>
              }
            >
              <RiskMap />
            </Suspense>
          </ClientOnly>
        </section>
        <section id="assistant" className="py-16 px-6 bg-muted/30">
          <AIChatbot />
        </section>
        <section id="forecast">
          <ForecastPanel />
        </section>
        <section id="alerts">
          <AlertsSection />
        </section>
        {/* Access Info Section */}
        <section className="py-12 px-6 bg-muted/30">
          <div className="container mx-auto max-w-4xl">
            <Card className="shadow-lg border-2">
              <CardHeader className="text-center">
                <div className="flex justify-center mb-4">
                  <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                    <Lock className="h-8 w-8 text-primary" />
                  </div>
                </div>
                <CardTitle className="text-2xl">
                  Advanced Analytics & Research Access
                </CardTitle>
                <CardDescription className="text-base mt-2">
                  In-depth environmental data and analytics for researchers and
                  professionals
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid md:grid-cols-3 gap-6 text-center">
                  <div className="space-y-2">
                    <Users className="h-10 w-10 text-primary mx-auto" />
                    <h3 className="font-semibold">For Researchers</h3>
                    <p className="text-sm text-muted-foreground">
                      Access detailed datasets and historical trends for
                      non-commercial use
                    </p>
                  </div>
                  <div className="space-y-2">
                    <Mail className="h-10 w-10 text-primary mx-auto" />
                    <h3 className="font-semibold">
                      For Disaster Risk Professionals
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Advanced forecasting and risk modeling tools
                    </p>
                  </div>
                  <div className="space-y-2">
                    <Lock className="h-10 w-10 text-primary mx-auto" />
                    <h3 className="font-semibold">Secure Platform</h3>
                    <p className="text-sm text-muted-foreground">
                      Protected access with verified credentials
                    </p>
                  </div>
                </div>

                <div className="border-t pt-6">
                  <div className="text-center space-y-4">
                    <p className="text-sm text-muted-foreground">
                      Need access to advanced analytics, data exports, and
                      research tools?
                      <br />
                      Request your login credentials through the AI in Climate
                      Research TT platform.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-3 justify-center">
                      <a
                        href="https://climate.lab.tt/index.php/contact-us"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Button size="lg" className="gap-2">
                          <Mail className="h-4 w-4" />
                          Request Access via AI in Climate Research TT
                        </Button>
                      </a>
                      <a
                        href="https://climate.lab.tt/index.php/featured_projects/ai4sids"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Button size="lg" variant="outline" className="gap-2">
                          <Users className="h-4 w-4" />
                          Learn More
                        </Button>
                      </a>
                    </div>
                    <p className="text-xs text-muted-foreground mt-4">
                      AI in Climate Research TT provides verified credentials
                      for academic researchers, government officials, and
                      authorized environmental professionals.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}
