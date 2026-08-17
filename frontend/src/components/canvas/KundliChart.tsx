import { useAppStore } from '../../store/appStore';
import { SouthIndianChart } from './SouthIndianChart';
import { deriveRasiNames, toChartPlanets } from '../../utils/chart';

export const KundliChart = () => {
  const { horoscopeData } = useAppStore();
  if (!horoscopeData) return null;

  const { grahas, lagna } = horoscopeData;

  const rasiNames = deriveRasiNames(grahas.map((g) => ({ rasiIndex: g.rasi_index, name: g.rasi })));

  return (
    <SouthIndianChart
      title="D-1 Rasi Chart"
      subtitle="Lagna Kundli"
      lagnaRasiIndex={lagna.rasi_index}
      planets={toChartPlanets(grahas, (g) => g.rasi_index)}
      rasiNames={rasiNames}
    />
  );
};
