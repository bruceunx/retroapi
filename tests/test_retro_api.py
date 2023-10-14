from retroapi import RetroApi


def test_valid_smiles():
    api = RetroApi()
    smiles = "COc1cccc(OC(=O)/C=C/c2cc(OC)c(OC)c(OC)c2)c1"
    assert api.validate_smiles(smiles) is True
    smiles = "Cccccc1100(OC(=O)/C=C/c2cc(OC)c(OC)c(OC)c2)c1"
    assert api.validate_smiles(smiles) is False


def test_create_task():
    api = RetroApi()
    smiles = "COc1cccc(OC(=O)/C=C/c2cc(OC)c(OC)c(OC)c2)c1"
    task_id = api.create_task(smiles)
    assert type(task_id) == str
    routes = api.get_routes(task_id)
    if routes is not None:
        route = routes[0]
        assert 'plausibility' in route


def test_stock():
    api = RetroApi()
    smiles = "COc1cccc(OC(=O)/C=C/c2cc(OC)c(OC)c(OC)c2)c1"
    assert api.check_stock(smiles) is False
    smiles = "COc1cc(C=CC(=O)O)cc(OC)c1OC"
    assert api.check_stock(smiles) is True


def test_image():
    api = RetroApi()
    # reaction
    # smiles = "CC(=O)OC(C)=O.COc1cc(C=O)cc(OC)c1OC>>COc1cc(C=CC(=O)O)cc(OC)c1OC"
    smiles = "COc1cc(C=CC(=O)O)cc(OC)c1OC"  # reagent
    img_bytes = api.get_image_from_smiles(smiles)
    assert type(img_bytes) == bytes

def test_synthesis_task():
    api = RetroApi()
    products = "COc1cc(C(=O)O)cc(OC)c1OC"
    reactants = "C=CC(=O)O.COc1cc(Br)cc(OC)c1OC"
    syn_task = api.create_syn_task(products, reactants)
    assert type(syn_task) == str
    conditions = api.get_syn_conditions(syn_task)
    if conditions is not None:
        cond = conditions[0]
        assert "temperature" in cond
        assert "solvent" in cond

