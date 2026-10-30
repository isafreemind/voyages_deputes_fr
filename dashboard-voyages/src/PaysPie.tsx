import {useMemo} from 'react';
import {Cell, Pie, PieChart, ResponsiveContainer, Tooltip} from 'recharts';
import {type Voyage} from './data';
import './deputies-pie.css';
import './organisations-pie.css';

const colors = ['#297e69', '#68ad93', '#375c9b', '#c68e4b', '#8b73a8', '#be6c69', '#70a9b5', '#a5a35e', '#557a64', '#bf86a6', '#6387ba', '#bd7957'];
export const NON_IDENTIFIE = '__non_identifie__';

export function PaysPie({voyages, onSelect}: {voyages: Voyage[]; onSelect: (pays: string) => void}) {
  const slices = useMemo(() => {
    const counts = new Map<string, number>();
    for (const voyage of voyages) {
      const countries = new Set(voyage.destination.pays_reperes);
      if (!countries.size) countries.add(NON_IDENTIFIE);
      for (const country of countries) counts.set(country, (counts.get(country) || 0) + 1);
    }
    return [...counts].map(([id, value]) => ({id, name: id === NON_IDENTIFIE ? 'Pays non identifié' : id, value})).sort((a,b) => b.value - a.value || a.name.localeCompare(b.name,'fr'));
  }, [voyages]);
  const total = slices.reduce((sum, slice) => sum + slice.value, 0);
  return <section className="card organisations-pie pays-pie" aria-labelledby="pays-pie-title">
    <div className="organisations-pie-header"><span className="section-kicker">DESTINATIONS · PAYS</span><h3 id="pays-pie-title">Répartition par pays de destination</h3><p>Nombre de déclarations associées à chaque pays selon les filtres actifs.</p></div>
    {total === 0 ? <p className="organisations-pie-empty">Aucune destination pour cette sélection.</p> : <div className="organisations-pie-layout">
      <div className="deputies-pie-chart organisations-pie-chart" role="img" aria-label={`Répartition de ${total} destinations et pays non identifiés. Le détail figure dans la liste.`}>
        <ResponsiveContainer width="100%" height="100%"><PieChart>
          <Pie data={slices} dataKey="value" nameKey="name" innerRadius="58%" outerRadius="88%" stroke="#fff" strokeWidth={1}>
            {slices.map((slice,index) => <Cell key={slice.id} fill={slice.id === NON_IDENTIFIE ? '#aab6ae' : colors[index % colors.length]} onClick={() => onSelect(slice.id)} style={{cursor:'pointer'}}/>)}
          </Pie><Tooltip formatter={(value:number) => [`${value} déclaration${value > 1 ? 's' : ''}`, 'Destination']}/>
        </PieChart></ResponsiveContainer>
        <div className="deputies-pie-total" aria-hidden="true"><strong>{total}</strong><span>destinations</span></div>
      </div>
      <div className="deputies-pie-legend organisations-pie-legend" aria-label="Détail par pays">
        {slices.map((slice,index) => <button type="button" key={slice.id} onClick={() => onSelect(slice.id)} aria-label={`${slice.name} : ${slice.value} déclaration${slice.value > 1 ? 's' : ''}, ${(slice.value / total * 100).toLocaleString('fr-FR',{maximumFractionDigits:1})} % des destinations`}>
          <span className="deputies-pie-swatch" style={{backgroundColor:slice.id === NON_IDENTIFIE ? '#aab6ae' : colors[index % colors.length]}} aria-hidden="true"/><span className="deputies-pie-name">{slice.name}</span><span className="deputies-pie-value">{slice.value}</span><span className="deputies-pie-percent">{(slice.value / total * 100).toLocaleString('fr-FR',{maximumFractionDigits:1})} %</span>
        </button>)}
      </div>
    </div>}
    <p className="organisations-pie-note">Les pays sont reconnus dans la destination déclarée, notamment à partir de certains lieux répertoriés. Une déclaration couvrant plusieurs pays compte dans chacun ; les pourcentages portent sur les destinations comptées. Les lieux sans pays reconnu figurent dans « Pays non identifié ».</p>
  </section>;
}
