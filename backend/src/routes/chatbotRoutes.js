import crypto from "node:crypto";
import express from "express";
import jwt from "jsonwebtoken";
import axios from "axios";
import { z } from "zod";
import { requireAuth } from "../middleware/auth.js";
import { config } from "../config.js";
import { createChatSession } from "../services/inMemoryStore.js";

const router = express.Router();

const tokenSchema = z.object({
  sessionId: z.string().uuid().optional()
});

const chatSchema = z.object({
  sessionId: z.string().uuid(),
  message: z.string().min(1),
  history: z.array(
    z.object({ role: z.enum(["user", "assistant"]), content: z.string() })
  ).optional()
});

router.post("/token", requireAuth, (req, res, next) => {
  try {
    const parsed = tokenSchema.parse(req.body || {});
    const sessionId = parsed.sessionId || crypto.randomUUID();

    createChatSession({
      id: sessionId,
      userId: req.user.userId,
      businessId: req.user.businessId,
      startedAt: new Date().toISOString()
    });

    const chatbotToken = jwt.sign(
      {
        sessionId,
        userId: req.user.userId,
        businessId: req.user.businessId,
        scope: "chat:invoke"
      },
      config.chatbotTokenSecret,
      { expiresIn: config.chatbotTokenTTL }
    );

    return res.json({ chatbotToken, sessionId, expiresIn: config.chatbotTokenTTL });
  } catch (err) {
    if (err.name === "ZodError") {
      return res.status(400).json({ error: "Invalid token payload", details: err.issues });
    }
    return next(err);
  }
});

router.post("/message", requireAuth, async (req, res, next) => {
  try {
    const parsed = chatSchema.parse(req.body);

    const response = await axios.post(`${config.aiServiceUrl}/chat`, {
      session_id: parsed.sessionId,
      user_id: req.user.userId,
      business_id: req.user.businessId,
      message: parsed.message,
      history: parsed.history || []
    });

    return res.json(response.data);
  } catch (err) {
    if (err.name === "ZodError") {
      return res.status(400).json({ error: "Invalid chat payload", details: err.issues });
    }
    if (err.response) {
      return res.status(err.response.status).json({ error: err.response.data });
    }
    return next(err);
  }
});

export default router;
