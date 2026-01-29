from otree.api import *
import time

class ChatPage(Page):
    @staticmethod
    def live_method(player, data):
        from chat_system import ChatMessage
        participant = player.participant

        if data.get('type') == 'send_chat_message':
            ChatMessage.create(
                participant=participant,
                timestamp=time.time(),
                body=data['body'],
                is_from_experimenter=False,
                is_read=False
            )
            messages = ChatMessage.filter(participant=participant)
            return {
                player.id_in_group: [
                    {
                        'body': msg.body,
                        'timestamp': msg.timestamp,
                        'is_from_experimenter': msg.is_from_experimenter,
                        'is_read': msg.is_read
                    }
                    for msg in messages
                ]
            }

        if data.get('type') == 'get_chat_messages':
            messages = ChatMessage.filter(participant=participant)
            return {
                player.id_in_group: [
                    {
                        'body': msg.body,
                        'timestamp': msg.timestamp,
                        'is_from_experimenter': msg.is_from_experimenter,
                        'is_read': msg.is_read
                    }
                    for msg in messages
                ]
            }

        if data.get('type') == 'mark_messages_read':
            messages = ChatMessage.filter(
                participant=participant,
                is_from_experimenter=True,
                is_read=False
            )
            for msg in messages:
                msg.is_read = True
                msg.save()
            return {player.id_in_group: 'messages_marked_read'}