import streamlit as st
from backend import workflow
from langchain_core.messages import HumanMessage
import uuid


def generate_thread_id():
    return str(uuid.uuid4())


def add_thread(thread_id):
    if "chat_thread" not in st.session_state:
        st.session_state["chat_thread"] = []

    if thread_id not in st.session_state["chat_thread"]:
        st.session_state["chat_thread"].append(thread_id)


def reset_chat():
    st.session_state["thread_id"] = generate_thread_id()
    add_thread(st.session_state["thread_id"])
    st.session_state["message_history"] = []


def load_conversation(thread_id):
    state = workflow.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )
    return state.values.get("messages", [])


# ---------------- Session State ----------------

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_thread" not in st.session_state:
    st.session_state["chat_thread"] = []

add_thread(st.session_state["thread_id"])

# ---------------- Sidebar ----------------

st.sidebar.title("ChatBot")

st.sidebar.button("New Chat", on_click=reset_chat)

st.sidebar.header("My Conversation History")

for thread_id in st.session_state["chat_thread"]:

    messages = load_conversation(thread_id)

    title = "New Chat"

    for msg in messages:
        if isinstance(msg, HumanMessage):
            title = (
                msg.content[:20] + "..."
                if len(msg.content) > 20
                else msg.content
            )
            break

    if st.sidebar.button(title, key=thread_id):

        st.session_state["thread_id"] = thread_id

        temp_messages = []

        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"

            temp_messages.append(
                {
                    "role": role,
                    "content": msg.content,
                }
            )

        st.session_state["message_history"] = temp_messages

# ---------------- LangGraph Config ----------------

config = {
    "configurable": {
        "thread_id": st.session_state["thread_id"]
    }
}

# ---------------- Display Messages ----------------

for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- User Input ----------------

user_input = st.chat_input("Type here")

if user_input:

    st.session_state["message_history"].append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        placeholder = st.empty()
        full_response = ""

        for chunk in workflow.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="messages",
        ):

            if hasattr(chunk[0], "content") and chunk[0].content:
                full_response += chunk[0].content
                placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)

    st.session_state["message_history"].append(
        {
            "role": "assistant",
            "content": full_response,
        }
    )