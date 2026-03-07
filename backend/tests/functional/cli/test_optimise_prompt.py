from pilates.interfaces.cli._main import cli


def test_optimise_prompt_help_text(cli_runner):
    """Test that optimise-prompt displays help text correctly."""
    result = cli_runner.invoke(cli, ["optimise-prompt", "--help"])

    assert result.exit_code == 0
    assert "Iteratively optimize system prompt" in result.output
    assert "--max-iterations" in result.output
    assert "--candidates-per-iteration" in result.output
    assert "--improvement-threshold" in result.output
    assert "--base-version" in result.output
