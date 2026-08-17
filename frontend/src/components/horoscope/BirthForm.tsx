import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { GlassCard } from '../ui/GlassCard';
import { Input } from '../ui/Input';
import { GlowButton } from '../ui/GlowButton';
import { DateInput } from '../ui/Calendar';
import { Clock } from '../ui/Clock';
import { fetchJathakam, fetchPanchangam } from '../../utils/api';
import type { BirthRequest } from '../../types';
import { useAppStore } from '../../store/appStore';
import { motion } from 'motion/react';

export const BirthForm = () => {
  const setHoroscopeData = useAppStore((state) => state.setHoroscopeData);
  const setPanchangamData = useAppStore((state) => state.setPanchangamData);

  // Pre-filled with Colombo, Sri Lanka for instant testing
  const [formData, setFormData] = useState<BirthRequest>({
    date: '1995-05-15',
    time: '10:30:00',
    latitude: 6.9271,
    longitude: 79.8612,
    timezone: 'Asia/Colombo',
  });

  const mutation = useMutation({
    mutationFn: async (data: BirthRequest) => {
      const [jathakam, panchangam] = await Promise.all([
        fetchJathakam(data),
        fetchPanchangam(data),
      ]);
      return { jathakam, panchangam };
    },
    onSuccess: ({ jathakam, panchangam }) => {
      setHoroscopeData(jathakam, formData);
      setPanchangamData(panchangam);
    },
    onError: (error) => {
      console.error('API Error:', error);
      alert('Failed to connect to Jyotisha API. Is your Python backend running?');
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [id]: id === 'latitude' || id === 'longitude' ? parseFloat(value) : value,
    }));
  };

  return (
    <GlassCard className="w-full max-w-md p-8">
      <div className="text-center mb-8">
        <h2 className="font-cinematic text-3xl font-bold text-white drop-shadow-[0_0_10px_rgba(212,168,75,0.4)]">
          Cosmic Coordinates
        </h2>
        <p className="text-gray-400 text-sm mt-2">Enter birth details to compute destiny.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex gap-4">
          <DateInput
            value={formData.date}
            onChange={(date) => setFormData(prev => ({ ...prev, date }))}
            label="Date of Birth"
          />
          <Clock
            value={formData.time}
            onChange={(time) => setFormData(prev => ({ ...prev, time }))}
          />
        </div>
        
        <div className="flex gap-4">
          <Input id="latitude" type="number" step="any" label="Latitude" required value={formData.latitude} onChange={handleChange} />
          <Input id="longitude" type="number" step="any" label="Longitude" required value={formData.longitude} onChange={handleChange} />
        </div>

        <Input id="timezone" type="text" label="IANA Timezone" required value={formData.timezone} onChange={handleChange} />

        <div className="pt-4">
          <GlowButton type="submit" isLoading={mutation.isPending}>
            Generate Horoscope
          </GlowButton>
        </div>
      </form>

      {/* Error state display */}
      {mutation.isError && (
        <motion.p initial={{ opacity:0 }} animate={{ opacity:1 }} className="text-red-400 text-sm text-center mt-4">
          Connection failed. Ensure backend is running on port 8000.
        </motion.p>
      )}
    </GlassCard>
  );
};