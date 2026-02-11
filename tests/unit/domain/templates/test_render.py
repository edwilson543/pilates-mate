from pilates.domain.templates import _render


class TestRenderSystemPrompt:
    def test_renders_without_smoke(self):
        system_prompt = _render.render_system_prompt()

        assert system_prompt is not None
