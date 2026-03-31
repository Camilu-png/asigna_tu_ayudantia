import { useState } from "react";
import { useUser } from "../context/UserContext";
import ColorPicker from "./ColorPicker";
import { getCourses } from "../api/courses";
import type { Course } from "../context/types";
import { DEFAULT_COURSE_COLOR } from "../context/constants";

const DAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const DAYS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];
const HOURS = Array.from({ length: 14 }, (_, i) => 8 + i);

interface CourseModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedDay: number;
  selectedHour: number;
}

export default function CourseModal({
  isOpen,
  onClose,
  selectedDay,
  selectedHour,
}: CourseModalProps) {
  const { addScheduleBlock, user, loadSchedule } = useUser();
  const [mode, setMode] = useState<"select" | "create">("select");
  const [courses, setCourses] = useState<Course[]>([]);
  const [loadingCourses, setLoadingCourses] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [newCourse, setNewCourse] = useState({
    name: "",
    code: "",
    professor: "",
    credits: 4,
    color: DEFAULT_COURSE_COLOR,
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const loadCourses = async () => {
    if (courses.length > 0) return;
    setLoadingCourses(true);
    try {
      const data = await getCourses();
      setCourses(data);
    } catch (err) {
      console.error("Error loading courses:", err);
    } finally {
      setLoadingCourses(false);
    }
  };

  if (isOpen && courses.length === 0 && !loadingCourses) {
    loadCourses();
  }

  if (!isOpen) return null;

  const handleSubmit = async () => {
    setError("");
    setSubmitting(true);

    try {
      const day = DAYS_EN[selectedDay];
      const startTime = `${HOURS[selectedHour]}:00`;
      const endTime = `${HOURS[selectedHour] + 1}:00`;

      if (mode === "select") {
        if (!selectedCourse) {
          setError("Selecciona una asignatura");
          setSubmitting(false);
          return;
        }
        await addScheduleBlock({
          user_id: user!.id,
          user_role: user!.role === "assistant" ? "assistant" : "student",
          day,
          start_time: startTime,
          end_time: endTime,
          course_id: selectedCourse.id,
          color: selectedCourse.color,
        });
      } else {
        if (!newCourse.name.trim()) {
          setError("Ingresa el nombre de la asignatura");
          setSubmitting(false);
          return;
        }
        if (!newCourse.code.trim()) {
          setError("Ingresa el código de la asignatura");
          setSubmitting(false);
          return;
        }
        if (!newCourse.professor.trim()) {
          setError("Ingresa el nombre del profesor");
          setSubmitting(false);
          return;
        }

        await addScheduleBlock({
          user_id: user!.id,
          user_role: user!.role === "assistant" ? "assistant" : "student",
          day,
          start_time: startTime,
          end_time: endTime,
          new_course: {
            name: newCourse.name,
            code: newCourse.code,
            professor: newCourse.professor,
            credits: newCourse.credits,
          },
          color: newCourse.color,
        });
      }

      await loadSchedule();
      onClose();
      setMode("select");
      setSelectedCourse(null);
      setNewCourse({
        name: "",
        code: "",
        professor: "",
        credits: 4,
        color: DEFAULT_COURSE_COLOR,
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || "Error al agregar el bloque");
    } finally {
      setSubmitting(false);
    }
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content">
        <div className="modal-header">
          <h3>Agregar bloque</h3>
          <button className="modal-close" onClick={onClose}>
            &times;
          </button>
        </div>

        <div className="modal-info">
          <span>{DAYS_ES[selectedDay]}</span>
          <span>
            {HOURS[selectedHour]}:00 - {HOURS[selectedHour] + 1}:00
          </span>
        </div>

        <div className="modal-tabs">
          <button
            className={`modal-tab ${mode === "select" ? "active" : ""}`}
            onClick={() => setMode("select")}
          >
            Seleccionar existente
          </button>
          <button
            className={`modal-tab ${mode === "create" ? "active" : ""}`}
            onClick={() => setMode("create")}
          >
            Crear nueva
          </button>
        </div>

        {mode === "select" ? (
          <div className="modal-body">
            {loadingCourses ? (
              <p className="modal-empty">Cargando asignaturas...</p>
            ) : courses.length === 0 ? (
              <p className="modal-empty">
                No hay asignaturas disponibles. Crea una nueva.
              </p>
            ) : (
              <div className="course-list">
                {courses.map((course) => (
                  <button
                    key={course.id}
                    type="button"
                    className={`course-option ${selectedCourse?.id === course.id ? "selected" : ""}`}
                    onClick={() => setSelectedCourse(course)}
                  >
                    <span
                      className="course-color"
                      style={{ backgroundColor: course.color }}
                    />
                    <div className="course-info">
                      <span className="course-name">{course.name}</span>
                      <span className="course-code">{course.code}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="modal-body">
            <div className="form-group">
              <label>Nombre de la asignatura *</label>
              <input
                type="text"
                value={newCourse.name}
                onChange={(e) =>
                  setNewCourse({ ...newCourse, name: e.target.value })
                }
                placeholder="Ej: Cálculo II"
              />
            </div>
            <div className="form-group">
              <label>Código *</label>
              <input
                type="text"
                value={newCourse.code}
                onChange={(e) =>
                  setNewCourse({ ...newCourse, code: e.target.value })
                }
                placeholder="Ej: MAT204"
              />
            </div>
            <div className="form-group">
              <label>Profesor *</label>
              <input
                type="text"
                value={newCourse.professor}
                onChange={(e) =>
                  setNewCourse({ ...newCourse, professor: e.target.value })
                }
                placeholder="Ej: Dr. Smith"
              />
            </div>
            <div className="form-group">
              <label>Créditos</label>
              <input
                type="number"
                value={newCourse.credits}
                onChange={(e) =>
                  setNewCourse({ ...newCourse, credits: parseInt(e.target.value) || 0 })
                }
                min="0"
              />
            </div>
            <div className="form-group">
              <label>Color</label>
              <ColorPicker
                value={newCourse.color}
                onChange={(color) => setNewCourse({ ...newCourse, color })}
              />
            </div>
          </div>
        )}

        {error && <p className="modal-error">{error}</p>}

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Cancelar
          </button>
          <button 
            className="btn-primary" 
            onClick={handleSubmit}
            disabled={submitting}
          >
            {submitting ? "Agregando..." : "Agregar"}
          </button>
        </div>
      </div>
    </div>
  );
}