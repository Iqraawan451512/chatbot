from setuptools import setup, find_packages

setup(
    name="todo-ai-chatbot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "openai==1.3.5",
        "pydantic==2.5.0",
        "sqlmodel==0.0.16",
        "asyncpg==0.29.0",
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0",
    ],
)