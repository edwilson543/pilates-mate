from pilates.domain.templates import _render


class TestRenderSystemPrompt:
    def test_renders_without_smoke(self):
        system_prompt = _render.render_system_prompt(
            exercises=[], example_lesson_plans=[]
        )

        assert system_prompt is not None
