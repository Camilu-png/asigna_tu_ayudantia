import { useUser } from '../context/UserContext';

interface BlockInfo {
  id: number;
  courseName: string | null;
  courseCode: string | null;
  color: string | null;
  startTime: string;
  endTime: string;
}

interface ScheduleCellProps {
  day: number;
  hour: number;
  blocks?: BlockInfo[];
  onClick: () => void;
}

export default function ScheduleCell({ day: _day, hour, blocks = [], onClick }: ScheduleCellProps) {
  const { removeScheduleBlock } = useUser();

  const block = blocks.length > 0 ? blocks[0] : null;
  const isFirstHour = block ? parseInt(block.startTime.split(':')[0]) === hour : false;

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (block) {
      removeScheduleBlock(block.id);
    }
  };

  if (block && isFirstHour) {
    return (
      <div
        className="schedule-cell occupied"
        style={{ 
          backgroundColor: block.color ? `${block.color}20` : undefined, 
          borderLeftColor: block.color || undefined 
        }}
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

  if (block) {
    return (
      <div
        className="schedule-cell occupied"
        style={{ 
          backgroundColor: block.color ? `${block.color}20` : undefined, 
          borderLeftColor: block.color || undefined 
        }}
        onClick={handleRemove}
      />
    );
  }

  return (
    <div className="schedule-cell empty" onClick={onClick}>
      <span className="cell-add">+</span>
    </div>
  );
}