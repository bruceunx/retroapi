## RetroSynthesis API

![test](https://github.com/bruceunx/retroapi/actions/workflows/python-app.yml/badge.svg)

- retroapi get predict routes given target molecule.

- supply plausible value for all predicts.

- predict conditions base on one reaction.

- add aync support

- deploy your backend server with **torchserve** (if api failed)

  > install torchserve and other libraries from requirements.txt
  > run download_models.sh
  > run

  ```bash
  torchserve --start --foreground --ncs --model-store=mars --models reaxys=reaxys.mar

  ```

  > test server

  ```bash

   curl http://127.0.0.1:8080/predictions/reaxys \                                                                                                            (base)
                --header "Content-Type: application/json" \
                --request POST \
                --data '{"smiles": ["CC(C)(C)OC(=O)N1CCC(OCCO)CC1"]}'
  ```

### Install

- using pip

```bash
pip install retroapi

```

### Usage

```python

from retroapi import RetroApi, Name2Smiles

token = "" # you may get token first

retro_api = RetroApi(token)

# if you have simles of molecule.
smiles = "COc1cccc(OC(=O)/C=C/c2cc(OC)c(OC)c(OC)c2)c1"

# else:
chemical_name = "4-Hydroxycoumarin"
name2smiles = Name2Smiles()
smiles = name2smiles.get_smiles(chemical_name)

# check if smiles is valid or not
is_valid_smiles = retro_api.validate_smiles(smiles)

if is_valid_smiles:
    routes = retro_api.predict_routes(smiles)
    if routes is not None:
        # work with routes
        pass

# check if chemical is buyable or not
is_buyable = retro_api.check_stock(smiles)

# check reaction conditions

# first you should get product smile
# second you should get reactants smile

products = "COc1cc(C(=O)O)cc(OC)c1OC"
reactants = "C=CC(=O)O.COc1cc(Br)cc(OC)c1OC"

conds = retro_api.process_reaction(product, reactants)
if conds is not None:
    # check reaction condition with plausible
    pass
```

### Async Usage

```python

from retroapi import RetroApi, Name2Smiles


async def foo():
    retro_api = RetroApi(token)

    # if you have simles of molecule.
    smiles = "COc1cccc(OC(=O)/C=C/c2cc(OC)c(OC)c(OC)c2)c1"

    # else:
    chemical_name = "4-Hydroxycoumarin"
    name2smiles = Name2Smiles()
    smiles = await name2smiles.aget_smiles(chemical_name)

    # check if smiles is valid or not
    is_valid_smiles = await retro_api.avalidate_smiles(smiles)

    if is_valid_smiles:
        routes = await retro_api.apredict_routes(smiles)
        if routes is not None:
            # work with routes
            pass

    # check if chemical is buyable or not
    is_buyable = await retro_api.acheck_stock(smiles)

    # check reaction conditions

    # first you should get product smile
    # second you should get reactants smile

    products = "COc1cc(C(=O)O)cc(OC)c1OC"
    reactants = "C=CC(=O)O.COc1cc(Br)cc(OC)c1OC"

    conds = await retro_api.aprocess_reaction(product, reactants)
    if conds is not None:
        # check reaction condition with plausible
        pass
```

## Change log:

### 2023-12-30 Extract condition recommend code from ASKCOS to notebook for local test.

### 2023-12-25 Run backend server with torchserve

### Add try_times in predict_routes and process_reaction w/ async

```python

routes = await retro_api.apredict_routes(smiles, try_num=20)

```

### **Need Token** to use this package

> It's wrap package for askcos.mit.edu API, so you can get token from website first.

### add aync for package

> with function name prefix with 'a', for example get_smile -> aget_smile

## API Documentation

### Class Name2Smiles

- get_smiles
  - parameter
    - chemical_name: str
  - output
    - smiles: str

### Class RetroApi

- validate_smiles

  - parameter
    - smiles: str
  - output
    - true/false

- predict_routes

  - parameter
    - smiles: str
  - output
    - routes: list

- process_reaction
  - parameter
    - product: str
      > product smiles
    - reactants: str
      > reactants smiles jointed by "." like "C=CC(=O)O.COc1cc(Br)cc(OC)c1OC"
  - output
    conditions: list
