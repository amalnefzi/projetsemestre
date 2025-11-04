import React from 'react';
import axios from 'axios';
import { useQuery } from '@tanstack/react-query';

const api = axios.create({ baseURL: (import.meta as any).env?.VITE_API_URL || 'http://127.0.0.1:8001' });

type Destination = {
  id: number;
  title: string;
  description: string | null;
  avg_price_level: number | null;
  popularity_score: number | null;
  image_url: string | null;
  city?: { id: number; name: string };
};

export default function Destinations() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['destinations'],
    queryFn: async () => (await api.get<Destination[]>('/api/destinations/')).data,
  });

  if (isLoading) return <div>Chargement...</div>;
  if (error) return <div className="text-red-600">Erreur de chargement</div>;

  return (
    <div>
      <div className="hero bg-base-100 rounded-lg mb-6">
        <div className="hero-content text-center">
          <div className="max-w-md">
            <h1 className="text-5xl font-bold">🌍 Destinations</h1>
            <p className="py-6">Découvrez nos destinations populaires</p>
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
              <p className="text-sm opacity-70">{d.city?.name}</p>
              <p className="text-sm">{d.description}</p>
              <div className="card-actions justify-between items-center mt-4">
                <div className="badge badge-outline">Score: {d.popularity_score ?? '-'}</div>
                <div className="badge badge-secondary">Prix: {d.avg_price_level ?? '-'}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


