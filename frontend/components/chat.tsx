import React, { useEffect, useRef, useState } from 'react';

const SOCKET_URL = 'ws://localhost:8000/ws';

const Chat = () => {
  const [messages, setMessages] = useState<string[]>([]);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(SOCKET_URL);
    ws.current.onmessage = (event) => {
      if (typeof event.data === 'string') {
        setMessages(msgs => [...msgs, event.data]);
      } else {
        // It's audio, play it
        const audioBlob = new Blob([event.data], { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        new Audio(audioUrl).play();
      }
    };
    return () => {
      ws.current?.close();
    };
  }, []);

  // Handle microphone and send audio data to backend (use utils/audio.ts for encoding)
  const handleRecord = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();
    mediaRecorder.ondataavailable = (e) => {
      if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.send(e.data);
      }
    };
    setTimeout(() => mediaRecorder.stop(), 5000); // Send 5 seconds of speech
  };

  return (
    <div>
      <button onClick={handleRecord}>Speak</button>
      <div>
        {messages.map((m, i) => (
          <div key={i}>{m}</div>
        ))}
      </div>
    </div>
  );
};

export default Chat;
