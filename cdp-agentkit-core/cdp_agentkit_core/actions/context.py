import contextvars
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class Context():
    """Manages multiple context vars"""
    def __init__(self):
        self._vars: Dict[str, contextvars.ContextVar] = {}
    
    def create(self, key: str, default_value: any = None):
        """Create a new context var with given key name"""
        if key in self._vars:
            raise ValueError(f"{key} already exists")
        self._vars[key] = contextvars.ContextVar(f"{key}", default=default_value)
        
    def set(self, key: str, value: any):
        """Set value for a key"""
        if key not in self._vars:
            self.create(key)
        self._vars[key].set(value)
        
    def get(self, key: str) -> Optional[any]:
        """Get current value for a key"""
        if key not in self._vars:
            #  raise ValueError(f"{key} does not exist")
            return None
        return self._vars[key].get()
    
    def reset(self, key: str):
        """Reset to its default value"""
        if key not in self._vars:
            raise ValueError(f"{key} does not exist")
        self._vars[key].set(None)

    #  model_config = ConfigDict(arbitrary_types_allowed=True)
    #  cvars: ContextVar = ContextVar('context_store', default={})

    #  def __init__(self):
    #      super(Context, self).__init__()

    #      if not self.cvars.get():
    #          self.cvars.set({})

    #      self._tokens: dict[str, Any] = {}

    #  def create_var(self, name: str, default=None) -> None:
    #      store = self.cvars.get()

    #      if name not in store:
    #          store[name] = ContextVar(name, default=default)
    #          self.cvars.set(store)

    #  def get(self, name: str) -> Any:
    #      store = self.cvars.get()

    #      if name not in store:
    #          raise KeyError(f"Context variable '{name}' not found")

    #      return store[name].get()

    #  def set(self, name: str, value: Any) -> None:
    #      store = self.cvars.get()

    #      if name not in store:
    #          self.create_var(name)
    #          store = self.cvars.get()

    #      self._tokens[name] = store[name].set(value)

    #  def reset(self, name: str = None) -> None:
    #      if name is not None:
    #          if name in self._tokens:
    #              self._tokens[name].reset()
    #              del self._tokens[name]

    #      else:
    #          for token in self._tokens.values():
    #              token.reset()

    #          self._tokens.clear()
    #          self.cvars.set({})
