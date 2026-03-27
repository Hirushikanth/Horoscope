import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { GlassCard } from '../ui/GlassCard';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { GlowButton } from '../ui/GlowButton';
import { fetchMatching } from '../../utils/api';
import { type MatchingInput } from '../../types';
import { useAppStore } from '../../store/appStore';
import { motion } from 'motion/react';
import { HeartHandshake } from 'lucide-react';

export const MatchingForm = () => {
  const setMatchingData = useAppStore((state) => state.setMatchingData);

  // Pre-filled with two coordinates for instant testing (Delhi vs Mumbai)
  const [formData, setFormData] = useState<MatchingInput>({
    bride: {
      date: '1995-05-15',
      time: '10:30:00',
      latitude: 28.6139,
      longitude: 77.2090,
      timezone: 'Asia/Kolkata',
    },
    groom: {
      date: '1992-08-20',
      time: '14:45:00',
      latitude: 19.0760,
      longitude: 72.8777,
      timezone: 'Asia/Kolkata',
    },
    system: 'both',
  });

  const mutation = useMutation({
    mutationFn: fetchMatching,
    onSuccess: (data) => {
      setMatchingData(data, formData);
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

  const handleBrideChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      bride: {
        ...prev.bride,
        [id]: id === 'latitude' || id === 'longitude' ? parseFloat(value) : value,
      }
    }));
  };

  const handleGroomChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      groom: {
        ...prev.groom,
        [id]: id === 'latitude' || id === 'longitude' ? parseFloat(value) : value,
      }
    }));
  };

  return (
    <div className="w-full max-w-5xl flex flex-col gap-6">
      
      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        
        {/* System Selector Card (Top Center) */}
        <div className="flex justify-center">
          <GlassCard className="w-full max-w-md p-6 text-center">
            <h2 className="font-cinematic text-2xl font-bold text-white mb-4">Matching Tradition</h2>
            <Select 
              id="system"
              label="Select Astrological System"
              value={formData.system}
              onChange={(e) => setFormData(prev => ({ ...prev, system: e.target.value as any }))}
              options={[
                { value: 'both', label: 'Comprehensive (North & South Combined)' },
                { value: 'north_indian', label: 'Ashta Koota Milan (North Indian 36 Points)' },
                { value: 'south_indian', label: 'Dashakoota Poruthams (South Indian 10 Points)' },
              ]}
            />
          </GlassCard>
        </div>

        {/* Dual Form Cards (Side-by-Side on Desktop) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
          
          {/* BRIDE CARD */}
          <GlassCard className="p-8 relative overflow-hidden group">
            {/* Subtle pink/gold glow for Bride side */}
            <div className="absolute -top-20 -left-20 w-48 h-48 bg-pink-500/10 rounded-full blur-3xl group-hover:bg-pink-500/20 transition-all duration-700"></div>
            
            <div className="relative z-10">
              <h3 className="font-cinematic text-3xl font-bold text-gold-light mb-1">Bride Details</h3>
              <p className="text-gray-400 text-xs tracking-widest uppercase mb-8 border-b border-white/10 pb-4">Natal Chart Data</p>
              
              <div className="flex gap-4">
                <Input id="date" type="date" label="Date of Birth" required value={formData.bride.date} onChange={handleBrideChange} />
                <Input id="time" type="time" step="1" label="Time of Birth" required value={formData.bride.time} onChange={handleBrideChange} />
              </div>
              <div className="flex gap-4">
                <Input id="latitude" type="number" step="any" label="Latitude" required value={formData.bride.latitude} onChange={handleBrideChange} />
                <Input id="longitude" type="number" step="any" label="Longitude" required value={formData.bride.longitude} onChange={handleBrideChange} />
              </div>
              <Input id="timezone" type="text" label="IANA Timezone" required value={formData.bride.timezone} onChange={handleBrideChange} />
            </div>
          </GlassCard>

          {/* GROOM CARD */}
          <GlassCard className="p-8 relative overflow-hidden group">
            {/* Subtle blue/gold glow for Groom side */}
            <div className="absolute -top-20 -right-20 w-48 h-48 bg-blue-500/10 rounded-full blur-3xl group-hover:bg-blue-500/20 transition-all duration-700"></div>
            
            <div className="relative z-10">
              <h3 className="font-cinematic text-3xl font-bold text-gold-light mb-1">Groom Details</h3>
              <p className="text-gray-400 text-xs tracking-widest uppercase mb-8 border-b border-white/10 pb-4">Natal Chart Data</p>
              
              <div className="flex gap-4">
                <Input id="date" type="date" label="Date of Birth" required value={formData.groom.date} onChange={handleGroomChange} />
                <Input id="time" type="time" step="1" label="Time of Birth" required value={formData.groom.time} onChange={handleGroomChange} />
              </div>
              <div className="flex gap-4">
                <Input id="latitude" type="number" step="any" label="Latitude" required value={formData.groom.latitude} onChange={handleGroomChange} />
                <Input id="longitude" type="number" step="any" label="Longitude" required value={formData.groom.longitude} onChange={handleGroomChange} />
              </div>
              <Input id="timezone" type="text" label="IANA Timezone" required value={formData.groom.timezone} onChange={handleGroomChange} />
            </div>
          </GlassCard>

        </div>

        {/* Big Submit Button */}
        <div className="w-full max-w-md mx-auto mt-4 relative z-20">
          <GlowButton type="submit" isLoading={mutation.isPending}>
            <HeartHandshake className="w-5 h-5 mr-2" />
            Calculate Cosmic Union
          </GlowButton>
        </div>

      </form>

      {/* Error state display */}
      {mutation.isError && (
        <motion.p initial={{ opacity:0 }} animate={{ opacity:1 }} className="text-red-400 text-sm text-center mt-2">
          Connection failed. Ensure backend is running on port 8000.
        </motion.p>
      )}

    </div>
  );
};