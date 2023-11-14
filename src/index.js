import express from 'express';
import http from 'http';
import RSA from 'node-rsa';
import {Server} from 'socket.io';
const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: '*',
  },
});
app.get('/', (req, res) => res.send('working...'));
let users = [];
let messages = [];

const backendRSA = new RSA({b: 512}); // server side public and private RSA keys

// runs every time a new client connects
io.on('connection', socket => {
  // seding the server side public key
  socket.emit('security', {publicKey: backendRSA.exportKey('public')});

  // callback that runs when the client sends a message
  socket.on('send-message', ({message, id}) => {
    messages.push({
      message: backendRSA.decrypt(message).toString(),
      authorId: id,
    });
    console.log(`User with id "${id}" sent the message:\n${message}\n`);

    // alert all sockets that a new message was sent
    io.emit('new-message');
  });

  // callback that runs when the client sends its public key
  socket.on('security-response', ({publicKey, id}) => {
    const frontPublicRSA = new RSA();
    users.push({
      id,
      rsa: frontPublicRSA.importKey(publicKey),
    });
  });

  // callback that runs when the client asks for all the messages
  socket.on('get-messages', () => {
    const targetUser = users.find(user => user.id === socket.id);
    if (targetUser) {
      // send all the messages for the client encryted with its public key
      socket.emit(
        'list-messages',
        messages.map(m => ({
          ...m,
          message: targetUser.rsa.encrypt(m.message).toString('base64'),
        })),
      );
    }
  });

  // callback that runs when the client disconnects
  socket.on('disconnect', () => {
    const targetIndex = users.findIndex(user => user.id === socket.id);
    if (targetIndex !== -1) {
      users = [
        ...users.slice(0, targetIndex),
        ...users.slice(targetIndex + 1, users.length),
      ];
    }
  });
});

server.listen(3030, () => console.log('server running'));
