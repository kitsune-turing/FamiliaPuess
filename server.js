import express from "express";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 3000;
const DIST = join(__dirname, "dist");

app.use((_req, res, next) => {
  res.setHeader("Strict-Transport-Security", "max-age=63072000; includeSubDomains");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("Referrer-Policy", "strict-origin-when-cross-origin");
  res.setHeader("Permissions-Policy", "camera=(), microphone=(), geolocation=()");
  res.setHeader(
    "Content-Security-Policy",
    [
      "default-src 'self'",
      "script-src 'self'",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "font-src 'self' https://fonts.gstatic.com",
      "img-src 'self' data: blob:",
      "connect-src 'self' https://process-api.familiapues.com",
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join("; "),
  );
  next();
});

app.use(express.static(DIST, { maxAge: "1y", immutable: true, index: false }));

app.use("/assets", express.static(join(DIST, "assets"), { maxAge: "1y", immutable: true }));

app.get("/{*path}", (_req, res) => {
  res.setHeader("Cache-Control", "no-cache");
  res.sendFile(join(DIST, "index.html"));
});

app.listen(PORT, () => {
  console.log(`Imputar running on port ${PORT}`);
});
