# Pipes and Interceptors

## 1. Overview (What does this do?)
Pipes and Interceptors provide an abstraction layer for handling cross-cutting concerns during the request lifecycle. Specifically, Pipes are primarily used for formal payload validation (checking if the incoming DTO is well-formed), whereas Interceptors are used for Aspect-Oriented Programming (AOP) flows, such as measuring execution time, transforming responses, or handling localized exceptions.

## 2. Philosophy (Why does it exist?)
The philosophy behind this abstraction is separating business logic from validation and request/response manipulation. By injecting Pipes before the Controller layer, developers are guaranteed that their domain services will only ever receive valid, strongly-typed data. This reduces boilerplate validation code inside endpoints, leading to cleaner, more maintainable code. 

## 3. Target Audience (Who is it for?)
This component is designed for developers who are constructing APIs and need a robust, reusable way to sanitize inputs and manipulate responses uniformly across multiple endpoints without polluting the controller layer.

## 4. Architecture (How does it work?)
In the Ferrox-Py 7-Layer Onion Pipeline, Pipes sit at Layer 5 (Validation Pipe), immediately before the Controller. They intercept the incoming raw JSON/dictionary and parse it through a Pydantic schema. If validation fails, they automatically halt the pipeline and return a standardized 400 Bad Request error. Interceptors wrap the Controller execution, allowing code to run both immediately before the handler and right after it successfully returns data.

## 5. Installation / Setup
No separate installation is required. Pipes and Interceptors are available natively in the `ferrox_py.core` package, leveraging `pydantic` for schema definitions under the hood. Make sure your environment has Pydantic correctly installed.

## 6. Quickstart (Usage)
Applying a validation pipe to a specific controller route is straightforward:

```python
from ferrox_py.core.pipes import ValidationPipe
from pydantic import BaseModel

class CreateUserModel(BaseModel):
    email: str
    password: str

# In your controller setup:
# The pipe ensures `data` is a valid CreateUserModel before `create_user` runs.
@post("/users")
@use_pipe(ValidationPipe(CreateUserModel))
def create_user(data: CreateUserModel):
    return {"status": "success", "user": data.email}
```

## 7. Ecosystem Integration
Pipes integrate seamlessly with the CQRS component (Command Query Responsibility Segregation). When dispatching a Command to the CQRS bus, a Validation Pipe can ensure that the command object is structurally valid before it ever reaches the Command Handler layer.
