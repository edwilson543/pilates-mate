from pilates.interfaces.cli._main import cli


def test_evaluate_prompt_help_text(cli_runner):
    result = cli_runner.invoke(cli, ["evaluate-prompt", "--help"])

    assert result.exit_code == 0
    assert "Evaluate system prompt template" in result.output
    assert "--version" in result.output
