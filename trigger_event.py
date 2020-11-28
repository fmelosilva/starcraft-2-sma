from event import Event
from typing import Callable

class TriggerEvent(Event):
    """
    Most commonly used when registering a Task.
    """
    def __init__(self, trigger, constant: bool = False, toggle: bool = False):
        Event.__init__(self, get_status=trigger, event_type=Event.TYPES.TRIGGER, constant=constant, toggle=toggle)

