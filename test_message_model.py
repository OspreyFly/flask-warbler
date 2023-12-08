# test_message_model.py

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from unittest import TestCase

from app import app
from models import db, User, Message

# Set the testing database
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.create_all()

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()
        db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transactions."""
        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        m = Message(text="Test message", timestamp=datetime.utcnow(), user_id=u.id)

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(u.messages), 1)
        self.assertEqual(u.messages[0].text, "Test message")
        self.assertEqual(repr(m), f"<Message #{m.id}: {m.text}>")
        self.assertIsInstance(m.timestamp, datetime)

    def test_message_without_user(self):
        """Does creating a message without a user raise an error?"""

        m = Message(text="Test message", timestamp=datetime.utcnow())

        db.session.add(m)

        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_message_repr(self):
        """Does the repr method for Message work as expected?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        m = Message(text="Test message", timestamp=datetime.utcnow(), user_id=u.id)

        db.session.add(m)
        db.session.commit()

        self.assertEqual(repr(m), f"<Message #{m.id}: {m.text}>")

    def test_delete_user_cascades_messages(self):
        """Does deleting a user cascade delete their messages?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        m = Message(text="Test message", timestamp=datetime.utcnow(), user_id=u.id)

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(Message.query.all()), 1)

        db.session.delete(u)
        db.session.commit()

        self.assertEqual(len(Message.query.all()), 0)


if __name__ == '__main__':
    unittest.main()
