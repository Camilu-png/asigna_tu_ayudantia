import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { USER_ROLES, INITIAL_COURSES, type UserRole } from "./userConstants";
import { authApi } from "../api/auth";
import type { User, Course, ScheduleBlock, UserContextType } from "./types";

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
    return loadFromStorage<string | null>("token", null);
  });

  const [refreshToken, setRefreshToken] = useState<string | null>(() => {
    return loadFromStorage<string | null>("refreshToken", null);
  });

  const [isLoading, setIsLoading] = useState(true);

  const [schedule, setSchedule] = useState<ScheduleBlock[]>(() => {
    return loadFromStorage<ScheduleBlock[]>("userSchedule", []);
  });

  const [allCourses, setAllCourses] = useState<Course[]>(() => {
    const saved = loadFromStorage<Course[] | null>("allCourses", null);
    return saved || INITIAL_COURSES;
  });

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
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authApi.login(email, password);
    setToken(response.access_token);
    setRefreshToken(response.refresh_token);

    const role =
      response.user.role === "assistant"
        ? USER_ROLES.ASSISTANT
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

  const addScheduleBlock = (block: Omit<ScheduleBlock, "id">) => {
    const newBlock = { ...block, id: Date.now() };
    setSchedule([...schedule, newBlock]);
  };

  const removeScheduleBlock = (blockId: number) => {
    setSchedule(schedule.filter((b) => b.id !== blockId));
  };

  return (
    <UserContext.Provider
      value={{
        user,
        schedule,
        allCourses,
        addCourse,
        addScheduleBlock,
        removeScheduleBlock,
        logout,
        setUser,
        login,
        isLoading,
        token,
        refreshAccessToken,
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
