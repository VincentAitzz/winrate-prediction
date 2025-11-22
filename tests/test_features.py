from app.services.features import selection_to_feature_vector


def test_selection_to_feature_vector_length():
    team = [1, 2, 3]
    enemy = [4, 5]
    vec = selection_to_feature_vector(team, enemy)
    assert vec.shape == (10,)


def test_selection_to_feature_vector_padding():
    team = [1]
    enemy = [2, 3, 4]
    vec = selection_to_feature_vector(team, enemy)
    # primeros valores: champ aliados (rellenos con 0)
    assert list(vec[:5]) == [1, 0, 0, 0, 0]
