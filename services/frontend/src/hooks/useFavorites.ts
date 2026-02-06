import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'swim-favorites';

export function useFavorites() {
  const [favorites, setFavorites] = useState<number[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  // localStorage에 저장
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(favorites));
    } catch (e) {
      console.error('Failed to save favorites:', e);
    }
  }, [favorites]);

  const toggleFavorite = useCallback((facilityId: number) => {
    setFavorites((prev) =>
      prev.includes(facilityId)
        ? prev.filter((id) => id !== facilityId)
        : [...prev, facilityId]
    );
  }, []);

  const isFavorite = useCallback(
    (facilityId: number) => favorites.includes(facilityId),
    [favorites]
  );

  return { favorites, toggleFavorite, isFavorite };
}
