# %%
from langchain_core.messages import HumanMessage
from langgraph.graph import END, MessageGraph

def entry(input: list[HumanMessage]):
    return input

def work_with_b(input: list[HumanMessage]):
    print("Using branch b")
    return input

def work_with_c(input: list[HumanMessage]):
    print("Using branch c")
    return input

def router(input: list[HumanMessage]):
    if "use_b" in input[0].content:
        return "branch_b"
    else:
        return "branch_c"

graph = MessageGraph()

graph.add_node("branch_a", entry)
graph.add_node("branch_b", work_with_b)
graph.add_node("branch_c", work_with_c)

graph.add_conditional_edges("branch_a", router, {"branch_b": "branch_b", "branch_c":"branch_c"})

graph.set_entry_point("branch_a")
graph.add_edge("branch_b", END)
graph.add_edge("branch_c", END)

runnable = graph.compile()

runnable.invoke("I want to use b")