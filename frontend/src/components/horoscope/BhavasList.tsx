import { motion } from 'motion/react';
import { useAppStore } from '../../store/appStore';
import { GlassCard } from '../ui/GlassCard';

export const BhavasList = () => {
  const { horoscopeData } = useAppStore();
  if (!horoscopeData) return null;

  const { bhavas } = horoscopeData;

  return (
    <div className="w-full">
      <div className="mb-8 text-center">
        <h2 className="font-cinematic text-3xl font-bold text-white">The 12 Bhavas</h2>
        <p className="text-sm text-gray-400 mt-2 italic">Your life's departments and their cosmic influences</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {bhavas.map((bhava: any, index: number) => (
          <motion.div
            key={bhava.house}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05, duration: 0.5 }}
            className="group [perspective:1000px] h-[320px]"
          >
            <div className="relative w-full h-full transition-all duration-700 [transform-style:preserve-3d] group-hover:[transform:rotateY(180deg)] group-hover:-translate-y-2">
              {/* Front Side */}
              <div className="absolute inset-0 [backface-visibility:hidden]">
                <GlassCard className="h-full w-full p-6 flex flex-col items-center justify-between text-center border-white/5 group-hover:border-gold-primary/30">
                  {/* Background Glow */}
                  <div className="absolute inset-0 bg-gradient-to-br from-gold-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  
                  <div className="relative z-10 w-full">
                    <div className="flex justify-between items-start mb-4">
                      <span className="text-[10px] font-bold text-gold-primary/60 uppercase tracking-[0.2em]">
                        House {bhava.house}
                      </span>
                      {bhava.occupants.length > 0 && (
                        <div className="flex gap-1">
                          {bhava.occupants.map((_: any, i: number) => (
                            <div key={i} className="w-1.5 h-1.5 rounded-full bg-gold-primary/60 shadow-[0_0_8px_rgba(212,168,75,0.5)]" />
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <div className="py-4">
                      <h3 className="font-cinematic text-6xl font-bold text-white mb-2 tracking-tighter">
                        {bhava.house}
                      </h3>
                      <div className="inline-block px-3 py-1 rounded-full bg-gold-primary/10 border border-gold-primary/20">
                        <p className="text-[11px] font-bold text-gold-light tracking-[0.15em] uppercase">
                          {bhava.sign}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="relative z-10 w-full pt-4 border-t border-white/5 space-y-4">
                    <div>
                      <p className="text-[9px] text-gray-500 uppercase tracking-widest mb-2 font-semibold">Occupants</p>
                      <div className="flex flex-wrap justify-center gap-1.5 min-h-[1.5rem]">
                        {bhava.occupants.length > 0 ? (
                          bhava.occupants.map((occupant: string) => (
                            <span key={occupant} className="text-[10px] px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-white font-medium">
                              {occupant}
                            </span>
                          ))
                        ) : (
                          <span className="text-[10px] text-gray-600 italic">No planetary occupants</span>
                        )}
                      </div>
                    </div>

                    <div className="pt-2">
                      <p className="text-[10px] text-gold-primary/50 uppercase tracking-[0.2em] font-medium">Lord: <span className="text-white">{bhava.lord}</span></p>
                    </div>
                  </div>
                </GlassCard>
              </div>

              {/* Back Side */}
              <div className="absolute inset-0 [backface-visibility:hidden] [transform:rotateY(180deg)]">
                <GlassCard className="h-full w-full p-6 flex flex-col justify-center items-center text-center border-gold-primary/20 bg-black/40">
                  <div className="absolute top-4 left-0 right-0 flex justify-center">
                    <div className="h-[1px] w-12 bg-gold-primary/30" />
                  </div>
                  
                  <div className="space-y-6">
                    <div>
                      <p className="text-gold-primary text-[11px] uppercase tracking-[0.3em] mb-3 font-bold">Signification</p>
                      <p className="text-white/90 text-sm leading-relaxed font-light px-2">
                        {bhava.signification}
                      </p>
                    </div>

                    <div className="pt-6 border-t border-white/10 w-full">
                      <p className="text-gold-light/60 text-[10px] uppercase tracking-widest mb-2 font-semibold">Themes</p>
                      <p className="text-gray-400 text-xs italic leading-relaxed px-2">
                        {bhava.keywords}
                      </p>
                    </div>
                  </div>

                  <div className="absolute bottom-4 left-0 right-0 flex justify-center">
                    <div className="h-[1px] w-12 bg-gold-primary/30" />
                  </div>
                </GlassCard>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};