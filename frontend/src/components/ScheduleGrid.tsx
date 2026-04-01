import { useState, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import ScheduleCell from './ScheduleCell';
import CourseModal from './CourseModal';

const DAYS_EN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const DAYS_ES = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
const HOURS = Array.from({ length: 14 }, (_, i) => 8 + i);

interface BlockInfo {
  id: number;
  courseName: string | null;
  courseCode: string | null;
  color: string | null;
  startTime: string;
  endTime: string;
  isBlocked?: boolean;
}

export default function ScheduleGrid() {
  const { schedule } = useUser();
  const location = useLocation();
  const isCourseView = location.pathname.startsWith('/courses/');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedCell, setSelectedCell] = useState({ day: 0, hour: 0 });

  const handleCellClick = (dayIndex: number, hourIndex: number) => {
    setSelectedCell({ day: dayIndex, hour: hourIndex });
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setSelectedCell({ day: 0, hour: 0 });
  };

  const scheduleMap = useMemo(() => {
    const map: Record<string, BlockInfo[]> = {};
    DAYS_EN.forEach(day => {
      map[day] = [];
    });
    
    schedule.forEach(block => {
      const dayIndex = DAYS_EN.indexOf(block.day);
      if (dayIndex === -1) return;
      
      const day = block.day;
      if (!map[day]) map[day] = [];
      
      map[day].push({
        id: block.id,
        courseName: block.course_name,
        courseCode: block.course_code,
        color: block.color,
        startTime: block.start_time,
        endTime: block.end_time,
        isBlocked: isCourseView,
      });
    });
    
    return map;
  }, [schedule, isCourseView]);

  const getBlocksForCell = (day: string, hour: number): BlockInfo[] => {
    const blocks = scheduleMap[day] || [];
    
    return blocks.filter(block => {
      const startHour = parseInt(block.startTime.split(':')[0]);
      const endHour = parseInt(block.endTime.split(':')[0]);
      return hour >= startHour && hour < endHour;
    });
  };

  const isCellBlocked = (day: string, hour: number): boolean => {
    const blocks = scheduleMap[day] || [];
    return blocks.some(block => {
      const startHour = parseInt(block.startTime.split(':')[0]);
      const endHour = parseInt(block.endTime.split(':')[0]);
      return hour >= startHour && hour < endHour;
    });
  };

  return (
    <div className="schedule-grid-container">
      <div className="schedule-grid">
        <div className="schedule-header">
          <div className="schedule-corner"></div>
          {DAYS_ES.map((day) => (
            <div key={day} className="schedule-day-header">{day}</div>
          ))}
        </div>
        
        <div className="schedule-body">
          {HOURS.map((hour) => (
            <div key={hour} className="schedule-row">
              <div className="schedule-hour-label">{hour}:00</div>
              {DAYS_EN.map((dayEn, dayIndex) => {
                const blocks = getBlocksForCell(dayEn, hour);
                const isBlocked = isCellBlocked(dayEn, hour);
                return (
                  <ScheduleCell
                    key={`${dayIndex}-${hour}`}
                    day={dayIndex}
                    hour={hour}
                    blocks={blocks}
                    isBlocked={isBlocked}
                    onClick={() => handleCellClick(dayIndex, HOURS.indexOf(hour))}
                  />
                );
              })}
            </div>
          ))}
        </div>
      </div>

      <CourseModal
        isOpen={modalOpen}
        onClose={handleCloseModal}
        selectedDay={selectedCell.day}
        selectedHour={selectedCell.hour}
      />
    </div>
  );
}