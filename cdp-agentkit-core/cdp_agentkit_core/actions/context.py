from contextvars import ContextVar

from typing import Any, Callable, Generic, Optional, TypeVar
from pydantic import BaseModel, Field, GetCoreSchemaHandler, ConfigDict
from pydantic.fields import FieldInfo
from pydantic_core import CoreSchema, core_schema



#  class Context():
#      """Manages multiple context vars"""
#      def __init__(self):
#          self._vars: Dict[str, contextvars.ContextVar] = {}
    
#      def create(self, key: str, default_value: any = None):
#          """Create a new context var with given key name"""
#          if key in self._vars:
#              raise ValueError(f"{key} already exists")
#          self._vars[key] = contextvars.ContextVar(f"{key}", default=default_value)
        
#      def set(self, key: str, value: any):
#          """Set value for a key"""
#          if key not in self._vars:
#              self.create(key)
#          self._vars[key].set(value)
        
#      def get(self, key: str) -> Optional[any]:
#          """Get current value for a key"""
#          if key not in self._vars:
#              #  raise ValueError(f"{key} does not exist")
#              return None
#          return self._vars[key].get()
    
#      def reset(self, key: str):
#          """Reset to its default value"""
#          if key not in self._vars:
#              raise ValueError(f"{key} does not exist")
#          self._vars[key].set(None)


#  T = TypeVar('T')

#  class ContextVarField(FieldInfo, Generic[T]):
#      def __init__(self, context_var: ContextVar[T], default: Optional[T] = None, **field_kwargs: Any):
#          super().__init__(**field_kwargs)
#          self.context_var = context_var
#          self.default = default

#      def __get__(self, instance, owner):
#          if instance is None:
#              return self
#          try:
#              return self.context_var.get()
#          except LookupError:
#              return self.default

#      def __set__(self, instance, value):
#          self.context_var.set(value)

#      def __repr__(self) -> str:
#          return f"ContextVarField(context_var={self.context_var!r}, default={self.default!r})"

#      def __get_pydantic_core_schema__(
#          cls,
#          source_type: Any,
#          handler: GetCoreSchemaHandler,
#      ) -> CoreSchema:
#          # Get the base schema for the type
#          schema = handler.generate_schema(source_type)
        
#          # Create a validator function that handles the ContextVar
#          def contextvar_validator(value: Any) -> Any:
#              if isinstance(value, ContextVar):
#                  try:
#                      return value.get()
#                  except LookupError:
#                      return None
#              return value

#          # Wrap the original schema with our custom validator
#          return core_schema.no_info_after_validator_function(
#              function=contextvar_validator,
#              schema=schema,
#          )

#  class ContextVarField(Field):
#      def __init__(self, var: ContextVar, **kwargs):
#          super().__init__(**kwargs)
#          self.var = var

#      def __get__(self, instance, owner):
#          if instance is None:
#              return self
#          return self.var.get()

#      def __set__(self, instance, value):
#          self.var.set(value)


#  def ContextVarField(context_var: ContextVar[T], **kwargs: Any) -> Any:
#      return Field(
#          default_factory=lambda: context_var.get() if context_var is not None else None,
#          **kwargs
#      )

class Context():
    class Config:
        arbitrary_types_allowed = True

    cvars: ContextVar[dict] = ContextVar('context_store', default={})
    #  cvars: dict = ContextVarField(..., description="internal cvars")

    def __init__(self):
        super(Context, self).__init__()

        if not self.cvars.get():
            self.cvars.set({})

        self._tokens: dict[str, Any] = {}

    def create_var(self, name: str, default=None) -> None:
        store = self.cvars.get()

        if name not in store:
            store[name] = ContextVar(name, default=default)
            self.cvars.set(store)

    def get(self, name: str) -> Optional[Any]:
        store = self.cvars.get()

        if name not in store:
            raise KeyError(f"Context variable '{name}' not found")

        return store[name].get()

    def set(self, name: str, value: Any) -> None:
        store = self.cvars.get()

        if name not in store:
            self.create_var(name)
            store = self.cvars.get()

        self._tokens[name] = store[name].set(value)

    def reset(self, name: str = None) -> None:
        if name is not None:
            if name in self._tokens:
                self._tokens[name].reset()
                del self._tokens[name]

        else:
            for token in self._tokens.values():
                token.reset()

            self._tokens.clear()
            self.cvars.set({})

