from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage,HumanMessage,BaseMessage
from langgraph.graph import StateGraph,START,END

from langgraph.graph.message import add_messages
from typing import TypedDict,Annotated
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
load_dotenv()
class ChatState(TypedDict):
  messages:Annotated[list[BaseMessage],add_messages]


model=ChatGroq(model="llama-3.1-8b-instant",streaming=True)
def ChatNode(state:ChatState):
 message=state['messages']

 response=model.invoke(message)

 return {"messages":response}


checkpointer=InMemorySaver()
graph=StateGraph(ChatState)
graph.add_node("ChatNode",ChatNode)
graph.add_edge(START,"ChatNode")
graph.add_edge("ChatNode",END)
workflow=graph.compile(checkpointer=checkpointer)

  