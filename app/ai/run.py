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
import json
import re

def extract_conversations(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split the file by the separators you used in the dump
    sessions = content.split("==================================================")
    
    with open(output_file, 'w', encoding='utf-8') as out:
        for session in sessions:
            if not session.strip():
                continue
            
            # Use regex to find the JSON block inside the dump
            json_match = re.search(r'\{.*\}', session, re.DOTALL)
            if not json_match:
                continue
                
            try:
                data = json.loads(json_match.group())
                
                # Extract Room and ID
                room_name = data.get("room", "Unknown")
                room_id = data.get("room_id", "Unknown")
                
                out.write(f"ROOM: {room_name} ({room_id})\n")
                out.write("-" * 30 + "\n")

                # Extract Messages from chat_history
                history = data.get("chat_history", {}).get("items", [])
                for item in history:
                    if item.get("type") == "message":
                        role = item.get("role", "unknown").upper()
                        # Content is a list, so join it
                        content_list = item.get("content", [])
                        message_text = " ".join(content_list)
                        
                        out.write(f"{role}: {message_text}\n")
                
                out.write("\n" + "="*50 + "\n\n")
                
            except json.JSONDecodeError:
                continue

    print(f"✅ Extracted summary saved to {output_file}")

if __name__ == "__main__":
    extract_conversations("response.txt", "conversation_summary.txt")
    