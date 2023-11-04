const express = require('express');
const http = require('http');
const socketIO = require('socket.io');
const { Worker } = require('worker_threads');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIO(server);

app.use(express.static(path.join(__dirname, 'public')));
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  next();
});

const worker = new Worker('./rsa-worker.js');

io.on('connection', (socket) => {
  console.log('User connected:', socket.id);

  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id);
  });

  socket.on('chat message', (msg) => {
    // Encrypt the message using RSA in the worker thread
    worker.postMessage({ type: 'encrypt', message: msg }, [msg.buffer]);
  });

  worker.on('message', (encryptedMsg) => {
    // Send the encrypted message back to the frontend
    io.emit('chat message', encryptedMsg);
  });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
