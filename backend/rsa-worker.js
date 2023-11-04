const { parentPort, workerData } = require('worker_threads');
const NodeRSA = require('node-rsa');

const key = new NodeRSA({ b: 512 });

parentPort.on('message', (message) => {
  if (message.type === 'encrypt') {
    // Encrypt the message using the public key
    const encryptedMsg = key.encrypt(message.message.toString('base64'), 'base64');
    parentPort.postMessage(encryptedMsg);
  }
});
