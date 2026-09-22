# Ferrox-Py Quickstart

## 1. Overview (What does this do?)
This Quickstart guide provides the absolute fastest way to bootstrap a functional 7-layer pipeline application using the `ferrox-py` framework. It serves as a rapid deployment reference to help developers go from zero to a fully integrated application instance capable of accepting and processing requests safely.

## 2. Philosophy (Why does it exist?)
The goal of this guide is ease of use and immediate developer productivity. While Ferrox-Py is an enterprise-grade framework with many layers of complexity, developers need a pragmatic entry point to experiment with the framework's mechanics locally without getting bogged down in complex boilerplate. It exists to demonstrate that strict architecture doesn't have to mean slow setup.

## 3. Target Audience (Who is it for?)
This guide is for new developers onboarding onto a `ferrox-py` codebase, as well as seasoned architects setting up a new microservice from scratch. If you want to see the application core up and running in a few lines of code, this document is for you.

## 4. Architecture (How does it work?)
Under the hood, the Quickstart relies entirely on the `FerroxApp` class and the underlying Inversion of Control `Container`. By instantiating these two core objects, the framework automatically wires together the base ASGI container and prepares the 7-layer middleware pipeline, routing, and error-handling defaults.

## 5. Installation / Setup
No specialized setup is required beyond installing the library into a Python 3.11+ environment. It is strongly advised to configure your environment variables (e.g., in a `.env` file) to match the requirements of the database and security layers before running the app.

```bash
pip install ferrox-py
```

## 6. Quickstart (Usage)
The minimal viable code to start a Ferrox-Py server:

```python
from ferrox_py.core.app import FerroxApp
from ferrox_py.core.container import Container

def start_server():
    # 1. Initialize Dependency Container
    container = Container()
    
    # 2. Build the Application
    app = FerroxApp(container)
    
    # 3. Launch the Server
    app.start()

if __name__ == "__main__":
    start_server()
```

## 7. Ecosystem Integration
This quickstart setup is the foundational block for the entire ecosystem. Once `FerroxApp` is running, you can progressively plug in other modules such as the Task Scheduling architecture, Database adapters (like SQLAlchemy integrations), and comprehensive Observability hooks without altering this base initialization code.
