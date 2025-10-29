import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CloudRain, Droplets, TrendingUp, AlertCircle } from "lucide-react";

const ForecastPanel = () => {
  const forecast = [
    { day: "Today", date: "Oct 16", rainfall: 145, risk: "critical", confidence: 95 },
    { day: "Tomorrow", date: "Oct 17", rainfall: 98, risk: "high-risk", confidence: 92 },
    { day: "Oct 18", date: "Fri", rainfall: 65, risk: "moderate", confidence: 88 },
    { day: "Oct 19", date: "Sat", rainfall: 42, risk: "low-risk", confidence: 85 },
    { day: "Oct 20", date: "Sun", rainfall: 28, risk: "low-risk", confidence: 80 },
    { day: "Oct 21", date: "Mon", rainfall: 15, risk: "safe", confidence: 78 },
    { day: "Oct 22", date: "Tue", rainfall: 12, risk: "safe", confidence: 75 },
  ];

  const getRiskColor = (risk: string) => {
    const colors = {
      "critical": "bg-critical text-critical-foreground",
      "high-risk": "bg-high-risk text-high-risk-foreground",
      "moderate": "bg-moderate text-moderate-foreground",
      "low-risk": "bg-low-risk text-low-risk-foreground",
      "safe": "bg-safe text-safe-foreground",
    };
    return colors[risk as keyof typeof colors] || "";
  };

  return (
    <section className="py-16 px-6 bg-muted/30">
      <div className="container mx-auto">
        <div className="text-center mb-10">
          <h2 className="text-4xl font-bold mb-3">7-Day Flood Forecast</h2>
          <p className="text-muted-foreground text-lg">
            AI-powered predictions integrating weather, tide, and hydrological models
          </p>
        </div>

        <div className="grid lg:grid-cols-7 md:grid-cols-4 sm:grid-cols-3 gap-4 mb-8">
          {forecast.map((day, index) => (
            <Card 
              key={index} 
              className={`shadow-md hover:shadow-lg transition-smooth ${
                index === 0 ? 'ring-2 ring-primary shadow-glow' : ''
              }`}
            >
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">{day.day}</CardTitle>
                <CardDescription className="text-xs">{day.date}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-center">
                  <CloudRain className="h-8 w-8 mx-auto text-primary mb-2" />
                  <div className="text-2xl font-bold">{day.rainfall}mm</div>
                  <div className="text-xs text-muted-foreground">Rainfall</div>
                </div>
                <Badge className={`w-full justify-center text-xs ${getRiskColor(day.risk)}`}>
                  {day.risk === "critical" ? "CRITICAL" : 
                   day.risk === "high-risk" ? "HIGH" :
                   day.risk === "moderate" ? "MODERATE" :
                   day.risk === "low-risk" ? "LOW" : "SAFE"}
                </Badge>
                <div className="text-xs text-center text-muted-foreground">
                  {day.confidence}% confidence
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Detailed Today's Forecast */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-critical" />
              Critical Alert: Today's Conditions
            </CardTitle>
            <CardDescription>
              Detailed breakdown of current flood risk factors
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <Droplets className="h-4 w-4 text-primary" />
                  Precipitation Analysis
                </div>
                <div className="text-sm text-muted-foreground">
                  Heavy rainfall expected: 145mm in next 24 hours. Previous 48h: 203mm accumulated.
                  Soil saturation at 87%.
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <TrendingUp className="h-4 w-4 text-high-risk" />
                  River Levels
                </div>
                <div className="text-sm text-muted-foreground">
                  Caroni River: 4.2m (+2.1m above normal). Ortoire River: 3.8m (+1.6m).
                  Flash flood warnings active for watershed areas.
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <CloudRain className="h-4 w-4 text-accent" />
                  Storm Systems
                </div>
                <div className="text-sm text-muted-foreground">
                  Tropical depression TD-12 approaching from east. Expected landfall: 18:00 UTC.
                  Storm surge: +0.8m above normal tides.
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

export default ForecastPanel;
