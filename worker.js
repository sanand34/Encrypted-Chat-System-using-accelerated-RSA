import {workerData, parentPort} from 'worker_threads';
import RSA from 'node-rsa';

function encrypt(message, publicKey) {
  const rsa = new RSA().importKey(publicKey);
  const encryptedMessage = rsa.encrypt(message, 'base64');
  return encryptedMessage;
}

function decrypt(encryptedMessage) {
  const privateKey = workerData.privateKey; // You may need to provide the private key in workerData
  const rsa = new RSA().importKey(privateKey);
  const decryptedMessage = rsa.decrypt(encryptedMessage, 'utf8');
  return decryptedMessage;
}

// Handle the encryption and decryption based on the action specified in workerData
if (workerData.action === 'encrypt') {
  const encryptedMessage = encrypt(workerData.message, workerData.publicKey);
  parentPort.postMessage({encryptedMessage});
} else if (workerData.action === 'decrypt') {
  const decryptedMessage = decrypt(workerData.encryptedMessage);
  parentPort.postMessage({decryptedMessage});
} else {
  throw new Error('Invalid action specified in workerData');
}
