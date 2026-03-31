import { useUser, USER_ROLES } from '../context/UserContext';

export default function Sidebar() {
  const { user, logout, sidebarCollapsed, toggleSidebar } = useUser();

  if (!user) return null;

  const isAssistant = user.role === USER_ROLES.ASSISTANT;

  return (
    <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        {!sidebarCollapsed && <h1 className="sidebar-logo">Ayudantía</h1>}
        <button className="sidebar-toggle" onClick={toggleSidebar} title={sidebarCollapsed ? 'Expandir' : 'Colapsar'}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {sidebarCollapsed ? (
              <path d="M9 18l6-6-6-6"/>
            ) : (
              <path d="M15 18l-6-6 6-6"/>
            )}
          </svg>
        </button>
      </div>

      <nav className="sidebar-nav">
        <a href="#" className="sidebar-link active">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          {!sidebarCollapsed && <span>Home</span>}
        </a>

        {isAssistant && !sidebarCollapsed && (
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

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="user-avatar">{user.name.charAt(0)}</div>
          {!sidebarCollapsed && (
            <div className="user-info">
              <span className="user-name">{user.name}</span>
              <span className="user-role">{isAssistant ? 'Ayudante' : 'Estudiante'}</span>
            </div>
          )}
        </div>
        <button className="sidebar-logout" onClick={logout} title="Cerrar sesión">
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
