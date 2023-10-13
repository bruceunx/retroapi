from convert_name_2_smiles import Name2Smiles


def test_name_2_smiles():
    name2smiles = Name2Smiles()
    chemical_name = "2,4,6-trinitrotoluene"
    smiles = name2smiles.get_smiles(chemical_name)
    assert smiles is not None
    assert smiles == "[N+](=O)([O-])C1=C(C)C(=CC(=C1)[N+](=O)[O-])[N+](=O)[O-]"
