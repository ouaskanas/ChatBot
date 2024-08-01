import React from 'react';
import Chat from './Component/Chat/Chat';
import './App.css';

function App() {
  return (
    <div className="App">
      <h1 className="app-header">Interview Chat</h1>
      <div className="chat-container">
        <Chat />
      </div>
    </div>
  );
}

export default App;
