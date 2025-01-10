from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TestBase(Base):
    __abstract__ = True
    def __init__(self, *args, **kwargs):
        for name, val in kwargs.items():
            col = getattr(self.__class__, name)
            kwargs[name] = col.type.python_type(val)
        return super().__init__(*args, **kwargs)