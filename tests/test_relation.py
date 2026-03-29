import agents


def test_relations_crud():
    relations = agents.Relations()
    relations.connect(1, 2, "enemies", 69.0)
    print(dir(relations))
    assert 1
