from pilates.domain.lesson_planning import _generation
from testing.helpers import lesson_planning as lesson_planning_helpers


class TestRenderSystemPrompt:
    def test_renders_without_smoke(self):
        repo = lesson_planning_helpers.FakeRepository()

        system_prompt = _generation.render_system_prompt(repository=repo)

        assert system_prompt is not None
