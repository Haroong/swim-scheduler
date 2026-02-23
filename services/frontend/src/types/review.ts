export interface Review {
  id: number;
  facility_id: number;
  nickname: string;
  rating: number;
  content: string;
  created_at: string | null;
  updated_at: string | null;
}

export interface ReviewStats {
  facility_id: number;
  average_rating: number;
  review_count: number;
}

export interface ReviewCreatePayload {
  facility_id: number;
  nickname: string;
  password: string;
  rating: number;
  content: string;
}

export interface ReviewUpdatePayload {
  password: string;
  rating?: number;
  content?: string;
}
