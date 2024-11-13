from contextvars import ContextVar
from typing import Dict, Any

from pydantic import BaseModel, Field, ConfigDict

class Context(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    cvars: ContextVar = ContextVar('context_store', default={})

    def __init__(self):
        super().__init__()

        if not self.cvars.get():
            self.cvars.set({})
        
        self._tokens: Dict[str, Any] = {}

    def create_var(self, name: str, default=None) -> None:
        store = self.cvars.get()

        if name not in store:
            store[name] = contextvars.ContextVar(name, default=default)
            self.cvars.set(store)

    def get(self, name: str) -> Any:
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
