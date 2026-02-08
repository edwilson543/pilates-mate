from pilates import _generation


def test_render():
    c = _generation.PilatesClass(warm_up="Warm", main_session="Main", cool_down="Cool")

    rendered = c.render()

    print(rendered)

