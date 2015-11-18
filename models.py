from sqlalchemy import create_engine, Column, Integer, VARCHAR, Text, ForeignKey
from sqlalchemy.sql import select, and_
from configparser import ConfigParser
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def __make_engine():
    parser = ConfigParser()
    parser.read("config.ini")
    section = parser["todolist"]
    user, pw, host, name = section["db_user"], section["db_password"], section["db_host"], section["db_name"]
    eng = create_engine("mysql+pymysql://{}:{}@{}/{}".format(user, pw, host, name))
    return eng

Base = declarative_base()


class TodoItem(Base):
    __tablename__ = "todo_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text)
    completed = Column(Integer, default=0)
    user = Column(ForeignKey("users.email"))


class User(Base):
    __tablename__ = "users"
    email = Column(VARCHAR(254), primary_key=True)
    display_name = Column(Text)
    todo_list = relationship("TodoItem", backref="owner")


eng = __make_engine()
Base.metadata.create_all(bind=eng)
Session = sessionmaker(bind=eng)


def add_user(email, display_name):
    sess = Session()
    user = User(email=email, display_name=display_name)
    sess.add(user)
    sess.commit()


def user_exists(email):
    sess = Session()
    result_count = sess.query(User).filter_by(email=email).count()
    if result_count > 0:
        return True
    else:
        return False


def add_todo(email, todo_description):
    sess = Session()
    user = sess.query(User).filter_by(email=email).one()
    user.todo_list.append(TodoItem(description=todo_description))
    sess.commit()


def get_user_todo_list(email):

    if not email:
        raise Exception("get_user_todo_list requires an email address and was not passed one.")

    sess = Session()
    user = sess.query(User).filter_by(email=email).one_or_none()
    todo_list = user.todo_list if user else []

    return [dict(id=todo.id, description=todo.description)
            for todo in todo_list
            if todo.completed == 0]


def declare_item_done(item_id):
    sess = Session()
    item = sess.query(TodoItem).filter_by(id=item_id).one()
    item.completed = 1
    sess.commit()


if __name__ == '__main__':
    email = "cotejrp@gmail.com"