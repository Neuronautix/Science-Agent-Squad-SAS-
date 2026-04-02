import os
import typer
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

# Load LangGraph architecture
from automation.graph import build_graph

# Load environment configuration (.env)
load_dotenv()

app = typer.Typer()

@app.command()
def execute(prompt: str):
    """
    Kicks off the FAIR-NAMs-Squad LangGraph framework to process a robust request.
    Example: python automation/main.py "Ask Dr. Nexus to search PubMed for Virtual Control Groups and Scribe to write the findings."
    """
    if not os.getenv("OPENAI_API_KEY"):
        typer.secho("ERROR: 'OPENAI_API_KEY' is missing from environment variables.", fg=typer.colors.RED)
        typer.secho("Please add your key to a .env file at the root of the project to enable LangGraph.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)

    typer.secho(f"🚀 Initializing Squad Multi-Agent Graph...", fg=typer.colors.CYAN)
    graph = build_graph()

    # System persona dictates the capabilities and tools available
    system_persona = SystemMessage(
        content=(
            "You are the FAIR-NAMs-Squad, an orchestration of specialist scientific agents. "
            "You have tools to search PubMed, validate schema.org terminology, and write draft sections to disk. "
            "Use your tools to fulfill the user request precisely."
        )
    )
    user_request = HumanMessage(content=prompt)

    try:
        # Stream the graph updates
        typer.secho(f"\n🧠 [THINKING] Executing graph state...", fg=typer.colors.BLUE)
        for event in graph.stream({"messages": [system_persona, user_request]}, stream_mode="values"):
            latest_msg = event["messages"][-1]
            
            # Print Tool Invocations
            if hasattr(latest_msg, 'tool_calls') and latest_msg.tool_calls:
                for target_tool in latest_msg.tool_calls:
                    typer.secho(f"🔧 [TOOL INVOKED]: {target_tool['name']} -> {target_tool['args']}", fg=typer.colors.YELLOW)
            # Print Agent Output text
            elif hasattr(latest_msg, 'content') and latest_msg.content:
                # To prevent echoing the original user prompt again cleanly
                if isinstance(latest_msg, HumanMessage) or isinstance(latest_msg, SystemMessage):
                    continue
                typer.echo(f"\n🤖 [AGENT OUTPUT]:\n{latest_msg.content}\n")
                
        typer.secho("✅ Task Execution Complete.", fg=typer.colors.GREEN)
    
    except Exception as e:
        typer.secho(f"Execution Error: {e}", fg=typer.colors.RED)

if __name__ == "__main__":
    app()
