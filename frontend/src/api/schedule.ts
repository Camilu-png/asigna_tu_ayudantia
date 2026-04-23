import api from "./client";

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

export interface AssistantCourse {
  id: number;
  name: string;
  code: string;
  professor: string;
  credits: number;
  color: string;
}

export const getAssistantCourses = async (assistantId: number): Promise<AssistantCourse[]> => {
  try {
    const response = await api.get(`/assistant/courses/${assistantId}`);
    return response.data.courses || [];
  } catch (error) {
    console.error("Error fetching assistant courses:", error);
    throw error;
  }
};

export const getScheduleBlocks = async (userId: number, _userRole: string): Promise<ScheduleBlock[]> => {
  try {
    const response = await api.get(`/schedule/blocks/${userId}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching schedule blocks:", error);
    throw error;
  }
};

export const createScheduleBlock = async (data: {
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
}): Promise<ScheduleBlock> => {
  try {
    const response = await api.post("/schedule/blocks", data);
    return response.data;
  } catch (error) {
    console.error("Error creating schedule block:", error);
    throw error;
  }
};

export const deleteScheduleBlock = async (
  blockId: number,
  userId: number,
  userRole: string
): Promise<void> => {
  try {
    await api.delete(`/schedule/blocks/${blockId}`, {
      params: { user_id: userId, user_role: userRole },
    });
  } catch (error) {
    console.error("Error deleting schedule block:", error);
    throw error;
  }
};

export const getCourses = async () => {
  try {
    const response = await api.get("/courses");
    return response.data;
  } catch (error) {
    console.error("Error fetching courses:", error);
    throw error;
  }
};

export const runSolver = async (courseId: number, save: boolean = false) => {
  try {
    const response = await api.post("/solver/solve", { course_id: courseId, save });
    return response.data;
  } catch (error) {
    console.error("Error running solver:", error);
    throw error;
  }
};