import {useMemo} from 'react';
import {Cell, Pie, PieChart, ResponsiveContainer, Tooltip} from 'recharts';
import {orgMap, type Voyage} from './data';
import './deputies-pie.css';
import './organisations-pie.css';

const colors = ['#297e69', '#68ad93', '#375c9b', '#c68e4b', '#8b73a8', '#be6c69', '#70a9b5', '#a5a35e', '#557a64', '#bf86a6', '#6387ba', '#bd7957'];

export function OrganisationsPie({voyages, onSelect}: {voyages: Voyage[]; onSelect: (id: string) => void}) {
  const slices = useMemo(() => {
    const counts = new Map<string, number>();
    for (const voyage of voyages) {
      const ids = new Set(voyage.organisations.filter(relation => relation.roles.includes('cite_dans_financement') && orgMap.has(relation.organisation_id)).map(relation => relation.organisation_id));
      for (const id of ids) counts.set(id, (counts.get(id) || 0) + 1);
    }
    return [...counts].map(([id, value]) => ({id, name:orgMap.get(id)!.nom, value})).sort((a,b) => b.value - a.value || a.name.localeCompare(b.name,'fr'));
  }, [voyages]);
  const total = slices.reduce((sum, slice) => sum + slice.value, 0);

  return <section className="card organisations-pie" aria-labelledby="organisations-pie-title">
    <div className="organisations-pie-header"><span className="section-kicker">FINANCEMENT · ORGANISATIONS RECONNUES</span><h3 id="organisations-pie-title">Répartition des organisations citées</h3><p>Nombre de déclarations où chaque organisation apparaît dans le champ « Tiers financeur ».</p></div>
    {total === 0 ? <p className="organisations-pie-empty">Aucune organisation reconnue dans le champ financement pour cette sélection.</p> :
      <div className="organisations-pie-layout">
        <div className="deputies-pie-chart organisations-pie-chart" role="img" aria-label={`Répartition de ${total} citations entre ${slices.length} organisations. Le détail figure dans la liste.`}>
          <ResponsiveContainer width="100%" height="100%"><PieChart>
            <Pie data={slices} dataKey="value" nameKey="name" innerRadius="58%" outerRadius="88%" stroke="#fff" strokeWidth={1}>
              {slices.map((slice,index) => <Cell key={slice.id} fill={colors[index % colors.length]} onClick={() => onSelect(slice.id)} style={{cursor:'pointer'}}/>)}
            </Pie>
            <Tooltip formatter={(value:number) => [`${value} déclaration${value > 1 ? 's' : ''}`, 'Organisation citée']}/>
          </PieChart></ResponsiveContainer>
          <div className="deputies-pie-total" aria-hidden="true"><strong>{total}</strong><span>citations</span></div>
        </div>
        <div className="deputies-pie-legend organisations-pie-legend" aria-label="Détail par organisation">
          {slices.map((slice,index) => <button type="button" key={slice.id} onClick={() => onSelect(slice.id)} aria-label={`${slice.name} : ${slice.value} déclaration${slice.value > 1 ? 's' : ''}, ${(slice.value / total * 100).toLocaleString('fr-FR',{maximumFractionDigits:1})} % des citations`}>
            <span className="deputies-pie-swatch" style={{backgroundColor:colors[index % colors.length]}} aria-hidden="true"/><span className="deputies-pie-name">{slice.name}</span><span className="deputies-pie-value">{slice.value}</span><span className="deputies-pie-percent">{(slice.value / total * 100).toLocaleString('fr-FR',{maximumFractionDigits:1})} %</span>
          </button>)}
        </div>
      </div>}
    <p className="organisations-pie-note">Les pourcentages portent sur les citations d’organisations reconnues. Une déclaration peut citer plusieurs organisations et compter pour chacune ; les noms ambigus ou non reconnus sont exclus. Une citation ne prouve pas une prise en charge totale.</p>
  </section>;
}
