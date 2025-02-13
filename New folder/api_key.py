import google.generativeai as genai

genai.configure(api_key="AIzaSyCGFuix5MqCBmJRE8oi1FzBYPjAt038dKc")
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Explain how AI works")
print(response.text)