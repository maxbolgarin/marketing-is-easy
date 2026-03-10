import {
  format,
  formatDistanceToNow,
  startOfWeek,
  endOfWeek,
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  parseISO,
} from "date-fns";

function toDate(date: string | Date): Date {
  if (typeof date === "string") {
    return parseISO(date);
  }
  return date;
}

/**
 * Formats a date as "Mar 10, 2026"
 */
export function formatDate(date: string | Date): string {
  return format(toDate(date), "MMM d, yyyy");
}

/**
 * Formats a date as "09:00"
 */
export function formatTime(date: string | Date): string {
  return format(toDate(date), "HH:mm");
}

/**
 * Formats a date as "Mar 10, 2026 09:00"
 */
export function formatDateTime(date: string | Date): string {
  return format(toDate(date), "MMM d, yyyy HH:mm");
}

/**
 * Formats a date relative to now, e.g. "2 hours ago"
 */
export function formatRelative(date: string | Date): string {
  return formatDistanceToNow(toDate(date), { addSuffix: true });
}

/**
 * Returns the 7 days (Mon-Sun) of the week containing the given date
 */
export function getWeekDays(date: Date): Date[] {
  const start = startOfWeek(date, { weekStartsOn: 1 });
  const end = endOfWeek(date, { weekStartsOn: 1 });
  return eachDayOfInterval({ start, end });
}

/**
 * Returns all days to display in a month calendar view,
 * padded to complete weeks (Mon-Sun boundaries)
 */
export function getMonthDays(date: Date): Date[] {
  const monthStart = startOfMonth(date);
  const monthEnd = endOfMonth(date);
  const calStart = startOfWeek(monthStart, { weekStartsOn: 1 });
  const calEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });
  return eachDayOfInterval({ start: calStart, end: calEnd });
}
