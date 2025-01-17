from event import Event

class PassiveEvent(Event):
    """
    Most commonly used on the global event dictionary.
    @param event_type should be any Event.TYPES except TRIGGER.
    """
    def __init__(self, on_event, event_type: Event.TYPES, constant: bool = False, toggle: bool = False):
        Event.__init__(self, on_event=on_event, event_type=event_type, constant=constant, toggle=toggle)

