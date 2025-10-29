import { Shield, MapPin, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";


const Hero = () => {
  return (
    <section className="relative min-h-[600px] flex items-center justify-center overflow-hidden">
      {/* Background Image with Overlay */}
      <div className="absolute inset-0">
        <img 
          src={'hero-caribbean.jpg'} 
          alt="Caribbean coastline showing SIDS vulnerability to flooding" 
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-hero opacity-80" />
      </div>

      {/* Content */}
      <div className="container relative z-10 px-6 py-20 text-center">
        <div className="max-w-4xl mx-auto space-y-6">
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-white drop-shadow-lg">
            AI4SIDS Disaster Resilience
          </h1>
          <p className="text-xl md:text-2xl text-white/95 max-w-2xl mx-auto drop-shadow">
            Real-time flood risk prediction and alerts for Caribbean Small Island Developing States
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
            <Button 
              size="lg" 
              className="bg-white text-primary hover:bg-white/90 shadow-lg text-lg px-8"
              asChild
            >
              <a href="#dashboard">
                <MapPin className="mr-2 h-5 w-5" />
                Check My Location
              </a>
            </Button>
            <Button 
              size="lg" 
              variant="outline"
              className="bg-white/10 text-white border-white/30 hover:bg-white/20 backdrop-blur-sm text-lg px-8"
              asChild
            >
              <a href="#dashboard">
                <Shield className="mr-2 h-5 w-5" />
                View Dashboard
              </a>
            </Button>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
            <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
              <div className="text-3xl font-bold text-white">24/7</div>
              <div className="text-white/80 mt-1">Real-time Monitoring</div>
            </div>
            <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
              <div className="text-3xl font-bold text-white">7-Day</div>
              <div className="text-white/80 mt-1">Forecast Available</div>
            </div>
            <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
              <div className="text-3xl font-bold text-white">Multi-Source</div>
              <div className="text-white/80 mt-1">Data Integration</div>
            </div>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <AlertTriangle className="h-8 w-8 text-white opacity-80" />
      </div>
    </section>
  );
};

export default Hero;
