# from cartesia import AsyncCartesia
# import os
# from dotenv import load_dotenv


# load_dotenv()

# async def translate_main(data: str):
#     client = AsyncCartesia(
#         api_key=os.getenv("CARTESIA_API_KEY")
#     )

#     try:
#         with open("sonic.wav", "wb") as f:
#             bytes_iter = client.tts.bytes(
#                 model_id="sonic-3",
#                 transcript=data,
#                 voice={
#                     "mode": "id",
#                     "id": "6ccbfb76-1fc6-48f7-b71d-91ac6298247b",
#                 },
#                 language="en",
#                 output_format={
#                     "container": "wav",
#                     "sample_rate": 44100,
#                     "encoding": "pcm_f32le",
#                 },
#             )

#             async for chunk in bytes_iter:
#                 f.write(chunk)

#     finally:
#         await client.close()
