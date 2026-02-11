import express from "express";
import cors from "cors";
import authRoutes from "./routes/authRoutes.js";
import chatbotRoutes from "./routes/chatbotRoutes.js";
import { config } from "./config.js";
import { apiRateLimiter } from "./middleware/rateLimiter.js";
import { requestLogger } from "./middleware/requestLogger.js";
import { notFoundHandler, errorHandler } from "./middleware/errorHandler.js";

const app = express();

app.use(cors());
app.use(express.json());
app.use(requestLogger);
app.use(apiRateLimiter);

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

app.use("/api/auth", authRoutes);
app.use("/api/chatbot", chatbotRoutes);

app.use(notFoundHandler);
app.use(errorHandler);

app.listen(config.port, () => {
  console.log(`Backend listening on http://localhost:${config.port}`);
});
