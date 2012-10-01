# -*- coding: utf-8 -*-
"""
This file contains classes for event handling and dispatching.

The comments in this file are written in the reStructured text format and adhere
to the commenting style used by epydoc.
"""

import logging
import sys

class EventDispatcher(object):
    """This is a simple event dispatcher class, that maintains a stack of handler
    lists.
    
    When dispatching an event each handler on the stack is examined from
    top to bottom whether their ``handles_types`` dictionary attribute has a key
    matching the dispatched event name. If so the value of the entry is called
    with the parameters given to the dispatch method. As soon as one of the 
    handlers returns ``True``, the traversal stops.
    """
    def __init__(self):
        """Initialize a new dispatcher object."""
        self._handlers_stack = []
        self._event_types = {}
        self._log = logging.getLogger('EventDispatcher')
    
    def handle_type(self, event_type):
        """Create a function that only dispatches events of the given type when 
        called. Use this to register callbacks with GLUT::
            
            dispatcher = EventDispatcher()
            glutKeyboardFunc(dispatcher.handle_type('keyboard'))
        
        :Parameters:
          event_type
            The type of the event the function should dispatch
        
        :return: a function that dispatches specific events if called
        """
        if self._event_types.has_key(event_type):
            return self._event_types[event_type]
        else:
            def _handle(*args, **kwargs):
                return self.dispatch(event_type, *args, **kwargs)
            self._event_types[event_type] = _handle
            return _handle
    
    def dispatch(self, event_type, *args, **kwargs):
        """Dispatch a single event of the given ``event_type``.
        
        :Parameters:
          event_type
            The type of the event to dispatch
        
        :return: ``True``, if any of the handlers returned ``True``, ``False``
          otherwise.
        """
        #self._log.debug(u"Dispatching event '%s' (%s, %s)...", event_type, str(args), str(kwargs))
        for handlers in self._handlers_stack:
            for handler in handlers:
                if getattr(handler, 'handles_types', {}).has_key(event_type):
                    handled = handler.handles_types[event_type](*args, **kwargs)
                    if handled:
                        return True
        return False
    
    def push_handlers(self, *handlers):
        """Pushes a new group of handlers onto the handler stack. The group can
        be popped off only as a whole.
        
        :Parameters:
          *handlers
            The handlers to push onto the stack
        """
        self._log.debug(u"Adding %u new handlers: %s", len(handlers), handlers)
        self._handlers_stack.insert(0, handlers)
    
    def pop_handlers(self):
        """Pops the topmost group of handlers off the handler stack.
        """
        handlers = self._handlers_stack.pop(0)
        self._log.debug(u"Removed %u handlers: %s", len(handlers), handlers)
