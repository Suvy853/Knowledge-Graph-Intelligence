import os
from dotenv import load_dotenv

load_dotenv()

print(f"NEO4J_URI: {os.getenv('NEO4J_URI')}")
print(f"NEO4J_USERNAME: {os.getenv('NEO4J_USERNAME')}")
print(f"NEO4J_USER: {os.getenv('NEO4J_USER')}")
print(f"NEO4J_PASSWORD: {os.getenv('NEO4J_PASSWORD')}")
print(f"NEO4J_DATABASE: {os.getenv('NEO4J_DATABASE')}")