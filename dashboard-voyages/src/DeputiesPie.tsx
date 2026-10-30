import {Cell, Pie, PieChart, ResponsiveContainer, Tooltip} from 'recharts';
import './deputies-pie.css';

const colors = ['#297e69', '#68ad93', '#375c9b', '#c68e4b', '#8b73a8', '#be6c69', '#70a9b5', '#a5a35e', '#557a64', '#bf86a6', '#6387ba', '#bd7957'];

export function DeputiesPie({deputies, total, onDeputy}: {
  deputies: [string, number][];
  total: number;
  onDeputy: (name: string) => void;
}) {
  const slices = deputies.map(([name, value]) => ({name, value}));

  return <section className="deputies-pie" aria-labelledby="deputies-pie-title">
    <div className="deputies-pie-heading">
      <h4 id="deputies-pie-title">Répartition par député</h4>
      <p>Nombre de déclarations liées à cette organisation, selon les filtres actifs.</p>
    </div>
    {total === 0 ? <p className="deputies-pie-empty">Aucune déclaration à afficher pour cette sélection.</p> :
      <div className="deputies-pie-layout">
        <div className="deputies-pie-chart" role="img" aria-label={`Répartition de ${total} déclarations entre ${deputies.length} députés. Les valeurs détaillées sont disponibles dans la liste.`}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={slices} dataKey="value" nameKey="name" innerRadius="58%" outerRadius="88%" stroke="#fff" strokeWidth={1}>
                {slices.map((slice, index) => <Cell key={slice.name} fill={colors[index % colors.length]} onClick={() => onDeputy(slice.name)} style={{cursor:'pointer'}} />)}
              </Pie>
              <Tooltip formatter={(value: number) => [`${value} déclaration${value > 1 ? 's' : ''}`, 'Déplacements déclarés']} />
            </PieChart>
          </ResponsiveContainer>
          <div className="deputies-pie-total" aria-hidden="true"><strong>{total}</strong><span>déclarations</span></div>
        </div>
        <div className="deputies-pie-legend" aria-label="Détail par député">
          {slices.map((slice, index) => <button type="button" key={slice.name} onClick={() => onDeputy(slice.name)} aria-label={`${slice.name} : ${slice.value} déclaration${slice.value > 1 ? 's' : ''}, ${(slice.value / total * 100).toLocaleString('fr-FR', {maximumFractionDigits: 1})} %`}>
            <span className="deputies-pie-swatch" style={{backgroundColor:colors[index % colors.length]}} aria-hidden="true" />
            <span className="deputies-pie-name">{slice.name}</span>
            <span className="deputies-pie-value">{slice.value}</span>
            <span className="deputies-pie-percent">{(slice.value / total * 100).toLocaleString('fr-FR', {maximumFractionDigits: 1})} %</span>
          </button>)}
        </div>
      </div>}
    <p className="deputies-pie-note">Une part correspond à une déclaration attribuée au député. L’organisation peut être simplement mentionnée : consultez les preuves dans le détail.</p>
  </section>;
}
