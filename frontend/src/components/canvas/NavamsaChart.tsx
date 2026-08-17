import { useAppStore } from '../../store/appStore';
import { SouthIndianChart } from './SouthIndianChart';
import { deriveRasiNames, toChartPlanets } from '../../utils/chart';

export const NavamsaChart = () => {
  const { horoscopeData } = useAppStore();
  if (!horoscopeData) return null;

  const { grahas, lagna, bhavas } = horoscopeData;

  // D9 boxes show Navamsa sign names (fall back to D1 labels where a sign
  // holds no graha in the Navamsa).
  const navamsaNames = deriveRasiNames(
    grahas.map((g) => ({ rasiIndex: g.navamsa_rasi_index, name: g.navamsa_rasi })),
  );
  const d1Names = deriveRasiNames(bhavas.map((b) => ({ rasiIndex: b.rasi_index, name: b.rasi })));
  const rasiNames = navamsaNames.map((name, i) =>
    /^\d+$/.test(name) ? d1Names[i] : name,
  );

  return (
    <SouthIndianChart
      title="D-9 Navamsa Chart"
      subtitle="Amma Natchathiram"
      lagnaRasiIndex={lagna.navamsa_rasi_index}
      planets={toChartPlanets(grahas, (g) => g.navamsa_rasi_index)}
      rasiNames={rasiNames}
    />
  );
};
