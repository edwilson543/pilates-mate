from pilates.application import generate_plan


def test_render():
    c = generate_plan.PilatesClass(
        warm_up="Warm", main_session="Main", cool_down="Cool"
    )

    rendered = c.render()

    print(rendered)
