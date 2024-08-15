from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

# Create the SQLite engine
engine = create_engine('sqlite:///system/genai/temp/model.sqlite')

# Create a base class for different table models
Base = declarative_base()

# Define the tables

class Planet(Base):
    __tablename__ = 'planets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    population = Column(Integer, nullable=True)

class Species(Base):
    __tablename__ = 'species'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    lifespan = Column(Integer, nullable=True)

class Candidate(Base):
    __tablename__ = 'candidates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    species_id = Column(Integer, ForeignKey('species.id'), nullable=False)
    homeworld_id = Column(Integer, ForeignKey('planets.id'), nullable=True)

    species = relationship("Species")
    homeworld = relationship("Planet")

class Voter(Base):
    __tablename__ = 'voters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    birth_date = Column(DateTime, nullable=True)
    planet_id = Column(Integer, ForeignKey('planets.id'), nullable=True)

    planet = relationship("Planet")

class Election(Base):
    __tablename__ = 'elections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

class Vote(Base):
    __tablename__ = 'votes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    voter_id = Column(Integer, ForeignKey('voters.id'), nullable=False)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    election_id = Column(Integer, ForeignKey('elections.id'), nullable=False)
    vote_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)

    voter = relationship("Voter")
    candidate = relationship("Candidate")
    election = relationship("Election")

class CampaignEvent(Base):
    __tablename__ = 'campaign_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_name = Column(String, nullable=False)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    event_date = Column(DateTime, nullable=False)
    planet_id = Column(Integer, ForeignKey('planets.id'), nullable=False)

    candidate = relationship("Candidate")
    planet = relationship("Planet")

class Poll(Base):
    __tablename__ = 'polls'

    id = Column(Integer, primary_key=True, autoincrement=True)
    poll_name = Column(String, nullable=False)
    election_id = Column(Integer, ForeignKey('elections.id'), nullable=False)
    date_conducted = Column(DateTime, nullable=False)

    election = relationship("Election")

class PollResult(Base):
    __tablename__ = 'poll_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    poll_id = Column(Integer, ForeignKey('polls.id'), nullable=False)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    percentage = Column(Integer, nullable=False)

    poll = relationship("Poll")
    candidate = relationship("Candidate")

class Debate(Base):
    __tablename__ = 'debates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    debate_name = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False)
    planet_id = Column(Integer, ForeignKey('planets.id'), nullable=False)

    planet = relationship("Planet")

class DebateParticipant(Base):
    __tablename__ = 'debate_participants'

    id = Column(Integer, primary_key=True, autoincrement=True)
    debate_id = Column(Integer, ForeignKey('debates.id'), nullable=False)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)

    debate = relationship("Debate")
    candidate = relationship("Candidate")

class CampaignDonation(Base):
    __tablename__ = 'campaign_donations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    donor_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    donation_date = Column(DateTime, nullable=False)

    candidate = relationship("Candidate")

class Party(Base):
    __tablename__ = 'parties'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class CandidateParty(Base):
    __tablename__ = 'candidate_parties'

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    party_id = Column(Integer, ForeignKey('parties.id'), nullable=False)

    candidate = relationship("Candidate")
    party = relationship("Party")

class NewsArticle(Base):
    __tablename__ = 'news_articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    publication_date = Column(DateTime, nullable=False)

class CandidateEndorsement(Base):
    __tablename__ = 'candidate_endorsements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    endorser_name = Column(String, nullable=False)
    endorsement_date = Column(DateTime, nullable=False)

    candidate = relationship("Candidate")

# Create tables in the database
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Sample data

# Planets
naboo = Planet(name='Naboo', population=4500000000)
coruscant = Planet(name='Coruscant', population=1000000000000)
tatooine = Planet(name='Tatooine', population=200000)

session.add_all([naboo, coruscant, tatooine])
session.commit()

# Species
human = Species(name='Human', lifespan=80)
twi_lek = Species(name='Twi\'lek', lifespan=90)
wookiee = Species(name='Wookiee', lifespan=400)

session.add_all([human, twi_lek, wookiee])
session.commit()

# Candidates
candidate_1 = Candidate(name='Leia Organa', species_id=human.id, homeworld_id=naboo.id)
candidate_2 = Candidate(name='Bail Antilles', species_id=human.id, homeworld_id=coruscant.id)
candidate_3 = Candidate(name='Chewbacca', species_id=wookiee.id, homeworld_id=tatooine.id)

session.add_all([candidate_1, candidate_2, candidate_3])
session.commit()

# Voters
voter_1 = Voter(name='Luke Skywalker', birth_date=datetime(19, 5, 25), planet_id=tatooine.id)
voter_2 = Voter(name='Padmé Amidala', birth_date=datetime(46, 12, 25), planet_id=naboo.id)
voter_3 = Voter(name='Han Solo', birth_date=datetime(29, 2, 1), planet_id=coruscant.id)

session.add_all([voter_1, voter_2, voter_3])
session.commit()

# Elections
election_1 = Election(name='Galactic Presidential Election 2024', start_date=datetime(2024, 11, 1), end_date=datetime(2024, 11, 30))

session.add(election_1)
session.commit()

# Votes
vote_1 = Vote(voter_id=voter_1.id, candidate_id=candidate_1.id, election_id=election_1.id)
vote_2 = Vote(voter_id=voter_2.id, candidate_id=candidate_2.id, election_id=election_1.id)
vote_3 = Vote(voter_id=voter_3.id, candidate_id=candidate_3.id, election_id=election_1.id)

session.add_all([vote_1, vote_2, vote_3])
session.commit()

# Campaign Events
event_1 = CampaignEvent(event_name='Leia\'s Rally on Naboo', candidate_id=candidate_1.id, event_date=datetime(2024, 10, 15), planet_id=naboo.id)
event_2 = CampaignEvent(event_name='Bail\'s Debate on Coruscant', candidate_id=candidate_2.id, event_date=datetime(2024, 10, 20), planet_id=coruscant.id)

session.add_all([event_1, event_2])
session.commit()

# Polls
poll_1 = Poll(poll_name='Galactic Pre-Election Poll', election_id=election_1.id, date_conducted=datetime(2024, 10, 25))

session.add(poll_1)
session.commit()

# Poll Results
poll_result_1 = PollResult(poll_id=poll_1.id, candidate