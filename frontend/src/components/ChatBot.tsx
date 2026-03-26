import { useState, useRef, useEffect } from 'react';

interface Message {
  id: number;
  role: 'assistant' | 'user';
  text: string;
}

let messageId = 1;

const INITIAL_MESSAGES: Message[] = [
  { id: 1, role: 'assistant', text: '¡Hola! Soy tu asistente de horario. ¿En qué puedo ayudarte hoy?' }
];

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: ++messageId,
      role: 'user',
      text: input.trim()
    };

    setMessages([...messages, userMessage]);
    setInput('');

    setTimeout(() => {
      const response = generateResponse(userMessage.text);
      setMessages(prev => [...prev, response]);
    }, 500);
  };

  const generateResponse = (text: string): Message => {
    const lowerText = text.toLowerCase();
    let responseText = 'Entiendo tu consulta. Puedo ayudarte con información sobre tu horario, asignaturas o preferencias. ¿Podrías ser más específico?';

    if (lowerText.includes('horario') || lowerText.includes('hora')) {
      responseText = 'Tu horario muestra las clases que tienes programadas. Puedes agregar bloques haciendo clic en las celdas del horario. Los bloques de color representan tus asignaturas.';
    } else if (lowerText.includes('asignatura') || lowerText.includes('curso')) {
      responseText = 'Las asignaturas se muestran en la sidebar (si eres ayudante) y en el horario con colores. Puedes crear nuevas asignaturas al agregar un bloque al horario.';
    } else if (lowerText.includes('color')) {
      responseText = 'Cada asignatura tiene un color único que la identifica en el horario. Puedes personalizar el color al crear una nueva asignatura.';
    } else if (lowerText.includes('hola') || lowerText.includes('buenos')) {
      responseText = '¡Hola de nuevo! ¿En qué puedo ayudarte con tu horario?';
    } else if (lowerText.includes('gracias')) {
      responseText = '¡De nada! Estoy aquí para ayudarte. ¿Necesitas algo más?';
    }

    return {
      id: ++messageId,
      role: 'assistant',
      text: responseText
    };
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={`chatbot ${isOpen ? 'open' : ''}`}>
      {isOpen ? (
        <div className="chatbot-panel">
          <div className="chatbot-header">
            <div className="chatbot-title">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
              Asistente IA
            </div>
            <button className="chatbot-close" onClick={() => setIsOpen(false)}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <div className="chatbot-messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`chatbot-message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'assistant' ? 'AI' : 'T'}
                </div>
                <div className="message-content">{msg.text}</div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div className="chatbot-input">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Escribe tu consulta..."
            />
            <button className="chatbot-send" onClick={handleSend}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </div>
        </div>
      ) : (
        <button className="chatbot-fab" onClick={() => setIsOpen(true)}>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </button>
      )}
    </div>
  );
}
