import './App.css'
import { UserProvider, useUser } from './context/UserContext'
import Home from './views/Home'
import Login from './views/Login'

function AppContent() {
  const { user, isLoading } = useUser();

  if (isLoading) {
    return null;
  }

  return user ? <Home /> : <Login />;
}

function App() {
  return(
    <UserProvider>
      <AppContent />
    </UserProvider>
  );
}

export default App
