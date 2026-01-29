"""
Experimenter Dashboard App - Fully Fixed
Proper imports for Participant and ExtraModel queries
"""

from otree.api import *
import time

class C(BaseConstants):
    NAME_IN_URL = 'experimenter_dashboard'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    pass

class Dashboard(Page):
    """
    Main dashboard page for experimenter to monitor all participant chats
    """

    @staticmethod
    def live_method(player: Player, data):
        """
        Handle live messages from the dashboard
        """
        from chat_system import ChatMessage
        from otree.models import Participant as ParticipantModel

        data_type = data.get('type')

        # Send a message to a specific participant
        if data_type == 'send_message':
            try:
                participant_id = data.get('participant_id')
                body = data.get('body', '').strip()

                if not participant_id or not body:
                    return {player.id_in_group: {'error': 'Missing participant_id or body'}}

                # Get the participant
                participant = ParticipantModel.objects_get(id=participant_id)

                # Create the message
                ChatMessage.create(
                    participant=participant,
                    timestamp=time.time(),
                    body=body,
                    is_from_experimenter=True,
                    is_read=False
                )

                return {0: 'update_chat'}

            except Exception as e:
                print(f"Error sending message: {e}")
                import traceback
                traceback.print_exc()
                return {player.id_in_group: {'error': str(e)}}

        # Get all chats for all participants
        elif data_type == 'get_all_chats':
            try:
                # Get all messages from DB
                all_messages = ChatMessage.filter()

                # Group messages by participant_id to optimize lookup
                messages_by_participant = {}
                for msg in all_messages:
                    p_id = msg.participant_id
                    if p_id not in messages_by_participant:
                        messages_by_participant[p_id] = []
                    messages_by_participant[p_id].append(msg)

                chats = {}

                for p_id, messages in messages_by_participant.items():
                    try:
                        participant = ParticipantModel.objects_get(id=p_id)
                    except:
                        continue

                    # Sort messages by timestamp
                    messages.sort(key=lambda m: m.timestamp)

                    # Count unread messages from participants
                    unread_count = sum(
                        1 for msg in messages
                        if not msg.is_from_experimenter and not msg.is_read
                    )

                    # Get session info
                    try:
                        session_code = participant.session.code if participant.session else 'Unknown'
                    except:
                        session_code = 'Unknown'

                    chats[participant.id] = {
                        'participant_code': participant.code,
                        'participant_label': participant.label or f"P{participant.id}",
                        'session_code': session_code,
                        'unread_count': unread_count,
                        'messages': [
                            {
                                'body': msg.body,
                                'timestamp': msg.timestamp,
                                'is_from_experimenter': msg.is_from_experimenter,
                                'is_read': msg.is_read
                            }
                            for msg in messages
                        ]
                    }

                return {player.id_in_group: chats}

            except Exception as e:
                print(f"Error getting all chats: {e}")
                import traceback
                traceback.print_exc()
                return {player.id_in_group: {'error': str(e)}}

        # Mark messages as read
        elif data_type == 'mark_participant_read':
            try:
                participant_id = data.get('participant_id')

                if not participant_id:
                    return {player.id_in_group: {'error': 'Missing participant_id'}}

                participant = ParticipantModel.objects_get(id=participant_id)

                # Mark all unread messages from this participant as read
                messages = ChatMessage.filter(
                    participant=participant,
                    is_from_experimenter=False,
                    is_read=False
                )

                for msg in messages:
                    msg.is_read = True
                    msg.save()

                return {player.id_in_group: 'marked_read'}

            except Exception as e:
                print(f"Error marking messages as read: {e}")
                import traceback
                traceback.print_exc()
                return {player.id_in_group: {'error': str(e)}}

        else:
            return {player.id_in_group: {'error': f'Unknown request type: {data_type}'}}

page_sequence = [Dashboard]