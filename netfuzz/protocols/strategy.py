from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def define_proto(self, session):
        pass
    
    @abstractmethod
    def fuzz(self):
        pass
