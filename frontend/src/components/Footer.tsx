export function Footer() {
    return (
        <footer className="bg-gray-900 text-white py-8 ">
            <div className="container mx-auto px-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div>
                        <h3 className="text-lg font-semibold mb-4">AI4SIDS</h3>
                        <p className="text-gray-300 text-sm">
                            AI-driven disaster resilience platform for Small Island Developing States.
                            Enhancing climate risk management through predictive analytics and real-time data.
                        </p>
                    </div>

                    <div>
                        <h4 className="font-semibold mb-4">Focus Areas</h4>
                        <ul className="space-y-2 text-sm text-gray-300">
                            <li>• Flood Risk Management</li>
                            <li>• Hurricane Prediction</li>
                            <li>• Sea-Level Rise Monitoring</li>
                            <li>• Drought Assessment</li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-semibold mb-4">Partnership</h4>
                        <ul className="space-y-2 text-sm text-gray-300">
                            <li>• Government Collaboration</li>
                            <li>• NGO Partnerships</li>
                            <li>• Academic Institutions</li>
                            <li>• Community Networks</li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-gray-700 mt-8 pt-6 text-center">
                    <p className="text-gray-400 text-sm">
                        © 2025 AI4SIDS. Building climate resilience for Small Island Developing States.
                    </p>
                </div>
            </div>
        </footer>
    )
}