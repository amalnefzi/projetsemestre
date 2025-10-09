import React, { useState } from 'react';
import axios from 'axios';
import { useMutation } from '@tanstack/react-query';

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000' });

type ChatMessage = {
  id: number;
  type: 'user' | 'ai';
  message: string;
  timestamp: Date;
};

// NOTE IMPORTANTE : Ce type a été simplifié pour correspondre au format de votre backend
// qui envoie des listes de chaînes ('annonces'), et non des objets structurés.
type SimpleAnnonce = {
  nom: string;
  prix: number;
  note: number;
  lien: string;
  source: string;
}; 

type ChatResponse = {
  ai_response: string;
  // 👈 CORRECTION : on attend 'annonces' (une liste de chaînes) et non 'recommendations'
  annonces: SimpleAnnonce[]; 
  detected_preferences: {
    budget: string;
    interests: string[];
    destination: string | null;
  };
};

export default function ChatAI() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      type: 'ai',
      message: "Bonjour ! Je suis votre assistant voyage IA. Dites-moi ce que vous cherchez : budget, intérêts, destination...",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  // 👈 CORRECTION : État renommé et typé comme liste de chaînes pour les annonces
  const [annoncesList, setAnnoncesList] = useState<SimpleAnnonce[]>([]); 

  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
// ChatAI.tsx - Ligne importante
    const response = await api.post<ChatResponse>('/api/chat/', {  // ← Bonne URL
        message,
        user_id: 1
    });
      return response.data;
    },
// Dans la partie onSuccess de useMutation
onSuccess: (data) => {
  // Ajouter la réponse de l'IA
  const aiMessage: ChatMessage = {
    id: Date.now(),
    type: 'ai',
    message: data.ai_response,
    timestamp: new Date()
  };
  
  setMessages(prev => [...prev, aiMessage]);
  
  // DEBUG: Afficher les données reçues
  console.log("Données reçues du backend:", data);
  
  // 👈 CORRECTION: Vérification plus robuste
  if (data.annonces && Array.isArray(data.annonces) && data.annonces.length > 0) {
    setAnnoncesList(data.annonces);
  } else {
    setAnnoncesList([]); // Réinitialiser si pas d'annonces
  }
},
    onError: (error) => {
      console.error('Erreur chat:', error);
      const errorMessage: ChatMessage = {
        id: Date.now(),
        type: 'ai',
        message: "Désolé, une erreur s'est produite. Pouvez-vous réessayer ?",
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

  // Crée un tableau combiné pour le prompt complet
  const updatedMessages = [...messages, userMessage];

  // 🧠 Construire un prompt complet avec historique + message actuel
  const fullPrompt =
    "Tu es un assistant de voyage intelligent. Réponds de façon naturelle, utile et concise.\n\n" +
    updatedMessages
      .map(m => `${m.type === 'user' ? 'Utilisateur' : 'Assistant'}: ${m.message}`)
      .join('\n') +
    `\nAssistant:`;

  // Met à jour les messages à l'écran
  setMessages(updatedMessages);

  // Envoie au backend
  chatMutation.mutate(fullPrompt);

  // Réinitialise l'input
  setInputMessage('');
};

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="hero bg-gradient-to-r from-primary to-secondary text-primary-content rounded-lg mb-6">
        <div className="hero-content text-center">
          <div className="max-w-md">
            <h1 className="text-5xl font-bold">🤖 Chat IA</h1>
            <p className="py-6">Parlez avec votre assistant voyage intelligent</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chat */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title">💬 Conversation</h2>
            <div className="h-96 overflow-y-auto space-y-4 p-4 bg-base-200 rounded">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`chat ${msg.type === 'user' ? 'chat-end' : 'chat-start'}`}
                >
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
            </div>
            
            <div className="card-actions">
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
                  Envoyer
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Recommandations */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title">🎯 Recommandations IA</h2>
            <div className="space-y-4">
            {annoncesList.length > 0 ? (
                annoncesList.map((annonce, index) => (
                  <div key={index} className="card bg-base-200 shadow">
                    <div className="card-body p-4">
                      <h4 className="font-bold">{annonce.nom}</h4>
                      <p>Prix : {annonce.prix} DT</p>
                      <p>Note : {annonce.note} ⭐</p>
                      <a href={annonce.lien} target="_blank" rel="noopener noreferrer" className="link link-primary">
                        Voir l'annonce ({annonce.source})
                      </a>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <p>💭 Commencez une conversation pour voir les recommandations</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Suggestions rapides */}
      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-4">💡 Suggestions rapides :</h3>
        <div className="flex flex-wrap gap-2">
          {[
            "Je cherche un voyage pas cher",
            "Je veux aller à la plage",
            "Je préfère la culture et les musées",
            "Budget luxe pour Paris",
            "Nature et randonnée"
          ].map((suggestion) => (
            <button
              key={suggestion}
              className="btn btn-outline btn-sm"
              onClick={() => setInputMessage(suggestion)}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}