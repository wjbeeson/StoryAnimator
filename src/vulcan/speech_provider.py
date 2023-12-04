from abc import ABC, abstractmethod

class ISpeechProvider(ABC):

    @abstractmethod
    def say(self, voice, text, filename, rate=1.0):

        pass


    @abstractmethod
    def say_ssml(self, voice, ssml, filename, rate=1.0):
        pass


