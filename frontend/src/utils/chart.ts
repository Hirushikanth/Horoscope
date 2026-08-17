import type { GrahaInfo, Trilingual } from '../types';
import type { ChartPlanet } from '../components/canvas/SouthIndianChart';

// Map English graha names to traditional 2-letter abbreviations
const PLANET_ABBR: Record<string, string> = {
  Sun: 'Su', Moon: 'Mo', Mars: 'Ma', Mercury: 'Me', Jupiter: 'Ju',
  Venus: 'Ve', Saturn: 'Sa', Rahu: 'Ra', Ketu: 'Ke',
};

export const planetAbbr = (name: string): string =>
  PLANET_ABBR[name] ?? name.substring(0, 2);

/** Convert graha list + a rasi selector into ChartPlanet entries. */
export const toChartPlanets = (
  grahas: GrahaInfo[],
  selectRasi: (g: GrahaInfo) => number,
): ChartPlanet[] =>
  grahas.map((g) => ({
    abbr: planetAbbr(g.name),
    rasiIndex: selectRasi(g),
    retrograde: g.retrograde,
    combust: g.combust,
  }));

/**
 * Build the 12 display names (index 0 = Aries) preferring Tamil, falling
 * back to English. Seeded from each graha's own trilingual rashi label so
 * the D9 grid shows the proper Navamsa sign names.
 */
export const deriveRasiNames = (
  labels: Array<{ rasiIndex: number; name: Trilingual }>,
): string[] => {
  const names: string[] = Array.from({ length: 12 }, (_, i) => i.toString());
  labels.forEach(({ rasiIndex, name }) => {
    names[rasiIndex] = name.tamil ?? name.english;
  });
  return names;
};
