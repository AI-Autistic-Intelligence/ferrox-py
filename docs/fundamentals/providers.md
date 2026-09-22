# Fundamentals: Providers
## 1. Philosophy / Purpose
Inversion of Control.

## 2. Usage Guide & Code Examples
```python
@injectable(scope=ProviderScope.SINGLETON)
class MyService:
    pass
```
