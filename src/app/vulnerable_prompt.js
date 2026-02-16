// Example vulnerable code for SecureAI-Scan (JS)
// This file intentionally contains patterns that should trigger SecureAI-Scan alerts

const express = require('express');
const openai = require('openai'); // Assume openai SDK is available
const logger = require('pino')(); // Example logger

const app = express();
app.use(express.json());

// AI001: Prompt injection via user input (High)
app.post('/prompt-injection', async (req, res) => {
  const prompt = `You are a secure assistant. User says: ${req.body.input}`;
  await openai.chat.completions.create({ model: "gpt-4.1", prompt });
  res.send('Prompt sent');
});

// AI002: Sensitive prompt logging (High)
app.post('/log-prompt', async (req, res) => {
  const prompt = req.body.prompt;
  const user = { email: req.body.email, token: req.body.token };
  logger.info({ prompt, email: user.email, token: user.token });
  res.send('Prompt logged');
});

// AI003: LLM call before authentication (Critical)
app.post('/ask', async (req, res) => {
  await openai.chat.completions.create({ messages: req.body.messages });
  // auth check happens later or not at all
  res.send('LLM called before auth');
});

// AI004: Sensitive data sent to LLM (High)
app.post('/send-sensitive', async (req, res) => {
  const user = req.body.user;
  await openai.chat.completions.create({
    messages: [{ role: "user", content: JSON.stringify(user) }],
  });
  res.send('Sensitive data sent to LLM');
});

// Start server (for test/demo purposes)
if (require.main === module) {
  app.listen(3000, () => {
    console.log('Test server running on port 3000');
  });
}
