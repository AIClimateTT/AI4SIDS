import { createEnv } from "@t3-oss/env-core";
import * as z from "zod";

export const env = createEnv({
  server: {
    VITE_BASE_URL: z.string().url().default("http://localhost:3000"),
    VITE_API_URL: z.string().url().default("http://localhost:8000"),

    // OAuth2 providers, optional, update as needed
    // GITHUB_CLIENT_ID: z.string().optional(),
    // GITHUB_CLIENT_SECRET: z.string().optional(),
    // GOOGLE_CLIENT_ID: z.string().optional(),
    // GOOGLE_CLIENT_SECRET: z.string().optional(),
  },
  runtimeEnv: process.env,
});
