export interface User {
  id: number;
  email: string;
  name: string;
  profile_image: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
