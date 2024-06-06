from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    teacher = relationship("Teacher")

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)

class Offering(Base):
    __tablename__ = 'offerings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    student_id = Column(Integer, ForeignKey('students.id'))
    grade = Column(DECIMAL)
    """ FIXME these were missing
    course = relationship("Course")
    student = relationship("Student")
    """

# Create the SQLite database
engine = create_engine('sqlite:///system/genai/temp/model.sqlite', echo=True)
Base.metadata.create_all(engine)

# Add some test data
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

teacher_1 = Teacher(name='Alice')
teacher_2 = Teacher(name='Bob')

course_1 = Course(name='Math', teacher=teacher_1)
course_2 = Course(name='Science', teacher=teacher_2)

student_1 = Student(name='Emma')
student_2 = Student(name='John')

offering_1 = Offering(course=course_1, student=student_1, grade=DECIMAL('95.5'))
offering_2 = Offering(course=course_2, student=student_2, grade=DECIMAL('82.3'))
""" FIXME proper syntax
offering_1 = Offering(course=course_1, student=student_1, grade=95.5)
offering_2 = Offering(course=course_2, student=student_2, grade=82.3)
"""

session.add_all([teacher_1, teacher_2, course_1, course_2, student_1, student_2, offering_1, offering_2])
session.commit()

print("Database created with test data.")
