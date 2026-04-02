from typing import Annotated, Sequence, TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from automation.tools import search_pubmed, check_schema_org, write_manuscript_section, search_you_engine, append_traceability_matrix

# 1. Define State Object
class GraphState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    reviewer_approved: bool

def create_model():
    return ChatOpenAI(model="gpt-4o", temperature=0.2)

def call_model(state: GraphState):
    model = create_model()
    # Bind all squad tools to the central model router
    tools = [search_pubmed, check_schema_org, write_manuscript_section, search_you_engine, append_traceability_matrix]
    model_with_tools = model.bind_tools(tools)
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def call_reviewer(state: GraphState):
    """Reviewer-2 Adversarial Checkpoint Node."""
    messages = state["messages"]
    last_message = messages[-1]

    # If the last message was a tool call, the Reviewer doesn't need to block it.
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return {"reviewer_approved": True}

    # Reviewer Persona Checkpoint
    model = create_model()
    reviewer_prompt = SystemMessage(content=(
        "You are Reviewer-2 (Adversarial Critic). You read the agent's final text output. "
        "If they use unscientific hype words (e.g. 'groundbreaking', 'revolutionary', 'game-changing'), OR if they fail to maintain a highly objective and neutral tone, "
        "you MUST reject it. Additionally, if the text does NOT include academic in-text citations (e.g. [1]) AND a formal 'Reference List' section at the bottom, "
        "you MUST reject it. To reject, reply starting exactly with 'REJECTED: ' and list the exact flaws prohibiting publication. "
        "If it is perfectly factual, objective, properly cited, and contains a reference list, reply exactly with 'APPROVED'."
    ))
    
    response = model.invoke([reviewer_prompt, HumanMessage(content=str(last_message.content))])
    
    if response.content.strip().startswith("APPROVED"):
        return {"reviewer_approved": True}
    else: # Rejection loops back to the agent through State Message appending
        return {"messages": [HumanMessage(content=f"Reviewer-2 Feedback: {response.content}")], "reviewer_approved": False}

# 3. Build StateMachine Graph
def build_graph():
    workflow = StateGraph(GraphState)
    
    # Define Nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("reviewer", call_reviewer)
    workflow.add_node("tools", ToolNode([search_pubmed, check_schema_org, write_manuscript_section, search_you_engine, append_traceability_matrix]))
    
    # Conditional routing logic after Agent
    def agent_router(state: GraphState):
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        return "reviewer"

    # Conditional routing logic after Reviewer
    def reviewer_router(state: GraphState):
        if state.get("reviewer_approved", False):
            return END
        return "agent" # Loops back to the drafting agent to fix the Reviewer's rejections

    # Wire Edges
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", agent_router, {"tools": "tools", "reviewer": "reviewer"})
    workflow.add_conditional_edges("reviewer", reviewer_router, {"agent": "agent", END: END})
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()
