from abc import ABC, abstractmethod

class ISpeechProvider(ABC):

    @abstractmethod
    def say(self, voice, text, filename, model):

        pass

