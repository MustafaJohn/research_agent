import dotenv from "dotenv";

dotenv.config();

export const config = {
  port: Number(process.env.PORT || 4000),
  jwtSecret: process.env.JWT_SECRET || "dev-secret",
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || "1h",
  chatbotTokenSecret: process.env.CHATBOT_TOKEN_SECRET || "chatbot-secret",
  chatbotTokenTTL: process.env.CHATBOT_TOKEN_TTL || "5m",
  aiServiceUrl: process.env.AI_SERVICE_URL || "http://localhost:8000"
};
