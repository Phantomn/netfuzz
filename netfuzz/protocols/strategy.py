from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def fuzz(self):
        pass
