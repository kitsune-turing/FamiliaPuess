import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    target: "es2020",
    rollupOptions: {
      output: {
        manualChunks: {
          react: ["react", "react-dom", "react-router-dom"],
        },
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/auth": "http://api:8000",
      "/dashboard": "http://api:8000",
      "/usuarios": "http://api:8000",
      "/roles": "http://api:8000",
      "/empleados": "http://api:8000",
      "/sedes": "http://api:8000",
      "/dispositivos": "http://api:8000",
      "/horarios": "http://api:8000",
      "/registro": "http://api:8000",
      "/reportes": "http://api:8000",
      "/auditoria": "http://api:8000",
      "/configuracion": "http://api:8000",
      "/novedades": "http://api:8000",
      "/calendario": "http://api:8000",
    },
  },
});
