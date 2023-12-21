from abc import ABC, abstractmethod

class ISpeechProvider(ABC):

    @abstractmethod
    def say(self, voice, text, filename, rate=1.0, pitch=-7):

        pass

