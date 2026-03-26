import { useUser } from '../context/UserContext';

interface ScheduleCellProps {
  day: number;
  hour: number;
  onClick: () => void;
}

export default function ScheduleCell({ day, hour, onClick }: ScheduleCellProps) {
  const { schedule, removeScheduleBlock } = useUser();

  const block = schedule.find(
    (b) => b.day === day && b.hour === hour
  );

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (block) {
      removeScheduleBlock(block.id);
    }
  };

  if (block) {
    return (
      <div
        className="schedule-cell occupied"
        style={{ backgroundColor: `${block.color}20`, borderLeftColor: block.color }}
        onClick={handleRemove}
        title="Click para eliminar"
      >
        <span className="cell-course-name">{block.courseName}</span>
        {block.courseCode && (
          <span className="cell-course-code">{block.courseCode}</span>
        )}
      </div>
    );
  }

  return (
    <div className="schedule-cell empty" onClick={onClick}>
      <span className="cell-add">+</span>
    </div>
  );
}
