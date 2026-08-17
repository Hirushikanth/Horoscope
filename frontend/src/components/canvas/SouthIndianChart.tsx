import { useEffect, useRef } from 'react';
import { GlassCard } from '../ui/GlassCard';

// South Indian (Tamil) fixed 4×4 grid: signs never move, houses rotate.
// Pisces (12) is always top-left; signs run clockwise around the perimeter.
//   ┌─────────┬─────────┬─────────┬─────────┐
//   │ 12 Mīna │  1 Meṣa │ 2 Vṛṣabha│ 3 Mithuna│
//   ├─────────┼─────────┼─────────┼─────────┤
//   │ 11 Kumbha│         │         │  4 Karka │
//   ├─────────┼─────────┼─────────┼─────────┤
//   │ 10 Makara│         │         │  5 Siṁha  │
//   ├─────────┼─────────┼─────────┼─────────┤
//   │ 9 Dhanus │ 8 Vṛścika│ 7 Tulā  │  6 Kanyā  │
//   └─────────┴─────────┴─────────┴─────────┘
// Reference: docs/south-indian-horoscope.md §2
//
// row-major grid coordinate of each rasi (0 = Aries … 11 = Pisces):
const GRID_POS: Record<number, [number, number]> = {
  11: [0, 0], // Pisces   — top-left corner
  0: [0, 1],  // Aries    — top row
  1: [0, 2],  // Taurus   — top row
  2: [0, 3],  // Gemini   — top-right corner
  3: [1, 3],  // Cancer   — right column
  4: [2, 3],  // Leo      — right column
  5: [3, 3],  // Virgo    — bottom-right corner
  6: [3, 2],  // Libra    — bottom row
  7: [3, 1],  // Scorpio  — bottom row
  8: [3, 0],  // Sagittarius — bottom-left corner
  9: [2, 0],  // Capricorn — left column
  10: [1, 0], // Aquarius  — left column
};

export interface ChartPlanet {
  abbr: string;
  rasiIndex: number; // 0-based (0 = Aries … 11 = Pisces)
  retrograde?: boolean;
  combust?: boolean;
}

interface SouthIndianChartProps {
  title: string;
  subtitle?: string;
  lagnaRasiIndex: number;
  planets: ChartPlanet[];
  /** 12 display names, index 0 = Aries … 11 = Pisces (Tamil preferred). */
  rasiNames: string[];
}

export const SouthIndianChart = ({
  title,
  subtitle,
  lagnaRasiIndex,
  planets,
  rasiNames,
}: SouthIndianChartProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.parentElement?.getBoundingClientRect();
    const size = Math.min(rect?.width || 400, 520);

    canvas.width = size * dpr;
    canvas.height = size * dpr;
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, size, size);

    const cell = size / 4;
    const pad = 2;

    // ─────────────────────────── grid ─────────────────────────── #
    ctx.strokeStyle = '#D4A84B';
    ctx.lineWidth = 1.5;
    ctx.shadowColor = 'rgba(212, 168, 75, 0.35)';
    ctx.shadowBlur = 6;

    ctx.strokeRect(pad, pad, size - pad * 2, size - pad * 2);
    for (let i = 1; i < 4; i++) {
      ctx.beginPath();
      ctx.moveTo(pad + cell * i, pad);
      ctx.lineTo(pad + cell * i, size - pad);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(pad, pad + cell * i);
      ctx.lineTo(size - pad, pad + cell * i);
      ctx.stroke();
    }

    // Center 2×2 cells — permanently empty, subtly darkened
    ctx.fillStyle = 'rgba(0, 0, 0, 0.25)';
    ctx.fillRect(pad + cell, pad + cell, cell * 2, cell * 2);

    ctx.shadowBlur = 0;

    // ─────────────────────── house mapping ─────────────────────── #
    // Houses rotate clockwise from the lagna box: next sign clockwise is
    // rasiIndex + 1 (wrapping 12 → 1).
    const houseOf = (rasiIndex: number) =>
      ((rasiIndex - lagnaRasiIndex) % 12 + 12) % 12 + 1;

    const byRasi = new Map<number, ChartPlanet[]>();
    planets.forEach((p) => {
      const list = byRasi.get(p.rasiIndex) ?? [];
      list.push(p);
      byRasi.set(p.rasiIndex, list);
    });

    for (let rasiIndex = 0; rasiIndex < 12; rasiIndex++) {
      const [row, col] = GRID_POS[rasiIndex];
      const x = pad + col * cell;
      const y = pad + row * cell;
      const cx = x + cell / 2;
      const cy = y + cell / 2;
      const isLagna = rasiIndex === lagnaRasiIndex;

      // Lagna corner darkened + diagonal slash (/)
      if (isLagna) {
        ctx.fillStyle = 'rgba(212, 168, 75, 0.10)';
        ctx.fillRect(x, y, cell, cell);
        ctx.strokeStyle = 'rgba(212, 168, 75, 0.85)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x + cell * 0.18, y + cell * 0.82);
        ctx.lineTo(x + cell * 0.82, y + cell * 0.18);
        ctx.stroke();
        ctx.strokeStyle = '#D4A84B';
        ctx.lineWidth = 1.5;
      }

      // House number — top-left corner of the box
      ctx.fillStyle = 'rgba(212, 168, 75, 0.75)';
      ctx.font = '600 11px Inter, sans-serif';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'top';
      ctx.fillText(String(houseOf(rasiIndex)), x + 6, y + 5);

      // Rashi name — Tamil preferred, English fallback
      ctx.fillStyle = 'rgba(212, 168, 75, 0.55)';
      ctx.font = '500 10px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'alphabetic';
      ctx.fillText(rasiNames[rasiIndex] ?? '', cx, y + 15);

      // Planets — stacked under the sign name
      const occupants = byRasi.get(rasiIndex) ?? [];
      ctx.font = '600 13px Inter, sans-serif';
      occupants.forEach((planet, pIndex) => {
        const py = cy + (pIndex - (occupants.length - 1) / 2) * 17 + 8;
        ctx.fillStyle = '#FFFFFF';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(planet.abbr, cx - (planet.retrograde || planet.combust ? 4 : 0), py);

        // Markers: R = Vakram (retrograde), C = Asthamangam (combust)
        if (planet.retrograde || planet.combust) {
          ctx.font = '700 10px Inter, sans-serif';
          ctx.fillStyle = planet.retrograde ? '#FB923C' : '#F87171';
          ctx.fillText(planet.retrograde ? 'R' : 'C', cx + 9, py);
          ctx.fillStyle = '#FFFFFF';
          ctx.font = '600 13px Inter, sans-serif';
        }
      });
    }
  }, [lagnaRasiIndex, planets, rasiNames]);

  return (
    <GlassCard className="w-full flex flex-col items-center justify-center p-6 md:p-8">
      <div className="w-full mb-6 text-center">
        <h2 className="text-gold-primary tracking-[0.2em] text-xs uppercase mb-1 font-medium">
          {title}
        </h2>
        {subtitle && <h3 className="font-cinematic text-2xl font-bold text-white">{subtitle}</h3>}
      </div>

      <div className="relative w-full max-w-[420px] aspect-square flex items-center justify-center">
        <canvas ref={canvasRef} className="block" />
      </div>

      <div className="w-full mt-6 grid grid-cols-2 md:grid-cols-3 gap-2 text-center text-[10px] text-gray-400 uppercase tracking-widest">
        <span>Su: Sun</span>
        <span>Mo: Moon</span>
        <span>Ma: Mars</span>
        <span>Me: Mercury</span>
        <span>Ju: Jupiter</span>
        <span>Ve: Venus</span>
        <span>Sa: Saturn</span>
        <span>Ra/Ke: Nodes</span>
        <span>R: Vakram · C: Asthamangam</span>
      </div>
    </GlassCard>
  );
};
