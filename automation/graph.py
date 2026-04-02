from typing import Annotated, Sequence, TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from automation.tools import search_pubmed, check_schema_org, write_manuscript_section, search_you_engine

# 1. Define State Object
class GraphState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def create_model():
    return ChatOpenAI(model="gpt-4o", temperature=0.2)

def call_model(state: GraphState):
    model = create_model()
    # Bind all squad tools to the central model router
    tools = [search_pubmed, check_schema_org, write_manuscript_section, search_you_engine]
    model_with_tools = model.bind_tools(tools)
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# 3. Build StateMachine Graph
def build_graph():
    workflow = StateGraph(GraphState)
    
    # Standard React tool-calling loop structure
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode([search_pubmed, check_schema_org, write_manuscript_section, search_you_engine]))
    
    # Conditional routing logic
    def should_continue(state: GraphState):
        messages = state["messages"]
        last_message = messages[-1]
        
        # If the LLM generates tool calls, route to the tools node
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        # Otherwise, the execution is finished
        return END

    # Wire Edges
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()
