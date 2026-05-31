from anthropic import Anthropic

client = Anthropic()
message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hello"}]
)
if message.content and getattr(message.content[0], "type", None) == "text":
    print(getattr(message.content[0], "text", "No text found."))
else:
    print("No text response.")
