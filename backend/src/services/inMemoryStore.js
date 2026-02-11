const users = [];
const sessions = [];

export function createUser(user) {
  users.push(user);
  return user;
}

export function findUserByEmail(email) {
  return users.find((u) => u.email === email);
}

export function createChatSession(session) {
  sessions.push(session);
  return session;
}

export function getChatSessionById(id) {
  return sessions.find((s) => s.id === id);
}
