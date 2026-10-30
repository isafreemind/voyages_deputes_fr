import {existsSync, readFileSync, writeFileSync} from 'node:fs';
const canonical=new URL('../../voyages_deputes_2020/base_voyages.json',import.meta.url);
const bundled=new URL('../src/base_voyages.json',import.meta.url);
const download=new URL('../public/base_voyages.json',import.meta.url);
const text=readFileSync(existsSync(canonical)?canonical:bundled,'utf8');
const data=JSON.parse(text);
if(data.metadonnees.schema_version!==2||!Array.isArray(data.organisations)) throw new Error('Base enrichie v2 attendue');
writeFileSync(bundled,text);writeFileSync(download,text);
console.log(`${data.voyages.length} déclarations, ${data.organisations.length} organisations synchronisées.`);
