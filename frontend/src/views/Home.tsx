import { useUser, USER_ROLES } from '../context/UserContext';
import Sidebar from '../components/Sidebar';
import ScheduleGrid from '../components/ScheduleGrid';
import ChatBot from '../components/ChatBot';
import { MOCK_USERS } from '../context/userConstants';
import '../styles/home.css';

function Home() {
  const { user, setUser } = useUser();

  if (!user) {
    return (
      <div className="login-prompt">
        <h2>Bienvenido a Asigna tu Ayudantía</h2>
        <p>Selecciona un rol para continuar:</p>
        <div className="login-buttons">
          <button onClick={() => setUser(MOCK_USERS[USER_ROLES.STUDENT])}>
            Entrar como Estudiante
          </button>
          <button onClick={() => setUser(MOCK_USERS[USER_ROLES.ASSISTANT])}>
            Entrar como Ayudante
          </button>
        </div>
      </div>
    );
  }

  const isAssistant = user.role === USER_ROLES.ASSISTANT;
  const roleLabel = isAssistant ? 'Ayudante' : 'Estudiante';

  return (
    <div className="home-layout">
      <Sidebar />
      <main className="home-main">
        <header className="home-header">
          <div className="welcome-section">
            <h2>Bienvenido, {user.name}</h2>
            <span className="user-role-badge">{roleLabel}</span>
          </div>
        </header>
        <section className="home-content">
          <ScheduleGrid />
        </section>
      </main>
      <ChatBot />
    </div>
  );
}

export default Home;
