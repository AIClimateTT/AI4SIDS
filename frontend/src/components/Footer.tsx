// export function Footer() {
//     return (
//         <footer className="bg-gray-900 text-white py-8 ">
//             <div className="container mx-auto px-4">
//                 <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
//                     <div>
//                         <h3 className="text-lg font-semibold mb-4">AI4SIDS</h3>
//                         <p className="text-gray-300 text-sm">
//                             AI-driven disaster resilience platform for Small Island Developing States.
//                             Enhancing climate risk management through predictive analytics and real-time data.
//                         </p>
//                     </div>

//                     <div>
//                         <h4 className="font-semibold mb-4">Focus Areas</h4>
//                         <ul className="space-y-2 text-sm text-gray-300">
//                             <li>• Flood Risk Management</li>
//                             <li>• Hurricane Prediction</li>
//                             <li>• Sea-Level Rise Monitoring</li>
//                             <li>• Drought Assessment</li>
//                         </ul>
//                     </div>

//                     <div>
//                         <h4 className="font-semibold mb-4">Partnership</h4>
//                         <ul className="space-y-2 text-sm text-gray-300">
//                             <li>• Government Collaboration</li>
//                             <li>• NGO Partnerships</li>
//                             <li>• Academic Institutions</li>
//                             <li>• Community Networks</li>
//                         </ul>
//                     </div>
//                 </div>

//                 <div className="border-t border-gray-700 mt-8 pt-6 text-center">
//                     <p className="text-gray-400 text-sm">
//                         © 2025 AI4SIDS. Building climate resilience for Small Island Developing States.
//                     </p>
//                 </div>
//             </div>
//         </footer>
//     )
// }

import { Shield, Mail, Phone, MapPin, ExternalLink } from "lucide-react";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-primary text-primary-foreground">
      <div className="container mx-auto px-6 py-12">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          {/* About */}
          <div className="space-y-3">
            <h3 className="font-bold text-lg flex items-center gap-2">
              <Shield className="h-5 w-5" />
              AI4SIDS
            </h3>
            <p className="text-sm text-primary-foreground/80">
              AI-powered disaster resilience platform for Caribbean Small Island Developing States.
            </p>
          </div>

          {/* Quick Links */}
          <div className="space-y-3">
            <h4 className="font-semibold">Quick Links</h4>
            <ul className="space-y-2 text-sm text-primary-foreground/80">
              <li>
                <a href="#" className="hover:text-primary-foreground transition-smooth">
                  About the Project
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-foreground transition-smooth">
                  Data Sources
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-foreground transition-smooth">
                  Methodology
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-foreground transition-smooth">
                  Partners
                </a>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div className="space-y-3">
            <h4 className="font-semibold">Resources</h4>
            <ul className="space-y-2 text-sm text-primary-foreground/80">
              <li>
                <a href="#" className="hover:text-primary-foreground transition-smooth flex items-center gap-1">
                  User Guide
                  <ExternalLink className="h-3 w-3" />
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-foreground transition-smooth flex items-center gap-1">
                  API Documentation
                  <ExternalLink className="h-3 w-3" />
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-foreground transition-smooth flex items-center gap-1">
                  FAQs
                  <ExternalLink className="h-3 w-3" />
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-foreground transition-smooth">
                  Privacy Policy
                </a>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div className="space-y-3">
            <h4 className="font-semibold">Emergency Contact</h4>
            <ul className="space-y-2 text-sm text-primary-foreground/80">
              <li className="flex items-center gap-2">
                <Phone className="h-4 w-4" />
                110 (Emergency)
              </li>
              <li className="flex items-center gap-2">
                <Phone className="h-4 w-4" />
                116 (Disaster Mgmt)
              </li>
              <li className="flex items-center gap-2">
                <Mail className="h-4 w-4" />
                aiclimatett@gmail.com
              </li>
              <li className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                Caribbean Region
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-primary-foreground/20 pt-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-primary-foreground/80">
            <p>
              © {currentYear} AI4SIDS. All rights reserved. Powered by AI and open data.
            </p>
            <div className="flex gap-4">
              <a href="#" className="hover:text-primary-foreground transition-smooth">
                Terms of Service
              </a>
              <a href="#" className="hover:text-primary-foreground transition-smooth">
                Accessibility
              </a>
              <a href="#" className="hover:text-primary-foreground transition-smooth">
                Contact
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
