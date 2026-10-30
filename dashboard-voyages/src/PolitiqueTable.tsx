import {useMemo,useState} from 'react';
import {ArrowUpRight} from 'lucide-react';
import {data,orgMap,type Voyage,type Affiliation} from './data';
import './politique.css';

export type ModePolitique = 'parti' | 'groupe';
export const INCONNU = '__inconnu__';
export function nomPolitique(affiliation:Affiliation,regroupe:boolean):string {
  if(affiliation.statut!=='identifie'||!affiliation.nom)return INCONNU;
  return regroupe ? affiliation.regroupement?.nom || affiliation.nom : affiliation.nom;
}
type Pair = {politique:string;organisation:string;nomOrganisation:string;declarations:number;deputes:Set<string>};

export function PolitiqueTable({voyages,onSelect}:{voyages:Voyage[];onSelect:(mode:ModePolitique,politique:string,organisation:string,regroupe:boolean)=>void}) {
  const [mode,setMode]=useState<ModePolitique>('parti');
  const [regroupe,setRegroupe]=useState(true);
  const [parti,setParti]=useState('all');
  const [organisation,setOrganisation]=useState('all');
  const [page,setPage]=useState(1);
  const pairs=useMemo(()=>{
    const map=new Map<string,Pair>();
    for(const voyage of voyages){
      const politique=nomPolitique(voyage.politique[mode],regroupe);
      const ids=new Set(voyage.organisations.filter(r=>r.roles.includes('cite_dans_financement') && orgMap.has(r.organisation_id)).map(r=>r.organisation_id));
      for(const id of ids){
        const key=JSON.stringify([politique,id]);
        const pair=map.get(key) || {politique,organisation:id,nomOrganisation:orgMap.get(id)!.nom,declarations:0,deputes:new Set<string>()};
        pair.declarations++;pair.deputes.add(voyage.depute.nom_complet);map.set(key,pair);
      }
    }
    return [...map.values()].sort((a,b)=>b.declarations-a.declarations || a.nomOrganisation.localeCompare(b.nomOrganisation,'fr') || a.politique.localeCompare(b.politique,'fr'));
  },[voyages,mode,regroupe]);
  const partis=[...new Set(pairs.map(x=>x.politique))].sort((a,b)=>a.localeCompare(b,'fr'));
  const orgs=[...new Map(pairs.map(x=>[x.organisation,x.nomOrganisation])).entries()].sort((a,b)=>a[1].localeCompare(b[1],'fr'));
  const filtered=pairs.filter(x=>(parti==='all'||x.politique===parti)&&(organisation==='all'||x.organisation===organisation));
  const pages=Math.max(1,Math.ceil(filtered.length/10));const current=Math.min(page,pages);const rows=filtered.slice((current-1)*10,current*10);
  const unknown=voyages.filter(v=>v.politique[mode].statut!=='identifie').length;
  const politiqueLabel=(value:string)=>value===INCONNU?'Non renseigné':value;
  return <section className="card politique-card" id="politique" aria-labelledby="politique-title">
    <span className="section-kicker">CROISEMENT · DÉCLARATIONS</span><h3 id="politique-title">Partis et organisations</h3>
    <p className="politique-intro">Organisations citées dans le champ « tiers financeur », regroupées selon le rattachement politique du député à la date du départ.</p>
    <div className="politique-controls">
      <label>Lecture<select value={mode} onChange={e=>{setMode(e.target.value as ModePolitique);setParti('all');setOrganisation('all');setPage(1)}}><option value="parti">Parti : rattachement financier</option><option value="groupe">Groupe parlementaire</option></select></label>
      <label>Libellés<select value={regroupe?'regroupes':'historiques'} onChange={e=>{setRegroupe(e.target.value==='regroupes');setParti('all');setOrganisation('all');setPage(1)}}><option value="regroupes">Regroupés</option><option value="historiques">Historiques</option></select></label>
      <label>{mode==='parti'?'Parti ou groupement':'Groupe parlementaire'}<select value={parti} onChange={e=>{setParti(e.target.value);setPage(1)}}><option value="all">Tous</option>{partis.map(p=><option value={p} key={p}>{politiqueLabel(p)}</option>)}</select></label>
      <label>Organisation<select value={organisation} onChange={e=>{setOrganisation(e.target.value);setPage(1)}}><option value="all">Toutes</option>{orgs.map(([id,name])=><option value={id} key={id}>{name}</option>)}</select></label>
    </div>
    <p className="politique-info">{mode==='parti'?'Le parti correspond au rattachement déclaré pour le financement de la vie politique, qui ne prouve pas une adhésion.':'Le groupe parlementaire est distinct du parti.'} {unknown} déclaration{unknown>1?'s':''} sans {mode==='parti'?'rattachement':'groupe'} identifié dans la sélection. {regroupe?'Certains libellés historiques sont rapprochés selon les règles ci-dessous.':'Les libellés historiques sont affichés séparément.'}</p>
    <details className="politique-groupings"><summary>Voir les regroupements et leurs sources</summary><p>Ces catégories facilitent la comparaison entre périodes ; elles ne déclarent pas que toutes les structures ou leurs membres sont identiques.</p>{data.metadonnees.politique.regroupements[mode].map(group=><div className="politique-grouping" key={group.id}><strong>{group.nom}</strong><p>{group.libelles.join(' · ')}</p><p>{group.note}</p><p>{group.sources.map((url,i)=><a key={url} href={url} target="_blank" rel="noreferrer">Source {i+1} ↗ </a>)}</p></div>)}</details>
    <div className="politique-scroll"><table><thead><tr><th>{mode==='parti'?'PARTI OU GROUPEMENT':'GROUPE PARLEMENTAIRE'}</th><th>ORGANISATION CITÉE</th><th>DÉCLARATIONS</th><th>DÉPUTÉS</th><th></th></tr></thead><tbody>{rows.map(row=><tr key={JSON.stringify([row.politique,row.organisation])}><td><strong>{politiqueLabel(row.politique)}</strong></td><td>{row.nomOrganisation}</td><td>{row.declarations}</td><td>{row.deputes.size}</td><td><button type="button" className="politique-view" onClick={()=>onSelect(mode,row.politique,row.organisation,regroupe)} aria-label={`Voir les déclarations : ${politiqueLabel(row.politique)}, ${row.nomOrganisation}`}>Voir <ArrowUpRight size={14}/></button></td></tr>)}</tbody></table>{!rows.length&&<p className="empty">Aucun rapprochement pour cette sélection.</p>}</div>
    <div className="pagination politique-pagination"><span>{filtered.length} combinaison{filtered.length>1?'s':''} · une déclaration peut citer plusieurs organisations</span><div><button disabled={current===1} onClick={()=>setPage(current-1)} aria-label="Combinaisons précédentes">‹</button><span>Page {current} / {pages}</span><button disabled={current===pages} onClick={()=>setPage(current+1)} aria-label="Combinaisons suivantes">›</button></div></div>
    <p className="politique-source">Rapprochements établis à partir des <a href="https://data.assemblee-nationale.fr/acteurs/historique-des-deputes" target="_blank" rel="noreferrer">données historiques de l’Assemblée nationale</a>. Une organisation citée ne finance pas nécessairement la totalité du voyage.</p>
  </section>
}
