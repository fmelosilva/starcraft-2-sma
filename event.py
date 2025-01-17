from enum import Enum

class Event(object):
    """
    Not meant to be used by itself.
    Trigger event or Passive event should be used instead.
    """

    class TYPES(Enum):
        EMPTY = 0,
        TRIGGER = 1,
        CONSTANT = 2,
        NEW_UNIT = 3,
        REMOVED_UNIT = 4,
        UPGRADE = 5

    def __init__(self, on_event = None, get_status = None,
                 event_type: TYPES = TYPES.EMPTY, constant: bool = False, toggle: bool = False):
        self.__on_event = on_event
        self.__get_status = get_status
        self.event_type = event_type
        self.constant = constant
        self.toggle = toggle
        self.__has_toggled = False
        

    def trigger_event(self, bot, *args):
        """
        Call the on_event method associated with this event.
        :return:
        """
        if self.__on_event:
            self.__on_event(bot, *args)

    def should_trigger(self, bot):
        """
        Call the get_status method associated with this event.
        :return:
        """
        if self.__get_status:
            status = self.__get_status(bot)
            if status or (self.toggle and self.__has_toggled):
                self.__has_toggled = True
                return True
            return False
        return True

