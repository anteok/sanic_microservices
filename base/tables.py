from sqlalchemy import MetaData, Table, Column, String, ForeignKey, UniqueConstraint, PrimaryKeyConstraint

metadata = MetaData()


users = Table(
    'users',
    metadata,
    Column('id', String, primary_key=True, index=True),
    Column('username', String, nullable=False, unique=True),
    Column('password', String, nullable=False),
    Column('email', String, nullable=False, unique=True),
    PrimaryKeyConstraint('id', name='users_id'),
    UniqueConstraint('username', name='username_un'),
    UniqueConstraint('email', name='email_un'),
)

offers = Table(
    'offers',
    metadata,
    Column('id', String, primary_key=True, index=True),
    Column('user_id', String, ForeignKey('users.id'), nullable=False),
    Column('text', String),
    PrimaryKeyConstraint('id', name='offers_id'),
)
