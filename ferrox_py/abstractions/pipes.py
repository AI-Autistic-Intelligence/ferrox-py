from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ValidationError

from ferrox_py.core.errors import FerroxError


class PipeTransform(ABC):
    @abstractmethod
    def transform(self, value: Any, metadata: Any) -> Any:
        pass

class ValidationPipe(PipeTransform):
    def __init__(self, target_type: type[BaseModel]):
        self.target_type = target_type

    def transform(self, value: Any, metadata: Any = None) -> Any:
        try:
            if isinstance(value, dict):
                return self.target_type(**value)
            return self.target_type.model_validate(value)
        except ValidationError as e:
            raise FerroxError(message=f"Validation failed: {e.errors()}", status_code=400)
