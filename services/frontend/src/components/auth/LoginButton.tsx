import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../../contexts/AuthContext';

export default function LoginButton() {
  const { login } = useAuth();

  return (
    <GoogleLogin
      onSuccess={async (response) => {
        if (response.credential) {
          await login(response.credential);
        }
      }}
      onError={() => {
        console.error('Google login failed');
      }}
      size="medium"
      theme="filled_blue"
      shape="pill"
      text="signin"
    />
  );
}
