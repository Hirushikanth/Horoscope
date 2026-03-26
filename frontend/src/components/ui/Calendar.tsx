import { useState, useEffect, useRef } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react';

interface CalendarPopupProps {
  value: string;
  onChange: (date: string) => void;
  onClose: () => void;
}

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export const CalendarPopup = ({ value, onChange, onClose }: CalendarPopupProps) => {
  const [viewDate, setViewDate] = useState(() => {
    const d = value ? new Date(value + 'T00:00:00') : new Date();
    return { year: d.getFullYear(), month: d.getMonth() };
  });
  const [selectedDate, setSelectedDate] = useState<Date | null>(
    value ? new Date(value + 'T00:00:00') : null
  );
  const [showYearPicker, setShowYearPicker] = useState(false);
  const popupRef = useRef<HTMLDivElement>(null);

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 101 }, (_, i) => currentYear - 100 + i);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (popupRef.current && !popupRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [onClose]);

  const getDaysInMonth = (year: number, month: number) => {
    return new Date(year, month + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (year: number, month: number) => {
    return new Date(year, month, 1).getDay();
  };

  const handlePrevMonth = () => {
    if (showYearPicker) {
      setViewDate(prev => ({ ...prev, year: prev.year - 10 }));
    } else {
      setViewDate(prev => {
        if (prev.month === 0) return { year: prev.year - 1, month: 11 };
        return { year: prev.year, month: prev.month - 1 };
      });
    }
  };

  const handleNextMonth = () => {
    if (showYearPicker) {
      setViewDate(prev => ({ ...prev, year: prev.year + 10 }));
    } else {
      setViewDate(prev => {
        if (prev.month === 11) return { year: prev.year + 1, month: 0 };
        return { year: prev.year, month: prev.month + 1 };
      });
    }
  };

  const handleYearSelect = (year: number) => {
    setViewDate(prev => ({ ...prev, year }));
    setShowYearPicker(false);
  };

  const handleDateSelect = (day: number) => {
    const date = new Date(viewDate.year, viewDate.month, day);
    setSelectedDate(date);
    const formatted = date.toISOString().split('T')[0];
    onChange(formatted);
    onClose();
  };

  const isSelected = (day: number) => {
    if (!selectedDate) return false;
    return (
      selectedDate.getDate() === day &&
      selectedDate.getMonth() === viewDate.month &&
      selectedDate.getFullYear() === viewDate.year
    );
  };

  const isToday = (day: number) => {
    const today = new Date();
    return (
      today.getDate() === day &&
      today.getMonth() === viewDate.month &&
      today.getFullYear() === viewDate.year
    );
  };

  const daysInMonth = getDaysInMonth(viewDate.year, viewDate.month);
  const firstDay = getFirstDayOfMonth(viewDate.year, viewDate.month);
  const days: (number | null)[] = [];

  for (let i = 0; i < firstDay; i++) days.push(null);
  for (let i = 1; i <= daysInMonth; i++) days.push(i);

  const decadeStart = Math.floor(viewDate.year / 10) * 10;

  return (
    <div
      ref={popupRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/30"
      onClick={onClose}
    >
      <div
        className="p-4 rounded-xl glass-card min-w-[320px]"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <button
            type="button"
            onClick={handlePrevMonth}
            className="p-2 rounded-lg hover:bg-white/10 text-white/70 hover:text-white transition-colors"
          >
            <ChevronLeft size={20} />
          </button>

          <div className="flex items-center gap-2">
            {!showYearPicker ? (
              <button
                type="button"
                onClick={() => setShowYearPicker(true)}
                className="font-cinematic text-white text-lg hover:text-gold-primary transition-colors"
              >
                {MONTHS[viewDate.month]} {viewDate.year}
              </button>
            ) : (
              <span className="font-cinematic text-white text-lg">
                {decadeStart} - {decadeStart + 9}
              </span>
            )}
          </div>

          <button
            type="button"
            onClick={handleNextMonth}
            className="p-2 rounded-lg hover:bg-white/10 text-white/70 hover:text-white transition-colors"
          >
            <ChevronRight size={20} />
          </button>
        </div>

        {!showYearPicker ? (
          <>
            {/* Day labels */}
            <div className="grid grid-cols-7 gap-1 mb-2">
              {DAYS.map(day => (
                <div key={day} className="text-center text-[10px] text-white/40 uppercase tracking-wider py-1">
                  {day}
                </div>
              ))}
            </div>

            {/* Calendar grid */}
            <div className="grid grid-cols-7 gap-1">
              {days.map((day, idx) => (
                <div key={idx} className="aspect-square">
                  {day !== null && (
                    <button
                      type="button"
                      onClick={() => handleDateSelect(day)}
                      className={`w-full h-full rounded-lg flex items-center justify-center text-sm transition-all duration-200
                        ${isSelected(day)
                          ? 'bg-gold-primary text-space-900 font-semibold shadow-[0_0_12px_rgba(212,168,75,0.4)]'
                          : isToday(day)
                            ? 'border border-gold-primary/50 text-white'
                            : 'text-white/70 hover:bg-white/10 hover:text-white'
                        }`}
                    >
                      {day}
                    </button>
                  )}
                </div>
              ))}
            </div>
          </>
        ) : (
          <>
            {/* Year grid */}
            <div className="grid grid-cols-5 gap-2 py-4">
              {years.filter(y => y >= decadeStart && y <= decadeStart + 9).map(year => (
                <button
                  key={year}
                  type="button"
                  onClick={() => handleYearSelect(year)}
                  className={`py-2 rounded-lg text-sm font-medium transition-all duration-200
                    ${year === viewDate.year
                      ? 'bg-gold-primary text-space-900 font-semibold'
                      : 'text-white/70 hover:bg-white/10 hover:text-white'
                    }`}
                >
                  {year}
                </button>
              ))}
            </div>

            {/* Month shortcuts when in year picker */}
            <div className="border-t border-white/10 pt-4 mt-2">
              <p className="text-[10px] text-white/40 uppercase tracking-wider mb-2 text-center">Quick Month</p>
              <div className="grid grid-cols-4 gap-1">
                {MONTHS.slice(0, 4).map((month, idx) => (
                  <button
                    key={month}
                    type="button"
                    onClick={() => {
                      setViewDate(prev => ({ ...prev, month: idx }));
                      setShowYearPicker(false);
                    }}
                    className="py-1.5 rounded text-xs text-white/60 hover:bg-white/10 hover:text-white transition-colors"
                  >
                    {month.slice(0, 3)}
                  </button>
                ))}
              </div>
              <div className="grid grid-cols-4 gap-1 mt-1">
                {MONTHS.slice(4, 8).map((month, idx) => (
                  <button
                    key={month}
                    type="button"
                    onClick={() => {
                      setViewDate(prev => ({ ...prev, month: idx + 4 }));
                      setShowYearPicker(false);
                    }}
                    className="py-1.5 rounded text-xs text-white/60 hover:bg-white/10 hover:text-white transition-colors"
                  >
                    {month.slice(0, 3)}
                  </button>
                ))}
              </div>
              <div className="grid grid-cols-4 gap-1 mt-1">
                {MONTHS.slice(8, 12).map((month, idx) => (
                  <button
                    key={month}
                    type="button"
                    onClick={() => {
                      setViewDate(prev => ({ ...prev, month: idx + 8 }));
                      setShowYearPicker(false);
                    }}
                    className="py-1.5 rounded text-xs text-white/60 hover:bg-white/10 hover:text-white transition-colors"
                  >
                    {month.slice(0, 3)}
                  </button>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

interface DateInputProps {
  value: string;
  onChange: (date: string) => void;
  label: string;
}

export const DateInput = ({ value, onChange, label }: DateInputProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const displayValue = value
    ? new Date(value + 'T00:00:00').toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    : '';

  return (
    <>
      <div className="relative w-full group mb-6">
        <label className="block text-white/50 text-xs mb-1 uppercase tracking-wider">
          {label}
        </label>
        <div className="flex items-center">
          <input
            type="text"
            readOnly
            value={displayValue}
            onClick={() => setIsOpen(true)}
            className="w-full bg-transparent border-b border-white/20 px-0 py-2 text-white cursor-pointer focus:outline-none focus:border-gold-primary transition-colors duration-300"
          />
          <button
            type="button"
            onClick={() => setIsOpen(true)}
            className="ml-2 text-white/50 hover:text-gold-primary transition-colors"
          >
            <CalendarIcon size={18} />
          </button>
        </div>
        <div className="absolute bottom-0 left-0 h-[2px] w-0 bg-gold-primary transition-all duration-500 ease-out group-focus-within:w-full shadow-[0_0_10px_rgba(212,168,75,0.5)]"></div>
      </div>
      {isOpen && (
        <CalendarPopup
          value={value}
          onChange={onChange}
          onClose={() => setIsOpen(false)}
        />
      )}
    </>
  );
};
