import chainlit as cl
# We import your existing logic from app.py
from app import get_answer 

@cl.on_chat_start
async def start():
    # This runs when you first open the webpage
    cl.user_session.set("top_k", 3)
    await cl.Message(content="🚀 Project RAG Demo is online. How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):
    # 1. Show a "loading" spinner while the AI thinks
    msg = cl.Message(content="")
    await msg.send()

    # 2. Get the settings we stored
    top_k = cl.user_session.get("top_k")

    # 3. Call your RAG logic (from app.py)
    # Note: If your get_answer isn't async, we run it in a thread to keep the UI responsive
    answer, sources = await cl.make_async(get_answer)(message.content, top_k)

    # 4. Format the sources into a nice list
    source_elements = [
        cl.Text(name=f"Source {i+1}", content=s, display="side") 
        for i, s in enumerate(sources)
    ]

    # 5. Update the message with the final answer and sources
    msg.content = answer
    msg.elements = source_elements
    await msg.update()