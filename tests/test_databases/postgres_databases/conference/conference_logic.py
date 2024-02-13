from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from your_application.model import SessionParticipant, Question  # Assuming you have this model

def validate_participant_of_session(row: LogicRow):
    # This function would be a placeholder for your validation logic.
    # You would check if the participant who is trying to post a question
    # is registered for the session linked to the question.
    question = row.new_row  # The question being posted
    participant_id = question.participant_id
    session_id = question.session_id
    # Query your database to check if the participant is associated with the session
    participant_session = SessionParticipant.query.filter_by(participant_id=participant_id, session_id=session_id).first()
    if not participant_session:
        raise ValueError("Participant must be registered for the session to post questions.")

# Define the rule
Rule.commit_row_event(on_class=Question, calling=validate_participant_of_session, row_event="before_insert")