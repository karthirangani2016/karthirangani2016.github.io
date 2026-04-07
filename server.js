const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const MESSAGES_FILE = path.join(__dirname, 'messages.json');
const ADMIN_PASSWORD = 'nexsolve@2026';

app.use(express.json());
app.use(express.static(__dirname));

if (!fs.existsSync(MESSAGES_FILE)) {
  fs.writeFileSync(MESSAGES_FILE, JSON.stringify([]));
}

app.post('/api/contact', (req, res) => {
  const { name, email, subject, message } = req.body;
  if (!name || !email || !subject || !message) {
    return res.status(400).json({ error: 'All fields are required.' });
  }

  const entry = {
    id: Date.now(),
    name,
    email,
    subject,
    message,
    date: new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })
  };

  const messages = JSON.parse(fs.readFileSync(MESSAGES_FILE));
  messages.unshift(entry);
  fs.writeFileSync(MESSAGES_FILE, JSON.stringify(messages, null, 2));

  res.json({ success: true });
});

app.post('/api/admin/messages', (req, res) => {
  const { password } = req.body;
  if (password !== ADMIN_PASSWORD) {
    return res.status(401).json({ error: 'Incorrect password.' });
  }
  const messages = JSON.parse(fs.readFileSync(MESSAGES_FILE));
  res.json({ messages });
});

app.delete('/api/admin/messages/:id', (req, res) => {
  const { password } = req.body;
  if (password !== ADMIN_PASSWORD) {
    return res.status(401).json({ error: 'Incorrect password.' });
  }
  let messages = JSON.parse(fs.readFileSync(MESSAGES_FILE));
  messages = messages.filter(m => m.id !== parseInt(req.params.id));
  fs.writeFileSync(MESSAGES_FILE, JSON.stringify(messages, null, 2));
  res.json({ success: true });
});

app.listen(PORT, () => {
  console.log(`NexSolve server running on port ${PORT}`);
});
