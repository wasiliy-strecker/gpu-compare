import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": process.env.GPU_COMPARE_API_URL || "http://localhost:58100",
      "/health": process.env.GPU_COMPARE_API_URL || "http://localhost:58100",
    },
  },
});
