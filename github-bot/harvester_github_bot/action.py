import abc

class ActionRequest:
    def __init__(self):
        pass
    def setAction(self, action):
        self.action = action


class Action(abc.ABC):
    # isMatched returns True if the actionRequest is matched with the action from github webook
    @abc.abstractmethod
    def isMatched(self, actionRequest):
        raise NotImplementedError
    
    @abc.abstractmethod
    def action(self, request):
        raise NotImplementedError

class LabelAction(abc.ABC):
    # isMatched returns True if it meets the condition to execute the action
    @abc.abstractmethod
    def isMatched(self, request):
        raise NotImplementedError
    
    @abc.abstractmethod
    def action(self, request):
        raise NotImplementedError