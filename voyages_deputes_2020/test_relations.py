import json
import unittest
from pathlib import Path
from relations import matches, evidence

ROOT=Path(__file__).resolve().parent

class RelationsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'base_voyages.json').read_text(encoding='utf-8'))

    def test_alias_boundaries(self):
        self.assertFalse(matches('ELN - European Leadership Network',['ELNET']))
        self.assertFalse(matches('AFPCNT',['APF']))
        self.assertEqual(len(matches('Association EL.NET',['EL.NET'])),1)
        self.assertEqual(len(matches('Elnet France',['ELNET','ELNET France'])),1)

    def test_negation(self):
        text="prise en charge par l'Arménie mais pas par Rasmussen Global"
        start,end,alias=matches(text,['Rasmussen Global'])[0]
        p=evidence(text,start,end,alias,'financement.texte_declare')
        self.assertEqual(p['roles'],['financement_exclu'])

    def test_elnet_and_ambiguous_name(self):
        org=next(o for o in self.data['organisations'] if o['id']=='elnet')
        self.assertEqual(org['statistiques']['declarations'],60)
        self.assertEqual(org['statistiques']['deputes_distincts'],48)
        self.assertEqual(len(org['candidats_declaration_ids']),1)
        v=next(v for v in self.data['voyages'] if v['id']==org['candidats_declaration_ids'][0])
        self.assertEqual(v['financement']['texte_declare'],'ELN - European Leadership Network')
        self.assertNotIn(v['id'],org['declaration_ids'])

    def test_provenance_and_integrity(self):
        vs=self.data['voyages']
        self.assertEqual(len(vs),407)
        self.assertEqual(len({v['id'] for v in vs}),407)
        orgids={o['id'] for o in self.data['organisations']}
        for v in vs:
            self.assertEqual(v['financement']['texte_declare'],v['donnees_originales']['Tiers financeur'])
            self.assertEqual(v['descriptif'],v['donnees_originales']['Descriptif'])
            for rel in v['organisations']+v['organisations_a_verifier']:
                self.assertIn(rel['organisation_id'],orgids)
                for p in rel['preuves']:
                    text=v['financement']['texte_declare'] if p['champ']=='financement.texte_declare' else v['descriptif']
                    self.assertEqual(text[p['debut']:p['fin']],p['texte'])
                    self.assertIn(p['texte'],p['extrait'])
        for org in self.data['organisations']:
            linked=[v for v in vs if any(r['organisation_id']==org['id'] for r in v['organisations'])]
            self.assertEqual(set(org['declaration_ids']),{v['id'] for v in linked})
            self.assertEqual(org['statistiques']['declarations'],len(linked))

    def test_clusters_remain_hypotheses(self):
        for c in self.data['regroupements_possibles']:
            self.assertEqual(c['statut'],'hypothese')
            self.assertGreaterEqual(len(c['deputes']),2)
            for v in self.data['voyages']:
                if v['id'] in c['declaration_ids']:
                    self.assertEqual(v['periode']['debut'],c['date_depart'])
                    self.assertIn(c['pays'],v['destination']['pays_reperes'])
                    self.assertIn(c['id'],v['regroupements_possibles_ids'])

    def test_treaty_is_not_the_presidency(self):
        v=next(v for v in self.data['voyages'] if v['financement']['texte_declare']=='Fondation Otto de Habsburg')
        ids=[r['organisation_id'] for r in v['organisations']]
        self.assertNotIn('presidence-france',ids)
        self.assertIn('otto-habsburg',ids)

    def test_destinations_have_traceable_countries(self):
        v=next(v for v in self.data['voyages'] if v['destination']['texte']=='Cannes')
        self.assertIn('France',v['destination']['pays_reperes'])
        self.assertTrue(any(p['pays']=='France' and p['type']=='lieu_repertorie' for p in v['destination']['pays_preuves']))
        v=next(v for v in self.data['voyages'] if v['destination']['texte']=='Argentine et Chili')
        self.assertEqual(set(v['destination']['pays_reperes']),{'Argentine','Chili'})
        for v in self.data['voyages']:
            for p in v['destination']['pays_preuves']:
                self.assertIn(p['texte'],v['destination']['texte'])
                self.assertIn(p['pays'],v['destination']['pays_reperes'])

if __name__=='__main__': unittest.main()
