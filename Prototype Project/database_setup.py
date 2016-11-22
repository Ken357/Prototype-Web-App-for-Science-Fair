import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Users(Base):
    """
    one to many table type
    this will be the main table where we will store all the users credentials
    for log in
    """
    __tablename__= "Users"
    username = Column(String(100),nullable=False, unique=True)
    name = Column(String(100),nullable=False)
    id = Column(Integer, primary_key=True)
    password = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    telephone = Column(String(100))

    @property
    def JsonReturn(self):
        return {
            "name": self.name,
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "telephone": self.telephone
        }

    def __repr__(self):
        return str(self.JsonReturn)


class Adress(Base):
    """
    Support table for storing the user's adresses
    """
    __tablename__="Adress"
    id = Column(Integer, primary_key=True)
    username = Column(Integer, ForeignKey(Users.username), nullable=False)
    adress_line = Column(String(100))
    City = Column(String(100), nullable=False)
    State = Column(String(100), nullable=False)
    Zip_Code = Column(Integer)
    users = relationship(Users)
    @property
    def JsonReturn(self):
        return{
            "username": self.username,
            "adress_line": self.adress_line,
            "City": self.City,
            "State": self.State,
            "Zip_Code": self.Zip_Code
        }

    def __repr__(self):
        return str(self.JsonReturn)


class advertisements(Base):
    """
    Table that will store the advertisements that will be published
    """
    __tablename__="advertisements"

    title = Column(String(200), nullable=False)
    owner_id = Column(Integer, ForeignKey(Users.id), nullable=False)
    id = Column(Integer, primary_key=True)
    image = Column(String(200))
    type_ad = Column(String(200))
    description = Column(String(500))
    date = Column(Date, nullable=False)
    owner = relationship(Users)

    @property
    def JsonReturn(self):
        return{
            "title":self.title,
            "owner_id":self.owner_id,
            "id":self.id,
            "image":self.image,
            "type_ad":self.type_ad,
            "description":self.description,
            "date":self.date
        }


class organized_searches:
    """
    Store daily searches from users
    """
    __tablename__="Entry history"
    id = Column(Integer,primary_key=True)
    search_date = Column(Date,nullable=False)
    person = Column(Integer, ForeignKey(Users.id))
    ad = Column(Integer, ForeignKey(advertisements.id))
    user = relationship(Users)
    ads = relationship(advertisements)

    @property
    def JsonReturn(self):
        return {
            "id": self.id,
            "search_date": self.search_date,
            "person": self.person,
            "ad": self.ad
        }



engine = create_engine('sqlite:///prototype.db')


Base.metadata.create_all(engine)
