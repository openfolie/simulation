from environment.walkablity import FlatPlain, RugidSurface


def test_flatplain():
    surface = FlatPlain(1)
    for row in surface.slopes:
        for item in row:
            assert item == 1
    for row in surface.diffs:
        for item in row:
            assert item == 0


def test_rugid():
    surface = RugidSurface(0, -4, 4, 2)
    for row in surface.slopes:
        for item in row:
            assert -4 <= item <= 4
