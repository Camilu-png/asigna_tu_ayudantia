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

export const getScheduleBlocks = async (userId: number, userRole: string): Promise<ScheduleBlock[]> => {
  try {
    const response = await api.get(`/schedule/blocks/${userId}/${userRole}`);
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