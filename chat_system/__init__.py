from otree.api import *
import time

from otree.models import Participant


class C(BaseConstants):
    NAME_IN_URL = 'chat_system'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# Store messages at participant level, not player level
class ChatMessage(ExtraModel):
    participant = models.Link(Participant)
    timestamp = models.FloatField()
    body = models.LongStringField()
    is_from_experimenter = models.BooleanField(initial=False)

    # Optional: mark if message has been read
    is_read = models.BooleanField(initial=False)


page_sequence = []