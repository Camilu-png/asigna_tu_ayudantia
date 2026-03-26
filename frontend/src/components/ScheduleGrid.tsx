import { useState } from 'react';
import ScheduleCell from './ScheduleCell';
import CourseModal from './CourseModal';

const DAYS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
const HOURS = Array.from({ length: 14 }, (_, i) => 8 + i);

export default function ScheduleGrid() {
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

  return (
    <div className="schedule-grid-container">
      <div className="schedule-grid">
        <div className="schedule-header">
          <div className="schedule-corner"></div>
          {DAYS.map((day) => (
            <div key={day} className="schedule-day-header">{day}</div>
          ))}
        </div>
        
        <div className="schedule-body">
          {HOURS.map((hour) => (
            <div key={hour} className="schedule-row">
              <div className="schedule-hour-label">{hour}:00</div>
              {DAYS.map((_, dayIndex) => (
                <ScheduleCell
                  key={`${dayIndex}-${hour}`}
                  day={dayIndex}
                  hour={hour}
                  onClick={() => handleCellClick(dayIndex, HOURS.indexOf(hour))}
                />
              ))}
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
