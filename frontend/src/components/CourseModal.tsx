import { useState } from 'react';
import { useUser } from '../context/UserContext';
import ColorPicker from './ColorPicker';
import type { Course } from '../context/types';

let courseIdCounter = 100;

const DAYS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
const HOURS = Array.from({ length: 14 }, (_, i) => 8 + i);

interface CourseModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedDay: number;
  selectedHour: number;
}

export default function CourseModal({ isOpen, onClose, selectedDay, selectedHour }: CourseModalProps) {
  const { user, allCourses, addCourse, addScheduleBlock } = useUser();
  const [mode, setMode] = useState<'select' | 'create'>('select');
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [newCourse, setNewCourse] = useState({ name: '', code: '', color: '#4ECDC4' });
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const userCourses = user?.courses || [];
  const displayCourses = userCourses.length > 0 ? userCourses : allCourses;

  const handleSubmit = () => {
    setError('');

    if (mode === 'select') {
      if (!selectedCourse) {
        setError('Selecciona una asignatura');
        return;
      }
      addScheduleBlock({
        day: selectedDay,
        hour: selectedHour,
        courseId: selectedCourse.id,
        courseName: selectedCourse.name,
        courseCode: selectedCourse.code,
        color: selectedCourse.color
      });
    } else {
      if (!newCourse.name.trim()) {
        setError('Ingresa el nombre de la asignatura');
        return;
      }
      const course: Course = {
        ...newCourse,
        id: ++courseIdCounter
      };
      addCourse(course);
      addScheduleBlock({
        day: selectedDay,
        hour: selectedHour,
        courseId: course.id,
        courseName: course.name,
        courseCode: course.code,
        color: course.color
      });
    }

    onClose();
    setMode('select');
    setSelectedCourse(null);
    setNewCourse({ name: '', code: '', color: '#4ECDC4' });
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
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <div className="modal-info">
          <span>{DAYS[selectedDay]}</span>
          <span>{HOURS[selectedHour]}:00 - {HOURS[selectedHour] + 1}:00</span>
        </div>

        <div className="modal-tabs">
          <button
            className={`modal-tab ${mode === 'select' ? 'active' : ''}`}
            onClick={() => setMode('select')}
          >
            Seleccionar existente
          </button>
          <button
            className={`modal-tab ${mode === 'create' ? 'active' : ''}`}
            onClick={() => setMode('create')}
          >
            Crear nueva
          </button>
        </div>

        {mode === 'select' ? (
          <div className="modal-body">
            {displayCourses.length === 0 ? (
              <p className="modal-empty">No hay asignaturas disponibles. Crea una nueva.</p>
            ) : (
              <div className="course-list">
                {displayCourses.map((course) => (
                  <button
                    key={course.id}
                    type="button"
                    className={`course-option ${selectedCourse?.id === course.id ? 'selected' : ''}`}
                    onClick={() => setSelectedCourse(course)}
                  >
                    <span className="course-color" style={{ backgroundColor: course.color }} />
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
                onChange={(e) => setNewCourse({ ...newCourse, name: e.target.value })}
                placeholder="Ej: Cálculo II"
              />
            </div>
            <div className="form-group">
              <label>Código (opcional)</label>
              <input
                type="text"
                value={newCourse.code}
                onChange={(e) => setNewCourse({ ...newCourse, code: e.target.value })}
                placeholder="Ej: MAT204"
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
          <button className="btn-secondary" onClick={onClose}>Cancelar</button>
          <button className="btn-primary" onClick={handleSubmit}>Agregar</button>
        </div>
      </div>
    </div>
  );
}
