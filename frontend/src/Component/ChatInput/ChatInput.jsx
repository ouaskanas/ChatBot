import React, { useState } from 'react';
import './ChatInput.css';

function ChatInput({ onSend }) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();

    if (message.trim()) {
      onSend(message);
      setMessage('');
    }
  };

  return (
    <div className="chat-input-container">
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          value={message} 
          onChange={(e) => setMessage(e.target.value)} 
          placeholder="Type your message..." 
          className="chat-input"
        />
        <button type="submit" className="send-button">Envoyer</button>
      </form>
    </div>
  );
}

export default ChatInput;
