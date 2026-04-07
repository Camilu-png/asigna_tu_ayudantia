import { useState } from "react";
import { useUser, USER_ROLES } from "../context/UserContext";
import Sidebar from "../components/Sidebar";
import ScheduleGrid from "../components/ScheduleGrid";
import ChatBot from "../components/ChatBot";
import { runSolver } from "../api/schedule";
import "../styles/home.css";

function CourseView() {
  const { user, sidebarCollapsed, selectedCourse } = useUser();
  const [solving, setSolving] = useState(false);
  // TODO: Use solverResult to display colored solutions in ScheduleGrid
  const [, setSolverResult] = useState<{
    success: boolean;
    message: string;
    fitness: number;
  } | null>(null);

  if (!user) {
    return null;
  }

  const isAssistant = user.role === USER_ROLES.ASSISTANT;
  const roleLabel = isAssistant ? "Ayudante" : "Estudiante";

  const handleSolve = async () => {
    if (!selectedCourse) return;
    
    setSolving(true);
    setSolverResult(null);
    
    try {
      const result = await runSolver(selectedCourse.id, true);
      setSolverResult(result);
      
      if (result.success) {
        alert(`Horario generado. Fitness: ${result.fitness}`);
      } else {
        alert(result.message);
      }
    } catch (error) {
      console.error("Solver error:", error);
      alert("Error al generar el horario");
    } finally {
      setSolving(false);
    }
  };

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
          {isAssistant && selectedCourse && (
            <button 
              onClick={handleSolve} 
              disabled={solving}
              className="solve-button"
            >
              {solving ? "Generando..." : "Generar Horario"}
            </button>
          )}
        </header>
        <section className="home-content">
          <ScheduleGrid />
        </section>
      </main>
      <ChatBot />
    </div>
  );
}

export default CourseView;
