# import asyncio
# from agent import app
# from voice_agent import translate_main

# async def main():
#     initial_state = {
#         "role": "Python Developer",
#         "level": "Senior",
#         "question_count": 0,
#         "chat_history": [],
#         "is_complete": False
#     }

#     final_state = await app.ainvoke(initial_state)

#     history = final_state["chat_history"]

#     # Convert history → speech text
#     if isinstance(history, list):
#         text = "\n".join(
#             msg["content"] if isinstance(msg, dict) else str(msg)
#             for msg in history
#         )
#     else:
#         text = str(history)

#     await translate_main(text)

#     print(f"Final Score & Feedback: {text}")



# if __name__ == "__main__":
#     asyncio.run(main())