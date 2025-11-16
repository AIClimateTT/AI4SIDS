import { createEnv } from "@t3-oss/env-core";
import * as z from "zod";

export const env = createEnv({
  server: {
    VITE_BASE_URL: z.string().url().default("http://localhost:3000"),
    VITE_API_URL: z.string().url().default("http://localhost:8000"),

    // API Polling Intervals (in seconds)
    VITE_REFETCH_INTERVAL: z.coerce.number().default(15),
    VITE_LOCATIONS_REFETCH_INTERVAL: z.coerce.number().default(60),
    VITE_ANALYTICS_REFETCH_INTERVAL: z.coerce.number().default(60),
    VITE_PREDICTION_STATUS_REFETCH_INTERVAL: z.coerce.number().default(30),
    VITE_API_STATUS_REFETCH_INTERVAL: z.coerce.number().default(30),

    // Data Freshness (in seconds)
    VITE_STALE_TIME: z.coerce.number().default(15),
    VITE_DATA_FRESH_THRESHOLD: z.coerce.number().default(30),

    // Retry Configuration
    VITE_RETRY_COUNT: z.coerce.number().default(3),
    VITE_RETRY_DELAY_BASE: z.coerce.number().default(5),
    
    // Chat Feature Toggles
    VITE_USE_STATIC_RESPONSES: z.coerce.boolean().default(true),
    VITE_CHAT_API_BASE_URL: z.string().url().default("http://localhost:8000"),
  },
  runtimeEnv: process.env,
});
