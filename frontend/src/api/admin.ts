import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

export interface Course {
  id: number;
  name: string;
  code: string;
  professor: string;
  credits: number;
}

export interface Enrollment {
  user_id: number;
  user_name: string;
  course_id: number;
  course_name: string;
  role: string;
  color: string;
}

export interface HelpBlock {
  id: number;
  assistant_id: number;
  assistant_name: string;
  course_id: number;
  course_name: string;
  color: string;
}

export interface DashboardData {
  users: User[];
  courses: Course[];
  enrollments: Enrollment[];
  help_blocks: HelpBlock[];
  stats: {
    total_users: number;
    total_courses: number;
    total_students: number;
    total_assistants: number;
  };
}

function getAuthHeaders(token: string | null) {
  return {
    headers: {
      Authorization: token ? `Bearer ${token}` : '',
    },
  };
}

export const adminApi = {
  getDashboard: async (token: string | null): Promise<DashboardData> => {
    const response = await axios.get<DashboardData>(
      `${API_URL}/admin/dashboard`,
      getAuthHeaders(token)
    );
    return response.data;
  },

  getUsers: async (token: string | null): Promise<{ users: User[] }> => {
    const response = await axios.get<{ users: User[] }>(
      `${API_URL}/admin/users`,
      getAuthHeaders(token)
    );
    return response.data;
  },

  createUser: async (token: string | null, data: {
    name: string;
    email: string;
    password: string;
    role: string;
  }): Promise<User> => {
    const response = await axios.post<User>(
      `${API_URL}/admin/users`,
      data,
      getAuthHeaders(token)
    );
    return response.data;
  },

  updateUser: async (token: string | null,
    userId: number,
    data: { name?: string; email?: string }
  ): Promise<User> => {
    const response = await axios.put<User>(
      `${API_URL}/admin/users/${userId}`,
      data,
      getAuthHeaders(token)
    );
    return response.data;
  },

  deleteUser: async (token: string | null, userId: number): Promise<{ message: string }> => {
    const response = await axios.delete<{ message: string }>(
      `${API_URL}/admin/users/${userId}`,
      getAuthHeaders(token)
    );
    return response.data;
  },

  assignAssistant: async (token: string | null, courseId: number, userId: number, color?: string) => {
    const response = await axios.post(
      `${API_URL}/admin/courses/${courseId}/assign-assistant`,
      { user_id: userId, color },
      getAuthHeaders(token)
    );
    return response.data;
  },

  removeAssistant: async (token: string | null, courseId: number, userId: number) => {
    const response = await axios.delete(
      `${API_URL}/admin/courses/${courseId}/remove-assistant/${userId}`,
      getAuthHeaders(token)
    );
    return response.data;
  },
};