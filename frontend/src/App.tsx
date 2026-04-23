import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { UserProvider, useUser } from "./context/UserContext";
import Home from "./views/Home";
import Login from "./views/Login";
import CourseView from "./views/CourseView";
import AdminView from "./views/AdminView";

function AdminRoute() {
  const { user, token } = useUser();
  
  if (!token) {
    return <Navigate to="/home" replace />;
  }
  
  return user?.role === 'admin' || user?.role === 'ADMIN' ? <AdminView /> : <Navigate to="/home" replace />;
}

function AppContent() {
  const { user, isLoading } = useUser();

  if (isLoading) {
    return null;
  }

  return user ? (
    <Routes>
      <Route path="/home" element={<Home />} />
      <Route path="/courses/:id" element={<CourseView />} />
      <Route path="/admin" element={<AdminRoute />} />
      <Route path="*" element={<Navigate to="/home" replace />} />
    </Routes>
  ) : (
    <Login />
  );
}

function App() {
  return (
    <BrowserRouter>
      <UserProvider>
        <AppContent />
      </UserProvider>
    </BrowserRouter>
  );
}

export default App;
