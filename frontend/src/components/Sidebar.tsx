import { useUser, USER_ROLES } from '../context/UserContext';
import type { UserRole } from '../context/userConstants';

export default function Sidebar() {
  const { user, logout, switchRole } = useUser();

  if (!user) return null;

  const isAssistant = user.role === USER_ROLES.ASSISTANT;

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-logo">Ayudantía</h1>
      </div>

      <nav className="sidebar-nav">
        <a href="#" className="sidebar-link active">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          Home
        </a>

        {isAssistant && (
          <div className="sidebar-section">
            <span className="sidebar-section-title">Mis asignaturas</span>
            {user.courses.map((course) => (
              <div key={course.id} className="sidebar-course">
                <span className="course-dot" style={{ backgroundColor: course.color }} />
                <span className="course-name">{course.name}</span>
              </div>
            ))}
          </div>
        )}
      </nav>

      <div className="sidebar-dev">
        <span className="dev-label">Modo desarrollo:</span>
        <select 
          value={user.role} 
          onChange={(e) => switchRole(e.target.value as UserRole)}
          className="dev-select"
        >
          <option value={USER_ROLES.STUDENT}>Estudiante</option>
          <option value={USER_ROLES.ASSISTANT}>Ayudante</option>
        </select>
      </div>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="user-avatar">{user.name.charAt(0)}</div>
          <div className="user-info">
            <span className="user-name">{user.name}</span>
            <span className="user-role">{isAssistant ? 'Ayudante' : 'Estudiante'}</span>
          </div>
        </div>
        <button className="sidebar-logout" onClick={logout}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
        </button>
      </div>
    </aside>
  );
}
