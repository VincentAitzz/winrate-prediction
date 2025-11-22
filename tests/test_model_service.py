from app.services.model import WinrateModelService


def test_model_predict_range():
    service = WinrateModelService()
    winrate = service.predict_winrate(
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10],
    )
    assert 0.0 <= winrate <= 1.0
