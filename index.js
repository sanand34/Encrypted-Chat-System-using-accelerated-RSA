import express from 'express';
import http from 'http';
import {Worker} from 'worker_threads';
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

// Function to create a worker thread
function createWorker(workerData) {
  return new Promise((resolve, reject) => {
    const worker = new Worker('./worker.js', {workerData});

    worker.on('message', resolve);
    worker.on('error', reject);
    worker.on('exit', code => {
      if (code !== 0)
        reject(new Error(`Worker stopped with exit code ${code}`));
    });
  });
}

// Encryption worker
async function encryptMessage(message, publicKey) {
  const result = await createWorker({message, publicKey, action: 'encrypt'});
  return result.encryptedMessage;
}

// Decryption worker
async function decryptMessage(encryptedMessage) {
  const result = await createWorker({encryptedMessage, action: 'decrypt'});
  return result.decryptedMessage;
}

// runs every time a new client connects
io.on('connection', socket => {
  // sending the server side public key
  socket.emit('security', {publicKey: backendRSA.exportKey('public')});

  // callback that runs when the client sends a message
  socket.on('send-message', async ({message, id}) => {
    const decryptedMessage = await decryptMessage(message);
    messages.push({
      message: decryptedMessage,
      authorId: id,
    });
    console.log(
      `User with id "${id}" sent the message:\n${decryptedMessage}\n`,
    );

    // alert all sockets that a new message was sent
    io.emit('new-message');
  });

  // callback that runs when the client sends its public key
  socket.on('security-response', ({publicKey, id}) => {
    users.push({
      id,
      rsa: new RSA().importKey(publicKey),
    });
  });

  // callback that runs when the client asks for all the messages
  socket.on('get-messages', async () => {
    const targetUser = users.find(user => user.id === socket.id);
    if (targetUser) {
      // send all the messages for the client encrypted with its public key
      const encryptedMessages = await Promise.all(
        messages.map(async m => ({
          ...m,
          message: await encryptMessage(m.message, targetUser.rsa),
        })),
      );
      socket.emit('list-messages', encryptedMessages);
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

server.listen(3000, () => console.log('server running'));
