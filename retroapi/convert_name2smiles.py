import requests

class Name2Smiles:

    URL = "https://opsin.ch.cam.ac.uk/opsin/{}"

    def __init__(self) -> None:
        pass

    def get_smiles(self, chemical_name: str) -> str | None:
        res = requests.get(self.URL.format(chemical_name))
        if res.status_code == 200:
            return res.json()['smiles']
        return None
