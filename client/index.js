const socket = io('http://localhost:3030');
const gbi = elementId => document.getElementById(elementId); // alias

let backendRSA = null; // server side RSA variable
const frontendRSA = new window.RSA({b: 512}); // here we have access to the node-rsa module

const chat = gbi('chatRoom');
const input = gbi('input');
const button = gbi('button');

// helper function to transform collection of elements in array of elements
const fromCollectionToArray = collection => {
  const result = [];
  for (let i = 0; i < collection.length; i++) {
    result.push(collection[i]);
  }
  return result;
};

// remove all messages
const cleanChat = () => {
  const children = fromCollectionToArray(chat.children);
  children.forEach(child => chat.removeChild(child));
};

// create and append elements in the <div class="chat"></div>
const renderMessage = (authorId, message) => {
  const msgBox = document.createElement('div');
  msgBox.classList.add('messageBox');
  if (authorId === socket.id) msgBox.classList.add('mine');

  const msg = document.createElement('div');
  msg.classList.add('message');
  msg.textContent = message;

  msgBox.appendChild(msg);
  chat.appendChild(msgBox);
};

// clear the input value
const cleanInput = () => (input.value = '');
// send message to the server
const sendMessage = message => {
  if (backendRSA) {
    socket.emit('send-message', {
      message: backendRSA.encrypt(message).toString('base64'),
      id: socket.id,
    });
  }
  cleanInput();
};

// event handler
button.onclick = () => {
  const {value} = input;
  if (!!value) {
    sendMessage(value);
  }
};

// clear chat on connect
cleanChat();
setTimeout(() => {
  // get previous messages
  socket.emit('get-messages');
}, 500);
// get server side public key
socket.on('security', ({publicKey}) => {
  backendRSA = new window.RSA();
  backendRSA.importKey(publicKey);
  // send client public key
  socket.emit('security-response', {
    publicKey: frontendRSA.exportKey('public'),
    id: socket.id,
  });
});

// callback that runs when server receives a new message
socket.on('new-message', () => {
  // "ask" the server for all the messages
  socket.emit('get-messages');
});
// callback that runs when the server sends all the messages
socket.on('list-messages', messages => {
  // clear the chat
  cleanChat();
  if (messages.length > 0) {
    // reder every message
    messages.forEach(msg =>
      renderMessage(msg.authorId, frontendRSA.decrypt(msg.message).toString()),
    );
  }
});
