from sqlalchemy import UniqueConstraint, create_engine, Column, Integer, String, ForeignKey, Table, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

'''
Use SQLAlchemy to create a sqlite database named system/genai/temp/model.sqlite, with courses, semesters, course_sections, students, instructors, student_course_enrollments and course_section_instructors. The relationships between these objects are as follows:

A course has many course_sections and a course_section has exactly one course.
Each course_section is offered on a specific semester and has a list of days and times on which the classes for that course_section is taught.
A student_course_enrollment is associated with exactly one course_section and exactly one student.
A course_section_instructor is associated with exactly one course_section and one instructor.
Each semester has a unique semester season label which is one of Winter24, Summer24, Fall24, Winter25, etc.
Hints: use autonum keys, allow nulls, Decimal types, foreign keys, no check constraints.

Include a notes field for courses, students, instructors and course_sections.

Create a few rows of data for each of courses, students, instructors and semesters.

Enforce the following StudentCourseSectionEnrollment requirement (do not generate check constraints):

A student cannot be enrolled in more than one course_section for the same course,
using a unique index for student and course_section.


------- creating this system (3 ChatGPT bugs)....

0. Copy to the manager
    ./chat_gpt-original.txt
1. als genai --using=students_courses.prompt --gen-using-file=system/genai/temp/chatgpt_retry.txt
    (more predictable than: als genai --using=students_courses.prompt)   
2. FAILS with missing import for UniqueConstraint - VSCode quick-fixes it.
3. Run "Retry from repaired model"
    * aside: the cli wants to recreate nw!
        * als create --project-name=students_courses --from-model=system/genai/temp/model.py --db-url=
4. Gens, but FAILED to create Ids, resulting in tables not classes
    * Repair by copying this over model (see fix below) 
    * AND DELETE DB!!
5.  Run "Retry from repaired model" (should be good now)

Revealing 3r bug - bad code for unique constraint
    https://stackoverflow.com/questions/65191991/sqlalchemy-composite-unique-constraint-creates-two-individual-indexes

'''

# Create database engine
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite', echo=True)
Base = declarative_base()

# Define the database schema
class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    notes = Column(String)
    course_sections = relationship("CourseSection", back_populates="course")

class Semester(Base):
    __tablename__ = 'semesters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    season_label = Column(String, unique=True)
    
class CourseSection(Base):
    __tablename__ = 'course_sections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    semester_id = Column(Integer, ForeignKey('semesters.id'))
    days_times = Column(String)
    notes = Column(String)
    course = relationship("Course", back_populates="course_sections")
    semester = relationship("Semester")

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    notes = Column(String)

class Instructor(Base):
    __tablename__ = 'instructors'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    notes = Column(String)

''' BUG: created tables not classes (failed to create id)...
student_course_enrollment = Table('student_course_enrollment', Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('course_section_id', Integer, ForeignKey('course_sections.id')),
    UniqueConstraint('student_id', 'course_section_id')
)

course_section_instructor = Table('course_section_instructor', Base.metadata,
    Column('instructor_id', Integer, ForeignKey('instructors.id')),
    Column('course_section_id', Integer, ForeignKey('course_sections.id')),
)

ChatGPT has created the tables above, but I will use the classes created by CoPilot (remarkable!)
'''

class StudentCourseEnrollment(Base):
    __tablename__ = 'student_course_enrollments'
    __table_args__ = (
        UniqueConstraint('student_id', 'course_section_id', name="your_unique_constraint_name"),
    )    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    course_section_id = Column(Integer, ForeignKey('course_sections.id'))
    student = relationship("Student")
    course_section = relationship("CourseSection")
    #  BUG: incorrect code: UniqueConstraint('student_id', 'course_section_id')

class CourseSectionInstructor(Base):
    __tablename__ = 'course_section_instructors'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instructor_id = Column(Integer, ForeignKey('instructors.id'))
    course_section_id = Column(Integer, ForeignKey('course_sections.id'))
    instructor = relationship("Instructor")
    course_section = relationship("CourseSection")

# Create tables in the database
Base.metadata.create_all(engine)
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

# Sample data for courses
course_data = [
    Course(name='Mathematics', notes='Introductory course on mathematics'),
    Course(name='Physics', notes='Basic concepts in physics'),
    Course(name='Computer Science', notes='Introduction to programming'),
]

session.add_all(course_data)

# Sample data for semesters
semester_data = [
    Semester(season_label='Winter24'),
    Semester(season_label='Summer24'),
    Semester(season_label='Fall24'),
]

session.add_all(semester_data)

# Sample data for students
student_data = [
    Student(name='Alice', notes='Undergraduate student'),
    Student(name='Bob', notes='Graduate student'),
    Student(name='Eve', notes='Exchange student'),
]

session.add_all(student_data)

# Sample data for instructors
instructor_data = [
    Instructor(name='Dr. Smith', notes='Mathematics professor'),
    Instructor(name='Prof. Johnson', notes='Physics professor'),
    Instructor(name='Dr. Lee', notes='Computer Science professor'),
]

session.add_all(instructor_data)

session.commit()
session.close()
