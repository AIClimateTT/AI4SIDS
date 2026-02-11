import { z } from 'zod';

// Define the schema for the /analytics route's search parameters
export const analyticsSearchSchema = z.object({
  forecastLocation: z.string().optional(),
});

// Export the inferred TypeScript type for easy use
export type AnalyticsSearch = z.infer<typeof analyticsSearchSchema>;