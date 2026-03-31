export interface Course {
  id: number;
  name: string;
  code: string;
  color: string;
}

export type UserRole = 'student' | 'assistant';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  courses: Course[];
}

export interface ScheduleBlock {
  id: number;
  day: number;
  hour: number;
  courseId: number;
  courseName: string;
  courseCode: string;
  color: string;
}

export interface UserContextType {
  user: User | null;
  schedule: ScheduleBlock[];
  allCourses: Course[];
  sidebarCollapsed: boolean;
  addCourse: (course: Course) => void;
  addScheduleBlock: (block: Omit<ScheduleBlock, 'id'>) => void;
  removeScheduleBlock: (blockId: number) => void;
  logout: () => void;
  setUser: (user: User | null) => void;
  login: (email: string, password: string) => Promise<User>;
  isLoading: boolean;
  token: string | null;
  refreshAccessToken: () => Promise<boolean>;
  toggleSidebar: () => void;
}
