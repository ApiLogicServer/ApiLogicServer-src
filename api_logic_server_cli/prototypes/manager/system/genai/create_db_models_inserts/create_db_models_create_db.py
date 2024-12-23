

# ALS/GenAI: Create an SQLite database
import os
mgr_db_loc = True
if mgr_db_loc:
    print(f'creating in manager: sqlite:///system/genai/temp/create_db_models.sqlite')
    engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
else:
    current_file_path = os.path.dirname(__file__)
    print(f'creating at current_file_path: {current_file_path}')
    engine = create_engine(f'sqlite:///{current_file_path}/create_db_models.sqlite')
Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
session = Session()

# ALS/GenAI: Prepare for sample data

