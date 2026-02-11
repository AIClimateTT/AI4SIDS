/**
 * Alert action item generation utilities
 * Maps flood risk levels to actionable recommendations
 */

export const generateActionItemsForLevel = (level: string): string[] => {
  const actions: Record<string, string[]> = {
    'critical': [
      'Evacuate immediately to higher ground',
      'Call emergency services: 110',
      'Avoid all flooded areas'
    ],
    'high': [
      'Prepare emergency kit and evacuation plan',
      'Secure property and valuables',
      'Monitor weather updates continuously'
    ],
    'moderate': [
      'Avoid low-lying areas and flood-prone roads',
      'Check drainage systems',
      'Stay informed about conditions'
    ],
    'low': [
      'Stay alert and monitor conditions',
      'Avoid travel near rivers and streams',
      'Prepare for potential worsening'
    ],
    'safe': [
      'Continue normal monitoring',
      'Stay weather-aware',
      'Review emergency plans'
    ]
  };
  
  return actions[level] || ['Monitor flood conditions'];
};

export const generateAlertTitle = (level: string, location: string): string => {
  const titles: Record<string, string> = {
    'critical': `EXTREME FLOOD WARNING - ${location}`,
    'high': `Flood Warning - ${location}`,
    'moderate': `Flood Watch - ${location}`,
    'low': `Flood Advisory - ${location}`,
    'safe': `Normal Conditions - ${location}`
  };
  
  return titles[level] || `Alert - ${location}`;
};

export const generateAlertDescription = (apiMessage: string, level: string, riverLevel?: number): string => {
  // Enhance the API message with more context
  const baseDescriptions: Record<string, string> = {
    'critical': 'Immediate evacuation recommended. Flooding expected within 2-4 hours.',
    'high': 'Prepare to evacuate. Monitor conditions closely and be ready to move to higher ground.',
    'moderate': 'Flooding possible in low-lying areas. Avoid unnecessary travel near waterways.',
    'low': 'Conditions approaching flood threshold. Stay alert and monitor updates.',
    'safe': 'Normal river conditions. Continue routine monitoring.'
  };
  
  const description = baseDescriptions[level] || apiMessage;
  
  if (riverLevel !== undefined) {
    return `${description} Current river level: ${riverLevel.toFixed(2)}m`;
  }
  
  return description;
};
