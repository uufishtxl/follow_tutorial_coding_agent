# %%
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv() 
llm = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0)


# %%
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    api_call_count: int = 0

# %%
from langchain_core.tools import tool
import random

@tool
def fake_weather_api(city: str) -> str:
    """Check the weather in a specified city. The API is available randomly, approximately every third call"""
    if random.randint(1, 3) == 1:
        return "Sunny, 22℃"
    else:
        return "Service temporarily unavailable"
# %%
from langchain_core.messages import HumanMessage, ToolMessage

llm_with_tools = llm.bind_tools([fake_weather_api])

tool_mapping = {"fake_weather_api": fake_weather_api}

messages = [
    HumanMessage(content="How will the weather be in munich today? I would like to eat outside if possible")
]

# llm_output = llm_with_tools.invoke(messages)
# messages.append(llm_output)

# for tool_call in llm_output.tool_calls:
#     tool = tool_mapping[tool_call["name"].lower()]
#     tool_output = tool.invoke(tool_call["args"])
#     messages.append(ToolMessage(content=tool_output, tool_call_id=tool_call["id"]))

# output_after_tool_implementation = llm_with_tools.invoke(messages)

# print(output_after_tool_implementation)

# %%
def should_continue(state: AgentState):
    # print(f"STATE: {state}")
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "__end__"
    return "continue"

def call_model(state: AgentState):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response], "api_call_count": state["api_call_count"]}

def call_tool(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    tool_call = last_message.tool_calls[0]
    tool = tool_mapping[tool_call["name"].lower()]
    output = tool.invoke(tool_call["args"])
    state["api_call_count"] += 1
    tool_message = ToolMessage(content=output, tool_call_id=tool_call["id"])
    return {"messages": [tool_message], "api_call_count": state["api_call_count"]}

# %%
from langgraph.graph import END, StateGraph
graph = StateGraph(AgentState)

graph.add_node("agent", call_model)
graph.add_node("action", call_tool)
graph.set_entry_point("agent")

graph.add_edge("action", "agent")
graph.add_conditional_edges("agent", should_continue, {"__end__": END, "continue": "action"})

app = graph.compile()

# %%
from langchain_core.messages import SystemMessage

system_message = SystemMessage(
    content="You are responsible for answering user questions. You use tools for that, These tools sometimes fail and you are very resilient and trying them again"
)
human_message = HumanMessage(content="How is the weather in munich today?")
messages = [system_message, human_message]

config = {"configurable": {"thread_id": '410'}}

result = app.invoke({"messages": messages, "api_call_count": 0}, config=config)

print("result: ", result)