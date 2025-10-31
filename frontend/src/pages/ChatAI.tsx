import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useMutation } from '@tanstack/react-query';

// ✅ Django tourne sur 8001 (avec Llama + Scraping intégré)
const api = axios.create({ 
  baseURL: 'http://127.0.0.1:8001'  // Django avec tout intégré
});

type ChatMessage = {
  id: number;
  type: 'user' | 'ai';
  message: string;
  timestamp: Date;
};

type SimpleAnnonce = {
  nom: string;
  prix: number;
  note: number;
  lien: string;
  source: string;
}; 

type ChatResponse = {
  ai_response: string;
  annonces: SimpleAnnonce[]; 
  detected_preferences: {
    budget: string | null;
    interests: string[];
    destination: string | null;
  };
};

export default function ChatAI() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      type: 'ai',
      message: "Bonjour ! 👋 Je suis votre assistant voyage. Dites-moi ce que vous recherchez : votre budget, vos intérêts, ou une destination qui vous fait rêver !",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [annoncesList, setAnnoncesList] = useState<SimpleAnnonce[]>([]);
  const [detectedPrefs, setDetectedPrefs] = useState<any>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll vers le bas
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      // ✅ Endpoint du scraping et de l'IA combinée
      const response = await api.post<ChatResponse>('/api/intelligent_travel_chat/', {
        message,
        user_id: 1
      });
      return response.data;
    },
    onSuccess: (data) => {
      // Ajouter la réponse de l'IA
      const aiMessage: ChatMessage = {
        id: Date.now(),
        type: 'ai',
        message: data.ai_response,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
      // Mettre à jour les annonces
      if (data.annonces && Array.isArray(data.annonces) && data.annonces.length > 0) {
        setAnnoncesList(data.annonces);
      }
      
      // Afficher les préférences détectées
      if (data.detected_preferences) {
        setDetectedPrefs(data.detected_preferences);
      }
    },
    onError: (error: any) => {
      console.error('❌ Erreur chat:', error);
      
      // Message d'erreur plus informatif
      let errorMsg = "Désolé, une erreur s'est produite. ";
      
      if (error.response) {
        // Le serveur a répondu avec un code d'erreur
        errorMsg += `Erreur ${error.response.status}: ${error.response.statusText}`;
        if (error.response.data?.error) {
          errorMsg += ` - ${error.response.data.error}`;
        }
      } else if (error.request) {
        // La requête a été faite mais aucune réponse reçue
        errorMsg += "Le serveur Django ne répond pas. Assurez-vous qu'il est démarré sur le port 8001. 🤔";
      } else {
        // Erreur lors de la configuration de la requête
        errorMsg += error.message || "Erreur de connexion";
      }
      
      const errorMessage: ChatMessage = {
        id: Date.now(),
        type: 'ai',
        message: errorMsg,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  });

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      type: 'user',
      message: inputMessage,
      timestamp: new Date()
    };

    // Ajouter le message utilisateur
    setMessages(prev => [...prev, userMessage]);

    // Envoyer seulement le dernier message (pas tout l'historique)
    chatMutation.mutate(inputMessage);

    // Réinitialiser l'input
    setInputMessage('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleResetChat = async () => {
    try {
      await api.post('/reset', { user_id: 1 });
      setMessages([{
        id: 1,
        type: 'ai',
        message: "Conversation réinitialisée ! Comment puis-je vous aider ? 😊",
        timestamp: new Date()
      }]);
      setAnnoncesList([]);
      setDetectedPrefs({});
    } catch (error) {
      console.error('Erreur reset:', error);
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-4">
      <div className="hero bg-gradient-to-r from-primary to-secondary text-primary-content rounded-lg mb-6">
        <div className="hero-content text-center py-8">
          <div className="max-w-md">
            <h1 className="text-5xl font-bold">🤖 Chat IA</h1>
            <p className="py-4">Votre assistant voyage intelligent</p>
            <button 
              onClick={handleResetChat}
              className="btn btn-sm btn-ghost"
            >
              🔄 Nouvelle conversation
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat principal */}
        <div className="lg:col-span-2 card bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title">💬 Conversation</h2>
            <div className="h-[500px] overflow-y-auto space-y-4 p-4 bg-base-200 rounded">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`chat ${msg.type === 'user' ? 'chat-end' : 'chat-start'}`}
                >
                  <div className="chat-header mb-1">
                    {msg.type === 'user' ? 'Vous' : '🤖 Assistant'}
                    <time className="text-xs opacity-50 ml-2">
                      {msg.timestamp.toLocaleTimeString('fr-FR', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </time>
                  </div>
                  <div className={`chat-bubble ${
                    msg.type === 'user' 
                      ? 'chat-bubble-primary' 
                      : 'chat-bubble-secondary'
                  }`}>
                    {msg.message}
                  </div>
                </div>
              ))}
              {chatMutation.isPending && (
                <div className="chat chat-start">
                  <div className="chat-bubble chat-bubble-secondary">
                    <span className="loading loading-dots loading-sm"></span>
                    L'IA réfléchit...
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            
            <div className="card-actions mt-4">
              <div className="join w-full">
                <input
                  type="text"
                  placeholder="Tapez votre message..."
                  className="input input-bordered join-item flex-1"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={chatMutation.isPending}
                />
                <button
                  className="btn btn-primary join-item"
                  onClick={handleSendMessage}
                  disabled={chatMutation.isPending || !inputMessage.trim()}
                >
                  Envoyer 📤
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Colonne droite : Préférences + Recommandations */}
        <div className="space-y-6">
          {/* Préférences détectées */}
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title text-sm">🎯 Préférences détectées</h2>
              <div className="space-y-2">
                {detectedPrefs.budget && (
                  <div className="badge badge-primary gap-2">
                    💰 {detectedPrefs.budget}
                  </div>
                )}
                {detectedPrefs.destination && (
                  <div className="badge badge-secondary gap-2">
                    📍 {detectedPrefs.destination}
                  </div>
                )}
                {detectedPrefs.interests && detectedPrefs.interests.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {detectedPrefs.interests.map((interest: string, i: number) => (
                      <div key={i} className="badge badge-accent badge-sm">
                        {interest}
                      </div>
                    ))}
                  </div>
                )}
                {!detectedPrefs.budget && !detectedPrefs.destination && (
                  <p className="text-xs text-gray-500">
                    Discutez pour que je comprenne vos besoins...
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Recommandations */}
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title text-sm">✨ Offres trouvées</h2>
              <div className="space-y-3 max-h-[400px] overflow-y-auto">
                {annoncesList.length > 0 ? (
                  annoncesList.map((annonce, index) => (
                    <div key={index} className="card bg-base-200 shadow-sm">
                      <div className="card-body p-3">
                        <h4 className="font-bold text-sm">{annonce.nom}</h4>
                        <div className="flex justify-between items-center text-xs">
                          <span className="badge badge-success">{annonce.prix} DT</span>
                          <span>⭐ {annonce.note}</span>
                        </div>
                        <a 
                          href={annonce.lien} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="link link-primary text-xs"
                        >
                          Voir sur {annonce.source} →
                        </a>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    <p className="text-xs">💭 Parlez-moi de vos envies de voyage pour voir des offres !</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Suggestions rapides */}
      <div className="mt-6">
        <h3 className="text-sm font-semibold mb-3">💡 Suggestions rapides :</h3>
        <div className="flex flex-wrap gap-2">
          {[
            "Je cherche un voyage pas cher",
            "Je veux aller à la plage cet été",
            "Je préfère la culture et les musées",
            "Voyage de luxe à Paris",
            "Nature et randonnée en montagne"
          ].map((suggestion) => (
            <button
              key={suggestion}
              className="btn btn-outline btn-sm"
              onClick={() => setInputMessage(suggestion)}
              disabled={chatMutation.isPending}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}