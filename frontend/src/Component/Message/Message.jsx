import React from 'react';
import './Message.css';

function Message({ text, sender }) {
  return (
    <div className={`message-container ${sender}`}>
      <div className={`message ${sender}`}>
        {text}
      </div>
    </div>
  );
}

export default Message;
