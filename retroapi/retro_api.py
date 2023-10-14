from typing import List

import requests


class RetroApi:

    Valid_URL = "https://askcos.mit.edu/api/v2/rdkit/smiles/validate/"
    Task_URL = "https://askcos.mit.edu/api/v2/retro/"
    Route_URL = "https://askcos.mit.edu/api/v2/celery/task/{}/"
    Stock_URL = "https://askcos.mit.edu/api/v2/buyables/?q={}"

    ReactionTemplate_URL = "https://askcos.mit.edu/api/template/?id=5e1f4b6e63488328509969cc"
    Image_URL = "https://askcos.mit.edu/api/v2/draw/?smiles={}"

    SynTask_URL = "https://askcos.mit.edu/api/v2/context/"
    Cond_URL = "https://askcos.mit.edu/api/v2/celery/task/{}"

    def create_task(self, smiles: str) -> str | None:
        data = {
            "target": smiles,
            "template_set": "reaxys",
            "template_prioritizer_version": 1,
            "precursor_prioritizer": "RelevanceHeuristic",
            "num_templates": 1000,
            "max_cum_prob": 0.999,
            "filter_threshold": 0.1,
            "cluster_method": "kmeans",
            "cluster_feature": "original",
            "cluster_fp_type": "morgan",
            "cluster_fp_length": 512,
            "cluster_fp_radius": 1,
            "selec_check": True,
            "attribute_filter": []
        }
        res = requests.post(self.Task_URL, json=data)
        if res.status_code == 200:
            return res.json()['task_id']
        else:
            return None

    def get_routes(self, task_id: str) -> List | None:
        url = self.Route_URL.format(task_id)
        for _ in range(5):
            res = requests.get(url)
            if res.json()['complete']:
                break
        else:
            return None
        return res.json()["output"]

    def predict_routes(self, smiles: str) -> List | None:
        task_id = self.create_task(smiles)
        if task_id is None:
            return None
        return self.get_routes(task_id)

    def validate_smiles(self, smiles: str) -> bool:
        res = requests.post(self.Valid_URL, json={"smiles": smiles})
        if res.status_code == 200:
            return res.json()['valid_chem_name']
        return False

    def check_stock(self, smiles: str) -> bool:
        url = self.Stock_URL.format(smiles)
        res = requests.get(url)
        if res.status_code == 200:
            return len(res.json()["result"]) != 0
        return False

    def get_image_from_smiles(self, smiles: str) -> bytes | None:
        url = self.Image_URL.format(smiles)
        res = requests.get(url)
        if res.status_code == 200:
            return res.content
        return None

    def create_syn_task(self, product: str, reactants: str) -> str | None:
        data = {
            "reactants": reactants,
            "products": product,
            "return_scores": True,
            "num_results": 10
        }
        res = requests.post(self.SynTask_URL, json=data)
        if res.status_code == 200:
            return res.json()["task_id"]
        return None

    def get_syn_conditions(self, task_id: str) -> List | None:
        for _ in range(5):
            res = requests.get(self.Cond_URL.format(task_id))
            if res.json()['complete']:
                break
        else:
            return None
        return res.json()["output"]

    def process_reaction(self, product: str, reactants: str) -> List | None:
        task_id = self.create_syn_task(product, reactants)
        if task_id is None:
            return None
        return self.get_syn_conditions(task_id)
