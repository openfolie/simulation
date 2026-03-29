import agents


def test_relations():
    relations = agents.Relations()
    relations.connect(1, 2, "enemies", 69.0)
    res = relations.get_relation(1, "enemies")
    assert len(res) == 1
    assert res[0][0] == 2
    assert res[0][1] == {"weight": 69.0}
