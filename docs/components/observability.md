# Observability Component

## 1. Philosophy / Purpose
Visibility and Tracing.

## 2. Architectural Layering
Cross-cutting concern.

## 3. How it Works (Under the hood)
Structlog with Correlation IDs via ContextVars.

## 4. Why it was designed this way
Async-safe logging.

## 5. Usage Guide & Code Examples
`get_logger("my_logger")`

## 6. Anti-Patterns
Standard python logging without context vars.

## 7. Pro-Tips / Best Practices
Always log correlation IDs.
