# %%
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import END, MessageGraph

from dotenv import load_dotenv
load_dotenv()

# %%
import os

llm = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0
)

# %%
def entry(input: list[HumanMessage]):
    return  input

def action(input: list[HumanMessage]):
    print(f"Action taken: {[msg.content for msg in input]}")
    if len(input) > 5:
        input.append(HumanMessage(content="end"))
    else:
        input.append(HumanMessage(content="continue"))
    return input

def should_continue(input: list[HumanMessage]):
    last_msg = input[-1]
    if "end" in last_msg.content:
        return "__end__"
    return "action"

graph = MessageGraph()
graph.add_node("agent", entry)
graph.add_node("action", action)
graph.add_conditional_edges("agent", should_continue, {"action": "action", "__end__": END})
graph.set_entry_point("agent")
graph.add_edge("action", "agent")

app = graph.compile()
result = app.invoke("Some Msg")

# %%
for msg in result:
    msg.pretty_print()
