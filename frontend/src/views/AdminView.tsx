import { useState, useEffect } from 'react';
import { useUser } from '../context/UserContext';
import { adminApi, type DashboardData } from '../api/admin';

type Tab = 'users' | 'courses';

export default function AdminView() {
  const { token } = useUser();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>('users');
  const [assignMode, setAssignMode] = useState<number | null>(null);
  const [selectedUser, setSelectedUser] = useState<number | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const dashboardData = await adminApi.getDashboard(token);
      setData(dashboardData);
    } catch (err) {
      console.error('Error loading dashboard:', err);
      setError('Error loading dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleAssignAssistant = async (courseId: number, userId: number) => {
    if (!confirm('Assign this user as assistant to the course?')) return;
    
    try {
      setActionLoading(true);
      await adminApi.assignAssistant(token, courseId, userId);
      await loadDashboard();
      setAssignMode(null);
      setSelectedUser(null);
    } catch (err) {
      console.error('Error assigning assistant:', err);
      alert('Error assigning assistant');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRemoveAssistant = async (courseId: number, userId: number) => {
    if (!confirm('Remove this assistant from the course?')) return;
    
    try {
      setActionLoading(true);
      await adminApi.removeAssistant(token, courseId, userId);
      await loadDashboard();
    } catch (err) {
      console.error('Error removing assistant:', err);
      alert('Error removing assistant');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!confirm('Delete this user? This cannot be undone.')) return;
    
    try {
      setActionLoading(true);
      await adminApi.deleteUser(token, userId);
      await loadDashboard();
    } catch (err) {
      console.error('Error deleting user:', err);
      alert('Error deleting user');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <p style={{ color: 'red' }}>{error}</p>
        <button onClick={loadDashboard}>Retry</button>
      </div>
    );
  }

  if (!data) {
    return <div style={{ padding: '20px' }}>No data available</div>;
  }

  const assistants = data.help_blocks;
  const availableUsers = data.users.filter(
    (u) => !assistants.some((a) => a.assistant_id === u.id)
  );

  return (
    <div style={{ padding: '20px' }}>
      <h1>Admin Dashboard</h1>
      
      <div style={{ marginBottom: '20px', padding: '10px', background: '#f5f5f5', borderRadius: '4px' }}>
        <h3>Stats</h3>
        <p>Total Users: {data.stats.total_users}</p>
        <p>Total Courses: {data.stats.total_courses}</p>
        <p>Total Students: {data.stats.total_students}</p>
        <p>Total Assistants: {data.stats.total_assistants}</p>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <button
          onClick={() => setActiveTab('users')}
          style={{ marginRight: '10px', padding: '8px 16px', fontWeight: activeTab === 'users' ? 'bold' : 'normal' }}
        >
          Users
        </button>
        <button
          onClick={() => setActiveTab('courses')}
          style={{ padding: '8px 16px', fontWeight: activeTab === 'courses' ? 'bold' : 'normal' }}
        >
          Courses
        </button>
      </div>

      {activeTab === 'users' && (
        <div>
          <h2>Users</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #ccc' }}>
                <th style={{ textAlign: 'left', padding: '8px' }}>ID</th>
                <th style={{ textAlign: 'left', padding: '8px' }}>Name</th>
                <th style={{ textAlign: 'left', padding: '8px' }}>Email</th>
                <th style={{ textAlign: 'left', padding: '8px' }}>Role</th>
                <th style={{ textAlign: 'left', padding: '8px' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.users.map((user) => (
                <tr key={user.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '8px' }}>{user.id}</td>
                  <td style={{ padding: '8px' }}>{user.name}</td>
                  <td style={{ padding: '8px' }}>{user.email}</td>
                  <td style={{ padding: '8px' }}>{user.role}</td>
                  <td style={{ padding: '8px' }}>
                    {user.role !== 'ADMIN' && (
                      <button
                        onClick={() => handleDeleteUser(user.id)}
                        disabled={actionLoading}
                        style={{ color: 'red' }}
                      >
                        Delete
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'courses' && (
        <div>
          <h2>Courses</h2>
          {data.courses.map((course) => {
            const courseAssistants = assistants.filter((a) => a.course_id === course.id);
            const isAssignMode = assignMode === course.id;

            return (
              <div
                key={course.id}
                style={{
                  marginBottom: '20px',
                  padding: '15px',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                }}
              >
                <h3>
                  {course.code}: {course.name}
                </h3>
                <p>Professor: {course.professor}</p>
                <p>Credits: {course.credits}</p>

                <h4>Assistants:</h4>
                {courseAssistants.length === 0 ? (
                  <p>No assistants assigned</p>
                ) : (
                  <ul>
                    {courseAssistants.map((a) => (
                      <li key={a.id}>
                        {a.assistant_name}
                        <button
                          onClick={() => handleRemoveAssistant(course.id, a.assistant_id)}
                          disabled={actionLoading}
                          style={{ marginLeft: '10px', color: 'red' }}
                        >
                          Remove
                        </button>
                      </li>
                    ))}
                  </ul>
                )}

                {isAssignMode ? (
                  <div style={{ marginTop: '10px' }}>
                    <select
                      onChange={(e) => setSelectedUser(Number(e.target.value))}
                      defaultValue=""
                    >
                      <option value="" disabled>
                        Select user
                      </option>
                      {availableUsers.map((u) => (
                        <option key={u.id} value={u.id}>
                          {u.name} ({u.email})
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={() => selectedUser && handleAssignAssistant(course.id, selectedUser)}
                      disabled={!selectedUser || actionLoading}
                      style={{ marginLeft: '10px' }}
                    >
                      Confirm
                    </button>
                    <button
                      onClick={() => {
                        setAssignMode(null);
                        setSelectedUser(null);
                      }}
                      disabled={actionLoading}
                      style={{ marginLeft: '10px' }}
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setAssignMode(course.id)}
                    disabled={availableUsers.length === 0}
                    style={{ marginTop: '10px' }}
                  >
                    + Add Assistant
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}