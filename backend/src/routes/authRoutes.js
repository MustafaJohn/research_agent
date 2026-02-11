import crypto from "node:crypto";
import express from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { z } from "zod";
import { config } from "../config.js";
import { createUser, findUserByEmail } from "../services/inMemoryStore.js";

const router = express.Router();

const authSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  name: z.string().min(2)
});

router.post("/signup", async (req, res, next) => {
  try {
    const parsed = authSchema.parse(req.body);
    if (findUserByEmail(parsed.email)) {
      return res.status(409).json({ error: "User already exists" });
    }

    const passwordHash = await bcrypt.hash(parsed.password, 10);
    const user = {
      id: crypto.randomUUID(),
      email: parsed.email,
      name: parsed.name,
      passwordHash,
      businessId: "demo-business"
    };

    createUser(user);
    return res.status(201).json({
      id: user.id,
      email: user.email,
      name: user.name
    });
  } catch (err) {
    if (err.name === "ZodError") {
      return res.status(400).json({ error: "Invalid signup payload", details: err.issues });
    }
    return next(err);
  }
});

router.post("/login", async (req, res, next) => {
  try {
    const parsed = authSchema.pick({ email: true, password: true }).parse(req.body);
    const user = findUserByEmail(parsed.email);
    if (!user) {
      return res.status(401).json({ error: "Invalid credentials" });
    }

    const isValid = await bcrypt.compare(parsed.password, user.passwordHash);
    if (!isValid) {
      return res.status(401).json({ error: "Invalid credentials" });
    }

    const token = jwt.sign(
      { userId: user.id, email: user.email, businessId: user.businessId },
      config.jwtSecret,
      { expiresIn: config.jwtExpiresIn }
    );

    return res.json({ token });
  } catch (err) {
    if (err.name === "ZodError") {
      return res.status(400).json({ error: "Invalid login payload", details: err.issues });
    }
    return next(err);
  }
});

export default router;
