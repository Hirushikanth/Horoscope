import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StarfieldBg } from './components/canvas/StarfieldBg';
import { BirthForm } from './components/horoscope/BirthForm';
import { Dashboard } from './components/horoscope/Dashboard';
import { useAppStore } from './store/appStore';
import { motion, AnimatePresence } from 'motion/react';

const queryClient = new QueryClient();

function MainApp() {
  const horoscopeData = useAppStore((state) => state.horoscopeData);
  const reset = useAppStore((state) => state.reset);

  return (
    <div className="relative min-h-screen bg-space-900 font-sans text-white overflow-x-hidden">
      <StarfieldBg />

      {/* Navigation / Header - Only shows when Dashboard is active */}
      <AnimatePresence>
        {horoscopeData && (
          <motion.nav 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="relative z-20 w-full p-6 max-w-6xl mx-auto flex justify-between items-center"
          >
            <h1 className="font-cinematic text-2xl font-bold tracking-widest text-white">JYOTISHA</h1>
            <button 
              onClick={reset} 
              className="text-xs uppercase tracking-widest text-gold-primary hover:text-gold-light border border-gold-primary/30 px-4 py-2 rounded-full hover:bg-gold-primary/10 transition-all"
            >
              New Calculation
            </button>
          </motion.nav>
        )}
      </AnimatePresence>

      <main className={`relative z-10 flex flex-col items-center ${!horoscopeData ? 'justify-center min-h-screen p-6' : 'p-4 pb-20'}`}>
        <AnimatePresence mode="wait">
          {!horoscopeData ? (
            // STATE 1: Landing Page & Form
            <motion.div
              key="landing"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.05, filter: "blur(10px)" }}
              transition={{ duration: 0.8, ease: "easeInOut" }}
              className="flex flex-col items-center w-full"
            >
              <div className="text-center mb-10">
                <h2 className="text-gold-primary tracking-[0.2em] text-sm uppercase mb-3 font-medium">Precision Vedic Astrology</h2>
                <h1 className="font-cinematic text-5xl md:text-7xl font-bold tracking-tight text-white drop-shadow-[0_0_15px_rgba(212,168,75,0.3)]">
                  Jyotisha
                </h1>
              </div>
              <BirthForm />
            </motion.div>
          ) : (
            // STATE 2: The Cinematic Dashboard
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, y: 30, filter: "blur(5px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="w-full"
            >
              <Dashboard />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MainApp />
    </QueryClientProvider>
  );
}