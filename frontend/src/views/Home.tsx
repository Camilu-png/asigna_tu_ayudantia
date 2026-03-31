import { useUser, USER_ROLES } from "../context/UserContext";
import Sidebar from "../components/Sidebar";
import ScheduleGrid from "../components/ScheduleGrid";
import ChatBot from "../components/ChatBot";
import "../styles/home.css";

function Home() {
  const { user, sidebarCollapsed, selectedCourse } = useUser();

  if (!user) {
    return null;
  }

  const isAssistant = user.role === USER_ROLES.ASSISTANT;
  const roleLabel = isAssistant ? "Ayudante" : "Estudiante";

  return (
    <div className={`home-layout ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <Sidebar />
      <main className="home-main">
        <header className="home-header">
          <div className="welcome-section">
            {selectedCourse ? (
              <>
                <h2>{selectedCourse.name}</h2>
                <span className="course-code-badge">{selectedCourse.code}</span>
              </>
            ) : (
              <>
                <h2>Bienvenido, {user.name}</h2>
                <span className="user-role-badge">{roleLabel}</span>
              </>
            )}
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
