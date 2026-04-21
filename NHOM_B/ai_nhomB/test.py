import google.generativeai as genai
genai.configure(api_key="AIzaSyAYuL6ZPBOUikK0WU97ef3LRhTPXIQepxo") # Key của bạn
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)