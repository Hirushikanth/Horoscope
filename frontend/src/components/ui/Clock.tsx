import { useState, useRef, useEffect } from 'react';
import { ChevronUp, ChevronDown, Clock as ClockIcon } from 'lucide-react';

interface ClockPopupProps {
  value: string;
  onChange: (time: string) => void;
  onClose: () => void;
}

export const ClockPopup = ({ value, onChange, onClose }: ClockPopupProps) => {
  const parseTime = (timeStr: string) => {
    if (!timeStr) return { hours: 10, minutes: 0, period: 'AM' };
    const [time, period] = timeStr.split(' ');
    const [h, m] = time.split(':').map(Number);
    return {
      hours: h === 12 ? 12 : h % 12 || 12,
      minutes: m,
      period: period || 'AM'
    };
  };

  const [selected, setSelected] = useState(() => parseTime(value));
  const [editingHours, setEditingHours] = useState(false);
  const [editingMinutes, setEditingMinutes] = useState(false);
  const [hoursInput, setHoursInput] = useState('');
  const [minutesInput, setMinutesInput] = useState('');
  const hoursRef = useRef<HTMLInputElement>(null);
  const minutesRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editingHours && hoursRef.current) {
      hoursRef.current.focus();
      hoursRef.current.select();
    }
  }, [editingHours]);

  useEffect(() => {
    if (editingMinutes && minutesRef.current) {
      minutesRef.current.focus();
      minutesRef.current.select();
    }
  }, [editingMinutes]);

  const handleHoursChange = (delta: number) => {
    const newHours = ((selected.hours - 1 + delta + 12) % 12) + 1;
    setSelected(prev => ({ ...prev, hours: newHours }));
  };

  const handleMinutesChange = (delta: number) => {
    const newMinutes = (selected.minutes + delta) % 60;
    setSelected(prev => ({ ...prev, minutes: newMinutes < 0 ? 59 : newMinutes }));
  };

  const handleHoursInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value.replace(/\D/g, '');
    setHoursInput(val);
  };

  const handleHoursInputBlur = () => {
    setEditingHours(false);
    if (hoursInput) {
      const num = parseInt(hoursInput, 10);
      if (!isNaN(num) && num >= 1 && num <= 12) {
        setSelected(prev => ({ ...prev, hours: num }));
      }
    }
    setHoursInput('');
  };

  const handleHoursInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleHoursInputBlur();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      handleHoursChange(1);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      handleHoursChange(-1);
    }
  };

  const handleMinutesInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value.replace(/\D/g, '').slice(0, 2);
    setMinutesInput(val);
  };

  const handleMinutesInputBlur = () => {
    setEditingMinutes(false);
    if (minutesInput) {
      const num = parseInt(minutesInput, 10);
      if (!isNaN(num) && num >= 0 && num <= 59) {
        setSelected(prev => ({ ...prev, minutes: num }));
      }
    }
    setMinutesInput('');
  };

  const handleMinutesInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleMinutesInputBlur();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      handleMinutesChange(1);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      handleMinutesChange(-1);
    }
  };

  const applyTime = () => {
    let hours24 = selected.hours;
    if (selected.period === 'PM' && selected.hours !== 12) hours24 += 12;
    if (selected.period === 'AM' && selected.hours === 12) hours24 = 0;

    const timeStr = `${hours24.toString().padStart(2, '0')}:${selected.minutes.toString().padStart(2, '0')}:00`;
    onChange(timeStr);
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/30"
      onClick={onClose}
    >
      <div
        className="p-6 rounded-xl glass-card min-w-[320px]"
        onClick={e => e.stopPropagation()}
      >
        {/* Time Display - Editable */}
        <div className="text-center mb-6">
          <div className="flex items-center justify-center gap-2">
            {/* Hours */}
            {editingHours ? (
              <input
                ref={hoursRef}
                type="text"
                value={hoursInput}
                onChange={handleHoursInputChange}
                onBlur={handleHoursInputBlur}
                onKeyDown={handleHoursInputKeyDown}
                className="w-16 bg-transparent border-b-2 border-gold-primary text-center font-cinematic text-4xl text-white outline-none"
                maxLength={2}
              />
            ) : (
              <button
                type="button"
                onClick={() => {
                  setHoursInput(selected.hours.toString());
                  setEditingHours(true);
                }}
                className="w-16 font-cinematic text-4xl text-white hover:text-gold-primary transition-colors cursor-pointer"
              >
                {selected.hours.toString().padStart(2, '0')}
              </button>
            )}

            <span className="font-cinematic text-4xl text-white/40">:</span>

            {/* Minutes */}
            {editingMinutes ? (
              <input
                ref={minutesRef}
                type="text"
                value={minutesInput}
                onChange={handleMinutesInputChange}
                onBlur={handleMinutesInputBlur}
                onKeyDown={handleMinutesInputKeyDown}
                className="w-16 bg-transparent border-b-2 border-gold-primary text-center font-cinematic text-4xl text-white outline-none"
                maxLength={2}
              />
            ) : (
              <button
                type="button"
                onClick={() => {
                  setMinutesInput(selected.minutes.toString().padStart(2, '0'));
                  setEditingMinutes(true);
                }}
                className="w-16 font-cinematic text-4xl text-white hover:text-gold-primary transition-colors cursor-pointer"
              >
                {selected.minutes.toString().padStart(2, '0')}
              </button>
            )}

            {/* Period */}
            <span className="ml-2 font-cinematic text-2xl text-gold-primary">
              {selected.period}
            </span>
          </div>
          <p className="text-[10px] text-white/40 mt-2 uppercase tracking-wider">Click numbers to edit</p>
        </div>

        {/* Time Pickers */}
        <div className="flex items-center justify-center gap-6">
          {/* Hours */}
          <div className="flex flex-col items-center">
            <button
              type="button"
              onClick={() => handleHoursChange(1)}
              className="p-2 rounded-lg hover:bg-white/10 text-white/70 hover:text-white transition-colors"
            >
              <ChevronUp size={24} />
            </button>
            <div className="w-16 flex items-center justify-center">
              <span className="font-cinematic text-xl text-white/50">
                {selected.hours.toString().padStart(2, '0')}
              </span>
            </div>
            <button
              type="button"
              onClick={() => handleHoursChange(-1)}
              className="p-2 rounded-lg hover:bg-white/10 text-white/70 hover:text-white transition-colors"
            >
              <ChevronDown size={24} />
            </button>
            <span className="text-[10px] text-white/40 uppercase mt-1">Hours</span>
          </div>

          <span className="font-cinematic text-3xl text-white/40 -mt-8">:</span>

          {/* Minutes */}
          <div className="flex flex-col items-center">
            <button
              type="button"
              onClick={() => handleMinutesChange(1)}
              className="p-2 rounded-lg hover:bg-white/10 text-white/70 hover:text-white transition-colors"
            >
              <ChevronUp size={24} />
            </button>
            <div className="w-16 flex items-center justify-center">
              <span className="font-cinematic text-xl text-white/50">
                {selected.minutes.toString().padStart(2, '0')}
              </span>
            </div>
            <button
              type="button"
              onClick={() => handleMinutesChange(-1)}
              className="p-2 rounded-lg hover:bg-white/10 text-white/70 hover:text-white transition-colors"
            >
              <ChevronDown size={24} />
            </button>
            <span className="text-[10px] text-white/40 uppercase mt-1">Minutes</span>
          </div>

          {/* AM/PM Toggle */}
          <div className="flex flex-col items-center ml-2">
            <button
              type="button"
              onClick={() => setSelected(prev => ({ ...prev, period: 'AM' }))}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                selected.period === 'AM' ? 'text-gold-primary bg-gold-primary/20' : 'text-white/30'
              }`}
            >
              AM
            </button>
            <button
              type="button"
              onClick={() => setSelected(prev => ({ ...prev, period: 'PM' }))}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 mt-1 ${
                selected.period === 'PM' ? 'text-gold-primary bg-gold-primary/20' : 'text-white/30'
              }`}
            >
              PM
            </button>
            <span className="text-[10px] text-white/40 uppercase mt-2">Period</span>
          </div>
        </div>

        {/* Apply Button */}
        <button
          type="button"
          onClick={applyTime}
          className="w-full mt-6 py-3 rounded-lg bg-gold-primary/20 border border-gold-primary/30 text-gold-light font-medium hover:bg-gold-primary/30 transition-colors"
        >
          Apply Time
        </button>
      </div>
    </div>
  );
};

interface ClockProps {
  value: string;
  onChange: (time: string) => void;
}

export const Clock = ({ value, onChange }: ClockProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const parseTime = (timeStr: string) => {
    if (!timeStr) return { hours: 10, minutes: 0, period: 'AM' };
    const [time, period] = timeStr.split(' ');
    const [h, m] = time.split(':').map(Number);
    return {
      hours: h === 12 ? 12 : h % 12 || 12,
      minutes: m,
      period: period || 'AM'
    };
  };

  const displayTime = () => {
    const { hours, minutes, period } = parseTime(value);
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')} ${period}`;
  };

  return (
    <>
      <div className="relative w-full group mb-6">
        <label className="block text-white/50 text-xs mb-1 uppercase tracking-wider">
          Time of Birth
        </label>
        <div className="flex items-center">
          <input
            type="text"
            readOnly
            value={displayTime()}
            onClick={() => setIsOpen(true)}
            className="w-full bg-transparent border-b border-white/20 px-0 py-2 text-white cursor-pointer focus:outline-none focus:border-gold-primary transition-colors duration-300"
          />
          <button
            type="button"
            onClick={() => setIsOpen(true)}
            className="ml-2 text-white/50 hover:text-gold-primary transition-colors"
          >
            <ClockIcon size={18} />
          </button>
        </div>
        <div className="absolute bottom-0 left-0 h-[2px] w-0 bg-gold-primary transition-all duration-500 ease-out group-focus-within:w-full shadow-[0_0_10px_rgba(212,168,75,0.5)]"></div>
      </div>
      {isOpen && (
        <ClockPopup
          value={value}
          onChange={onChange}
          onClose={() => setIsOpen(false)}
        />
      )}
    </>
  );
};
