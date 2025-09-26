import { createFileRoute } from '@tanstack/react-router'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'

export const Route = createFileRoute('/(dashboard)/learn')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className="py-16 px-4 space-y-16">
      {/* Header */}
      <section className="py-16">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-6">
            Learn About AI4SIDS
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Understanding climate resilience, disaster management, and how AI technology
            can enhance early warning systems for Small Island Developing States.
          </p>
        </div>
      </section>

      {/* Key Concepts */}
      <section className="">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Key Concepts
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg text-blue-600">Multi-Hazard Early Warning Systems</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Integrated systems that monitor multiple climate risks including floods, hurricanes,
                  droughts, and sea-level rise to provide comprehensive early warnings.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg text-green-600">Predictive Analytics</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  AI algorithms that analyze historical data, real-time sensors, and satellite imagery
                  to predict climate events and their potential impacts.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg text-purple-600">Climate Risk Mapping</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Geographic visualization of climate vulnerabilities and risk zones to inform
                  disaster preparedness and response planning.
                </CardDescription>
              </CardContent>
            </Card>
          </div>

          {/* FAQ Section */}
          <div className="bg-white rounded-xl p-8 shadow-lg">
            <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">
              Frequently Asked Questions
            </h3>

            <Accordion type="single" collapsible className="space-y-4">
              <AccordionItem value="item-1">
                <AccordionTrigger className="text-left">
                  What makes Small Island Developing States particularly vulnerable to climate change?
                </AccordionTrigger>
                <AccordionContent>
                  SIDS face unique vulnerabilities due to their geographic isolation, limited land area,
                  exposure to sea-level rise, frequent extreme weather events, and limited resources for
                  disaster response and recovery. Their economies often depend on climate-sensitive sectors
                  like tourism and fishing, making them especially susceptible to climate impacts.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-2">
                <AccordionTrigger className="text-left">
                  How does AI4SIDS enhance traditional disaster management approaches?
                </AccordionTrigger>
                <AccordionContent>
                  AI4SIDS integrates multiple data sources (satellite imagery, IoT sensors, weather data,
                  citizen reports) with advanced AI algorithms to provide faster, more accurate predictions.
                  This enables proactive rather than reactive disaster management, optimizes resource allocation,
                  and provides automated early warning systems that can save lives and reduce economic losses.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-3">
                <AccordionTrigger className="text-left">
                  What types of climate hazards can the platform address?
                </AccordionTrigger>
                <AccordionContent>
                  While starting with flood risk management in Trinidad, AI4SIDS is designed to expand to
                  multiple climate hazards including hurricanes, tropical storms, droughts, sea-level rise,
                  coastal erosion, and extreme temperature events. The platform's modular design allows for
                  phased implementation across different hazard types.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-4">
                <AccordionTrigger className="text-left">
                  How can communities and local organizations get involved?
                </AccordionTrigger>
                <AccordionContent>
                  Communities can participate through citizen reporting systems, local sensor networks,
                  and community-based early warning programs. We offer training workshops for local responders,
                  educational programs on climate adaptation, and opportunities for community feedback through
                  our generative AI components. Local knowledge is crucial for effective disaster management.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-5">
                <AccordionTrigger className="text-left">
                  What data sources does AI4SIDS integrate?
                </AccordionTrigger>
                <AccordionContent>
                  The platform integrates diverse data sources including satellite imagery for land use and
                  weather monitoring, IoT sensors for real-time environmental measurements, meteorological data
                  from weather stations, ocean monitoring systems, citizen reports through mobile apps, and
                  historical climate and disaster records for pattern analysis and model training.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-6">
                <AccordionTrigger className="text-left">
                  How is the platform designed for scalability across different SIDS?
                </AccordionTrigger>
                <AccordionContent>
                  AI4SIDS follows a modular, cloud-based architecture that can be adapted to different island
                  contexts. The platform includes configurable risk models, adaptable user interfaces for
                  different languages and local needs, standardized APIs for data integration, and a knowledge-sharing
                  network that allows SIDS to learn from each other's experiences and best practices.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        </div>
      </section>
    </div>
  )
}
