import React from 'react';
import axios from 'axios';
import { useQuery } from '@tanstack/react-query';

const api = axios.create({ baseURL: (import.meta as any).env?.VITE_API_URL || 'http://127.0.0.1:8001' });

type Rec = {
  id: number;
  title: string;
  description: string | null;
  avg_price_level: number | null;
  popularity_score: number | null;
  image_url: string | null;
};

export default function Recommendations() {
  const userId = 1; // à remplacer par l'ID utilisateur connecté
  const { data, isLoading, error } = useQuery({
    queryKey: ['reco', userId],
    queryFn: async () => (await api.get<Rec[]>(`/api/recommendations/?user_id=${userId}`)).data,
  });

  if (isLoading) return <div>Chargement...</div>;
  if (error) return <div className="text-red-600">Erreur de chargement</div>;

  return (
    <div>
      <div className="hero bg-gradient-to-r from-primary to-secondary text-primary-content rounded-lg mb-6">
        <div className="hero-content text-center">
          <div className="max-w-md">
            <h1 className="text-5xl font-bold">🎯 Recommandations</h1>
            <p className="py-6">Destinations personnalisées selon vos préférences</p>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {data?.map((d) => (
          <div key={d.id} className="card bg-base-100 shadow-xl">
            {d.image_url && (
              <figure>
                <img src={d.image_url} alt={d.title} className="w-full h-48 object-cover" />
              </figure>
            )}
            <div className="card-body">
              <h2 className="card-title">{d.title}</h2>
              <p className="text-sm">{d.description}</p>
              <div className="card-actions justify-end mt-4">
                <div className="badge badge-primary">Score: {d.popularity_score ?? '-'}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


