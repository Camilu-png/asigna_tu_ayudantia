export const USER_ROLES = {
  STUDENT: 'student',
  ASSISTANT: 'assistant'
} as const;

export type UserRole = typeof USER_ROLES.STUDENT | typeof USER_ROLES.ASSISTANT;

export const MOCK_USERS: Record<UserRole, {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  courses: Array<{ id: number; name: string; code: string; color: string }>;
}> = {
  [USER_ROLES.STUDENT]: {
    id: 1,
    name: 'Juan Pérez',
    email: 'juan.perez@usm.cl',
    role: USER_ROLES.STUDENT,
    courses: [
      { id: 1, name: 'Cálculo II', code: 'MAT204', color: '#4ECDC4' },
      { id: 2, name: 'Física I', code: 'FIS100', color: '#FF6B6B' },
      { id: 3, name: 'Programación', code: 'INF201', color: '#45B7D1' }
    ]
  },
  [USER_ROLES.ASSISTANT]: {
    id: 1,
    name: 'María González',
    email: 'maria.gonzalez@usm.cl',
    role: USER_ROLES.ASSISTANT,
    courses: [
      { id: 4, name: 'Álgebra Lineal', code: 'MAT102', color: '#96CEB4' },
      { id: 5, name: 'Cálculo I', code: 'MAT101', color: '#FFEAA7' }
    ]
  }
};

export const INITIAL_COURSES = [
  { id: 1, name: 'Cálculo II', code: 'MAT204', color: '#4ECDC4' },
  { id: 2, name: 'Física I', code: 'FIS100', color: '#FF6B6B' },
  { id: 3, name: 'Programación', code: 'INF201', color: '#45B7D1' },
  { id: 4, name: 'Álgebra Lineal', code: 'MAT102', color: '#96CEB4' },
  { id: 5, name: 'Cálculo I', code: 'MAT101', color: '#FFEAA7' },
  { id: 6, name: 'Estructuras de Datos', code: 'INF202', color: '#DDA0DD' },
  { id: 7, name: 'Química General', code: 'QUI100', color: '#98D8C8' },
  { id: 8, name: 'Electromagnetismo', code: 'FIS200', color: '#F7DC6F' }
];
