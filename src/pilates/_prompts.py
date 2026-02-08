import jinja2
import pathlib


def render_system_prompt() -> str:
    prompts_dir = pathlib.Path(__file__).parent / "prompts"

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(prompts_dir),
        autoescape=jinja2.select_autoescape()
    )
    template = env.get_template("system.jinja")
    return template.render()


if __name__ == "__main__":
    print(render_system_prompt())
