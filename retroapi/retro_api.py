from typing import Any, List, Dict
import time
import asyncio
import aiohttp

import requests

RouteTaskData = {
    "retro_backend_options": [{
        "retro_backend": "template_relevance",
        "retro_model_name": "reaxys",
        "max_num_templates": 1000,
        "max_cum_prob": 0.999,
        "attribute_filter": []
    }],
    "banned_chemicals": [],
    "banned_reactions": [],
    "use_fast_filter":
    True,
    "fast_filter_threshold":
    0.001,
    "retro_rerank_backend":
    "relevance_heuristic",
    "cluster_precursors":
    False,
    "cluster_setting": {
        "feature": "original",
        "cluster_method": "hdbscan",
        "fp_type": "morgan",
        "fp_length": 512,
        "fp_radius": 1,
        "classification_threshold": 0.2
    },
    "extract_template":
    False,
    "return_reacting_atoms":
    True,
    "selectivity_check":
    True,
    "group_by_strategy":
    True
}


class RetroApi:

    Valid_URL = "https://askcos.mit.edu/api/rdkit/validate/"

    Task_URL = "https://askcos.mit.edu/api/tree-search/expand-one/call-async/"
    Route_URL = "https://askcos.mit.edu/api/legacy/celery/task/{}/"

    SynTask_URL = "https://askcos.mit.edu/api/legacy/context/"
    Cond_URL = "https://askcos.mit.edu/api/legacy/celery/task/{}/"

    Image_URL = "https://askcos.mit.edu/api/draw/?smiles={}"

    def __init__(self, token: str) -> None:
        self.headers = {"Authorization": token}

    def create_task(self, smiles: str) -> str | None:
        data: Dict[str, Any] = {
            "smiles": smiles,
        }
        data.update(RouteTaskData)
        res = requests.post(self.Task_URL, json=data, headers=self.headers)
        if res.status_code == 200:
            return res.json()
        else:
            return None

    async def acreate_task(self, smiles: str) -> str | None:
        data: Dict[str, Any] = {
            "smiles": smiles,
        }
        data.update(RouteTaskData)
        async with aiohttp.ClientSession(headers=self.headers) as client:
            res = await client.post(self.Task_URL, json=data)
            print(await res.json())
            if res.status == 200:
                res_data = await res.json()
                return res_data
        return None

    def get_routes(self, task_id: str) -> List | None:
        url = self.Route_URL.format(task_id)
        for _ in range(10):
            res = requests.get(url)
            if res.json()['complete']:
                break
            time.sleep(2)
        else:
            return None
        return res.json()["output"]["result"]['0']

    async def aget_routes(self, task_id: str) -> List | None:
        url = self.Route_URL.format(task_id)
        async with aiohttp.ClientSession() as client:
            for _ in range(10):
                res = await client.get(url)
                res_data = await res.json()
                if res_data['complete']:
                    return res_data["output"]["result"]['0']
                await asyncio.sleep(2)
        return None

    def predict_routes(self, smiles: str) -> List | None:
        task_id = self.create_task(smiles)
        if task_id is None:
            return None
        return self.get_routes(task_id)

    async def apredict_routes(self, smiles: str) -> List | None:
        task_id = await self.acreate_task(smiles)
        if task_id is None:
            return None
        return await self.aget_routes(task_id)

    def validate_smiles(self, smiles: str) -> bool:
        res = requests.post(self.Valid_URL, json={"smiles": smiles})
        if res.status_code == 200:
            return res.json()['valid_chem_name']
        return False

    async def avalidate_smiles(self, smiles: str) -> bool:
        async with aiohttp.ClientSession() as client:
            res = await client.post(self.Valid_URL, json={"smiles": smiles})
            if res.status == 200:
                res_data = await res.json()
                return res_data['valid_chem_name']
        return False

    def get_image_from_smiles(self, smiles: str) -> bytes | None:
        url = self.Image_URL.format(smiles)
        res = requests.get(url)
        if res.status_code == 200:
            return res.content
        return None

    async def aget_image_from_smiles(self, smiles: str) -> bytes | None:
        url = self.Image_URL.format(smiles)
        async with aiohttp.ClientSession() as client:
            res = await client.get(url)
            if res.status == 200:
                return await res.read()
        return None

    def create_syn_task(self, product: str, reactants: str) -> str | None:
        data = {
            "reactants": reactants,
            "products": product,
            "return_scores": True,
            "num_results": 10
        }
        res = requests.post(self.SynTask_URL, json=data, headers=self.headers)
        if res.status_code == 200:
            return res.json()["task_id"]
        return None

    async def acreate_syn_task(self, product: str, reactants: str) -> str | None:
        data = {
            "reactants": reactants,
            "products": product,
            "return_scores": True,
            "num_results": 10
        }
        async with aiohttp.ClientSession(headers=self.headers) as client:
            res = await client.post(self.SynTask_URL, json=data)
            if res.status == 200:
                res_data = await res.json()
                return res_data["task_id"]
        return None

    def get_syn_conditions(self, task_id: str) -> List | None:
        for _ in range(10):
            res = requests.get(self.Cond_URL.format(task_id))
            if res.json()['complete']:
                break
            time.sleep(2)
        else:
            return None
        return res.json()["output"]

    async def aget_syn_conditions(self, task_id: str) -> List | None:
        async with aiohttp.ClientSession() as client:
            for _ in range(10):
                res = await client.get(self.Cond_URL.format(task_id))
                res_data = await res.json()
                if res_data['complete']:
                    return res_data["output"]
                await asyncio.sleep(2)
        return None

    def process_reaction(self, product: str, reactants: str) -> List | None:
        task_id = self.create_syn_task(product, reactants)
        if task_id is None:
            return None
        return self.get_syn_conditions(task_id)

    async def aprocess_reaction(self, product: str, reactants: str) -> List | None:
        task_id = await self.acreate_syn_task(product, reactants)
        if task_id is None:
            return None
        return await self.aget_syn_conditions(task_id)
