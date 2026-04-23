import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { USER_ROLES, INITIAL_COURSES, type UserRole } from "./userConstants";
import { authApi } from "../api/auth";
import { getScheduleBlocks, createScheduleBlock as apiCreateScheduleBlock, deleteScheduleBlock as apiDeleteScheduleBlock, getAssistantCourses } from "../api/schedule";
import type { User, Course, ScheduleBlock, AssistantCourse, UserContextType } from "./types";

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

interface StoredUser {
  id: number;
  name: string;
  email: string;
  role: UserRole;
}

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const storedUser = loadFromStorage<StoredUser | null>("user", null);
    if (storedUser) {
      return {
        ...storedUser,
        courses: [],
      };
    }
    return null;
  });

  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem("token");
  });

  const [refreshToken, setRefreshToken] = useState<string | null>(() => {
    return localStorage.getItem("refreshToken");
  });

  const [isLoading, setIsLoading] = useState(true);

  const [schedule, setSchedule] = useState<ScheduleBlock[]>(() => {
    return loadFromStorage<ScheduleBlock[]>("userSchedule", []);
  });

  const [blockedBlocks, setBlockedBlocks] = useState<ScheduleBlock[]>([]);

  const [allCourses, setAllCourses] = useState<Course[]>(() => {
    const saved = loadFromStorage<Course[] | null>("allCourses", null);
    return saved || INITIAL_COURSES;
  });

  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(() => {
    return loadFromStorage<boolean>("sidebarCollapsed", false);
  });

  const [assistantCourses, setAssistantCourses] = useState<AssistantCourse[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<AssistantCourse | null>(null);

  const toggleSidebar = useCallback(() => {
    setSidebarCollapsed((prev) => !prev);
  }, []);

  const refreshAccessToken = useCallback(async () => {
    if (!refreshToken) return false;
    try {
      const response = await authApi.refresh(refreshToken);
      setToken(response.access_token);
      setRefreshToken(response.refresh_token);
      localStorage.setItem("token", response.access_token);
      localStorage.setItem("refreshToken", response.refresh_token);
      return true;
    } catch {
      return false;
    }
  }, [refreshToken]);

  const loadSchedule = useCallback(async () => {
    if (!user) return;
    try {
      const userRole = user.role === USER_ROLES.ASSISTANT ? "assistant" : "student";
      const blocks = await getScheduleBlocks(user.id, userRole);
      setSchedule(blocks);
    } catch (error) {
      console.error("Error loading schedule:", error);
    }
  }, [user]);

  const loadAssistantData = useCallback(async () => {
    if (!user || (user.role !== USER_ROLES.ASSISTANT && user.role !== 'ASSISTANT')) return;
    
    try {
      const [courses, blocked] = await Promise.all([
        getAssistantCourses(user.id),
        getScheduleBlocks(user.id, "student"),
      ]);
      setAssistantCourses(courses);
      setBlockedBlocks(blocked);
    } catch (error) {
      console.error("Error loading assistant data:", error);
    }
  }, [user]);

  useEffect(() => {
    if (user) {
      loadSchedule();
      if (user.role === USER_ROLES.ASSISTANT || user.role === 'ASSISTANT') {
        loadAssistantData();
      }
    }
  }, [user, loadSchedule, loadAssistantData]);

  useEffect(() => {
    if (user) {
      const storedUser: StoredUser = {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role as UserRole,
      };
      localStorage.setItem("user", JSON.stringify(storedUser));
    } else {
      localStorage.removeItem("user");
    }
  }, [user]);

  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
    } else {
      localStorage.removeItem("token");
    }
  }, [token]);

  useEffect(() => {
    if (refreshToken) {
      localStorage.setItem("refreshToken", refreshToken);
    } else {
      localStorage.removeItem("refreshToken");
    }
  }, [refreshToken]);

  useEffect(() => {
    localStorage.setItem("userSchedule", JSON.stringify(schedule));
  }, [schedule]);

  useEffect(() => {
    localStorage.setItem("sidebarCollapsed", JSON.stringify(sidebarCollapsed));
  }, [sidebarCollapsed]);

  useEffect(() => {
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authApi.login(email, password);
    setToken(response.access_token);
    setRefreshToken(response.refresh_token);

    const role: UserRole =
      response.user.role === "assistant"
        ? USER_ROLES.ASSISTANT
        : response.user.role === "ADMIN"
          ? "admin" as UserRole
          : USER_ROLES.STUDENT;

    const newUser: User = {
      id: response.user.id,
      name: response.user.name,
      email: response.user.email,
      role: role,
      courses: [],
    };
    setUser(newUser);
    return newUser;
  };

  const logout = async () => {
    if (token) {
      try {
        await authApi.logout(token);
      } catch {
        // Ignore logout errors
      }
    }
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("userSchedule");
    setUser(null);
    setToken(null);
    setRefreshToken(null);
    setSchedule([]);
  };

  const addCourse = (course: Course) => {
    const newCourse = { ...course, id: Date.now() };
    const updatedCourses = [...allCourses, newCourse];
    setAllCourses(updatedCourses);
    localStorage.setItem("allCourses", JSON.stringify(updatedCourses));
  };

  const addScheduleBlock = async (block: Omit<{
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
  }, "id">) => {
    if (!user) return;
    
    const userRole = user.role === USER_ROLES.ASSISTANT ? "assistant" : "student";
    
    try {
      const newBlock = await apiCreateScheduleBlock({
        user_id: user.id,
        user_role: userRole,
        day: block.day,
        start_time: block.start_time,
        end_time: block.end_time,
        course_id: block.course_id,
        new_course: block.new_course,
        color: block.color,
      });
      setSchedule([...schedule, newBlock]);
    } catch (error) {
      console.error("Error creating schedule block:", error);
      throw error;
    }
  };

  const removeScheduleBlock = async (blockId: number) => {
    if (!user) return;
    
    const userRole = user.role === USER_ROLES.ASSISTANT ? "assistant" : "student";
    
    try {
      await apiDeleteScheduleBlock(blockId, user.id, userRole);
      setSchedule(schedule.filter((b) => b.id !== blockId));
    } catch (error) {
      console.error("Error deleting schedule block:", error);
      throw error;
    }
  };

  return (
    <UserContext.Provider
      value={{
        user,
        schedule,
        allCourses,
        sidebarCollapsed,
        assistantCourses,
        selectedCourse,
        blockedBlocks,
        addCourse,
        addScheduleBlock,
        removeScheduleBlock,
        logout,
        setUser,
        login,
        isLoading,
        token,
        refreshAccessToken,
        toggleSidebar,
        loadSchedule,
        loadAssistantData,
        setSelectedCourse,
      }}
    >
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return context;
}