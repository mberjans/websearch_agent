import typer
from search_agent.answer_orchestrator import app as answer_app

app = typer.Typer()
app.add_typer(answer_app, name="answer")

if __name__ == "__main__":
    app()