import React, { useState } from "react";
import ChatInput from "../ChatInput/ChatInput";
import Message from "../Message/Message";
import './Chat.css';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [filename, setFilename] = useState('');
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [initialQuestions, setInitialQuestions] = useState([]);
  const [level, setLevel] = useState(0);
  const [subLevel, setSubLevel] = useState(0);
  const [error, setError] = useState(null);
  const [interviewCompleted, setInterviewCompleted] = useState(false);

  const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const handleSend = async (message) => {
    setMessages((prevMessages) => [...prevMessages, { text: message, sender: 'user' }]);
    
    await delay(3000); // Ajout d'une latence de 3 secondes
  
    const url = 'http://localhost:5000/interview';
    const body = {
      user_input: message,
      level,
      sub_level: subLevel,
      filename: filename,
      question: currentQuestion,
      answer: message,
      name: "",  // Assurez-vous d'inclure un champ 'name' même s'il est vide
      domain: "",  // Assurez-vous d'inclure un champ 'domain' même s'il est vide
      initial_questions: initialQuestions,
    };
  
    console.log('Sending data to server:', body);  // Log des données envoyées
  
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });
  
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
  
      const data = await response.json();
      console.log('Success:', data);
  
      if (data.error) {
        setError(data.error);
        setMessages((prevMessages) => [...prevMessages, { text: data.error, sender: 'bot' }]);
      } else {
        setError(null);
        if (data.filename) setFilename(data.filename);
        if (data.question) {
          setCurrentQuestion(data.question);
          setInitialQuestions(data.initial_questions || []);
          setMessages((prevMessages) => [...prevMessages, { text: data.question, sender: 'bot' }]);
          setLevel(data.level || level);
          setSubLevel(data.sub_level || subLevel);
        } else if (data.message) {
          setMessages((prevMessages) => [...prevMessages, { text: data.message, sender: 'bot' }]);
          setLevel(data.level);
          setSubLevel(data.sub_level || subLevel);
          if (data.level === 2) {
            setInterviewCompleted(true); // Marquer l'entretien comme terminé
          }
        }
      }
    } catch (error) {
      setError('Une erreur est survenue. Veuillez réessayer.');
      setMessages((prevMessages) => [...prevMessages, { text: 'Une erreur est survenue. Veuillez réessayer.', sender: 'bot' }]);
    }
  };
  

  return (
    <>
      <div className="Chat">
        <div className="message-container">
          <Message text="Bonjour ! Je suis votre assistant d'entretien. Pour commencer, pourriez-vous vous présenter ?" sender="bot" />
          {messages.map((msg, index) => (
            <Message key={index} text={msg.text} sender={msg.sender} />
          ))}
        </div>
        {error && <div className="error">{error}</div>}
      </div>
      {!interviewCompleted && <ChatInput onSend={handleSend} />} {/* Désactiver le ChatInput si l'entretien est terminé */}
    </>
  );
}

export default Chat;
