import { createContext, useContext, useState, useEffect } from 'react';
import { USER_ROLES, MOCK_USERS, INITIAL_COURSES, type UserRole } from './userConstants';
import type { User, Course, ScheduleBlock, UserContextType } from './types';

export { USER_ROLES };
export type { UserRole };

const UserContext = createContext<UserContextType | null>(null);

function loadFromStorage<T>(key: string, fallback: T): T {
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : fallback;
  } catch {
    return fallback;
  }
}

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const savedRole = loadFromStorage<string | null>('userRole', null);
    return savedRole ? MOCK_USERS[savedRole as UserRole] : MOCK_USERS[USER_ROLES.STUDENT];
  });

  const [schedule, setSchedule] = useState<ScheduleBlock[]>(() => {
    return loadFromStorage<ScheduleBlock[]>('userSchedule', []);
  });

  const [allCourses, setAllCourses] = useState<Course[]>(() => {
    const saved = loadFromStorage<Course[] | null>('allCourses', null);
    return saved || INITIAL_COURSES;
  });

  useEffect(() => {
    if (user) {
      localStorage.setItem('userRole', user.role);
    }
  }, [user]);

  useEffect(() => {
    localStorage.setItem('userSchedule', JSON.stringify(schedule));
  }, [schedule]);

  const switchRole = (newRole: UserRole) => {
    setUser(MOCK_USERS[newRole]);
  };

  const addCourse = (course: Course) => {
    const newCourse = { ...course, id: Date.now() };
    const updatedCourses = [...allCourses, newCourse];
    setAllCourses(updatedCourses);
    localStorage.setItem('allCourses', JSON.stringify(updatedCourses));
  };

  const addScheduleBlock = (block: Omit<ScheduleBlock, 'id'>) => {
    const newBlock = { ...block, id: Date.now() };
    setSchedule([...schedule, newBlock]);
  };

  const removeScheduleBlock = (blockId: number) => {
    setSchedule(schedule.filter(b => b.id !== blockId));
  };

  const logout = () => {
    localStorage.removeItem('userRole');
    localStorage.removeItem('userSchedule');
    setUser(MOCK_USERS[USER_ROLES.STUDENT]);
  };

  return (
    <UserContext.Provider value={{
      user,
      schedule,
      allCourses,
      switchRole,
      addCourse,
      addScheduleBlock,
      removeScheduleBlock,
      logout,
      setUser
    }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}
