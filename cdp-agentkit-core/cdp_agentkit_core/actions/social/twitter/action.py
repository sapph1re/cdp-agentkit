import contextvars
import threading

from collections.abc import Callable
from pydantic import BaseModel


class Action(BaseModel):
    """Twitter Action Base Class."""

    name: str
    description: str
    args_schema: type[BaseModel] | None = None
    func: Callable[..., str]


class ActionThread(threading.Thread):
    fn: Callable | None
    running: bool
    stopped_event: threading.Event | None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ctx = contextvars.copy_context()
        self.daemon = True
        self.running = False

    def set_fn(fn: Callable):
        self.fn = fn

    def run(self):
        if self.running:
            return

        for var, value in self.ctx.items():
            var.set(value)

        if self.fn is None:
            return

        self.fn()

    def stop(self) -> threading.Event | None:
        if self.running is False:
            return None

        self.stopped_event = threading.Event()

        return self.stopped_event

    def stopped(self):
        if self.stopped_event is not None:
            self.stopped_event.set()

        self.running = False

        #  def execute(fn):
        #      def decorator(cls):
        #          def wrapper(self, *args, **kwargs):
        #              cls.__init__(self, *args, **kwargs)

        #              self.fn = fn

        #          cls.__init__ == wrapper
        #          return cls

        #      return decorator
