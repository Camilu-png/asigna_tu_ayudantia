import { useUser } from "../context/UserContext";

interface BlockInfo {
  id: number;
  courseName: string | null;
  courseCode: string | null;
  color: string | null;
  startTime: string;
  endTime: string;
  isBlocked?: boolean;
}

interface ScheduleCellProps {
  day: number;
  hour: number;
  blocks?: BlockInfo[];
  isBlocked?: boolean;
  onClick: () => void;
}

export default function ScheduleCell({
  day: _day,
  hour,
  blocks = [],
  isBlocked = false,
  onClick,
}: ScheduleCellProps) {
  const { removeScheduleBlock } = useUser();

  const activeBlock = blocks.find((b) => !b.isBlocked);
  const blockedBlock = blocks.find((b) => b.isBlocked);
  const block = activeBlock || blockedBlock;
  const isFirstHour = block
    ? parseInt(block.startTime.split(":")[0]) === hour
    : false;

  const handleClick = (e: React.MouseEvent) => {
    if (isBlocked) {
      e.stopPropagation();
      return;
    }
    onClick();
  };

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (activeBlock) {
      removeScheduleBlock(activeBlock.id);
    }
  };

  if (block && isFirstHour && activeBlock) {
    return (
      <div
        className={`schedule-cell occupied ${isBlocked ? "blocked" : ""}`}
        style={{
          backgroundColor: activeBlock.color
            ? `${activeBlock.color}20`
            : undefined,
          borderLeftColor: activeBlock.color || undefined,
          opacity: isBlocked ? 0.4 : 1,
          cursor: isBlocked ? "not-allowed" : "pointer",
        }}
        onClick={isBlocked ? undefined : handleRemove}
        title={
          isBlocked
            ? "Bloqueado - tienes clase en este horario"
            : "Click para eliminar"
        }
      >
        <span className="cell-course-name">{activeBlock.courseName}</span>
        {activeBlock.courseCode && (
          <span className="cell-course-code">{activeBlock.courseCode}</span>
        )}
        {isBlocked && (
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="lock-icon"
          >
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
        )}
      </div>
    );
  }

  if (block && isFirstHour && blockedBlock) {
    return (
      <div
        className="schedule-cell blocked"
        style={{
          backgroundColor: blockedBlock.color
            ? `${blockedBlock.color}20`
            : undefined,
          borderLeftColor: blockedBlock.color || undefined,
          opacity: 0.4,
          cursor: "not-allowed",
        }}
        title="Bloqueado - tienes clase en este horario"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="lock-icon"
        >
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
          <path d="M7 11V7a5 5 0 0 1 10 0v4" />
        </svg>
      </div>
    );
  }

  if (block && blockedBlock) {
    return (
      <div
        className="schedule-cell blocked"
        style={{
          backgroundColor: blockedBlock.color
            ? `${blockedBlock.color}20`
            : undefined,
          borderLeftColor: blockedBlock.color || undefined,
          opacity: 0.4,
        }}
      />
    );
  }

  if (block && activeBlock) {
    return (
      <div
        className="schedule-cell occupied"
        style={{
          backgroundColor: activeBlock?.color
            ? `${activeBlock.color}20`
            : undefined,
          borderLeftColor: activeBlock?.color || undefined,
        }}
        onClick={handleRemove}
      />
    );
  }

  return (
    <div className="schedule-cell empty" onClick={handleClick}>
      <span className="cell-add">+</span>
    </div>
  );
}
