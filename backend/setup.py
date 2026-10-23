from setuptools import setup, find_packages

setup(
    name="todo-ai-chatbot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # Keep in sync with api/requirements.txt
        "fastapi==0.115.6",
        "uvicorn[standard]==0.34.0",
        "sqlmodel==0.0.22",
        "pydantic==2.10.4",
        "SQLAlchemy==2.0.45",
        "PyJWT==2.10.1",
        "psycopg2-binary==2.9.10",
    ],
)