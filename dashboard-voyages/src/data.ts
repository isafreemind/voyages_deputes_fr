import raw from './base_voyages.json';
export interface Proof {champ:string;debut:number;fin:number;texte:string;alias:string;extrait:string;roles:string[]}
export interface Relation {organisation_id:string;statut:string;roles:string[];preuves:Proof[]}
export interface Candidate {organisation_id:string;statut:string;raison:string;preuves:Proof[]}
export interface Affiliation {statut:string;id?:string;nom?:string;sigle?:string;regroupement?:{id:string;nom:string};mandats?:{id:string;debut:string;fin:string|null;qualite:string}[]}
export interface Voyage {
 id:string;depute:{nom_complet:string;nom:string|null;prenom:string|null};legislature:number;
 declaration:{date:string|null};destination:{texte:string;pays_reperes:string[];pays_preuves:{pays:string;texte:string;type:string;alias:string}[]};
 periode:{debut:string|null;fin:string|null;duree_jours:number|null;duree_texte:string};
 financement:{texte_declare:string;montants_mentionnes:{texte:string;contexte:string}[]};
 descriptif:string;tags:{tag:string}[];source_url:string;
 organisations:Relation[];organisations_a_verifier:Candidate[];regroupements_possibles_ids:string[];
 politique:{date_reference:string|null;acteur_id:string|null;source_url:string|null;parti:Affiliation;groupe:Affiliation};
}
export interface Organisation {id:string;nom:string;alias:string[];alias_ambigus?:string[];note?:string;alias_observes:string[];declaration_ids:string[];candidats_declaration_ids:string[];statistiques:{declarations:number;deputes_distincts:number;citations_champ_financement:number}}
export interface Cluster {id:string;organisation_id:string;date_depart:string;pays:string;statut:string;critere:string;declaration_ids:string[];deputes:string[];dates_retour:string[]}
interface PoliticalGrouping {id:string;nom:string;organes:string[];libelles:string[];note:string;sources:string[]}
interface Base {voyages:Voyage[];organisations:Organisation[];regroupements_possibles:Cluster[];metadonnees:{politique:{regroupements:{methode:string;parti:PoliticalGrouping[];groupe:PoliticalGrouping[]}};relations:{roles:Record<string,string>;couverture:{organisations:number;declarations_avec_organisation:number;declarations_sans_organisation_reconnue:number;declarations_avec_candidat_ambigu:number}}}}
export const data=raw as unknown as Base;
export const orgMap=new Map(data.organisations.map(o=>[o.id,o]));
export const roleNames:Record<string,string>={cite_dans_financement:'Cité au financement',mention:'Simple mention',prise_en_charge_mentionnee:'Prise en charge mentionnée',organisateur_mentionne:'Organisateur mentionné',invitant_mentionne:'Invitant mentionné',partenaire_mentionne:'Partenaire mentionné',financement_exclu:'Financement explicitement exclu'};
