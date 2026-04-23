export interface Course {
  id: number;
  name: string;
  code: string;
  color: string;
}

export interface AssistantCourse {
  id: number;
  name: string;
  code: string;
  professor: string;
  credits: number;
  color: string;
}

export type UserRole = 'student' | 'assistant' | 'admin' | 'ADMIN' | 'USER' | 'ASSISTANT';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  courses: Course[];
}

export interface ScheduleBlock {
  id: number;
  day: string;
  start_time: string;
  end_time: string;
  course_id: number | null;
  course_name: string | null;
  course_code: string | null;
  color: string | null;
}

export interface CreateScheduleBlockRequest {
  user_id: number;
  user_role: string;
  day: string;
  start_time: string;
  end_time: string;
  course_id?: number;
  new_course?: {
    name: string;
    code: string;
    professor: string;
    credits: number;
  };
  color?: string;
}

export interface UserContextType {
  user: User | null;
  schedule: ScheduleBlock[];
  allCourses: Course[];
  sidebarCollapsed: boolean;
  assistantCourses: AssistantCourse[];
  selectedCourse: AssistantCourse | null;
  blockedBlocks: ScheduleBlock[];
  addCourse: (course: Course) => void;
  addScheduleBlock: (block: CreateScheduleBlockRequest) => Promise<void>;
  removeScheduleBlock: (blockId: number) => Promise<void>;
  logout: () => void;
  setUser: (user: User | null) => void;
  login: (email: string, password: string) => Promise<User>;
  isLoading: boolean;
  token: string | null;
  refreshAccessToken: () => Promise<boolean>;
  toggleSidebar: () => void;
  loadSchedule: () => Promise<void>;
  loadAssistantData: () => Promise<void>;
  setSelectedCourse: (course: AssistantCourse | null) => void;
}
