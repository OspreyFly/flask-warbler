import os
from unittest import TestCase
from models import db, User, Message
from app import app, CURR_USER_KEY

# Use a different database for testing
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Create our tables
db.create_all()

class MessageViewsTestCase(TestCase):
    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        # Add a test user
        self.user = User.signup("testuser", "test@test.com", "password", None)
        db.session.commit()

        # Add a test message
        self.message = Message(text="Test message", user_id=self.user.id)
        db.session.add(self.message)
        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transactions."""
        db.session.rollback()

    def test_show_message(self):
        """Test showing a message."""
        with self.client as c:
            resp = c.get(f'/messages/{self.message.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.message.text, html)

    def test_messages_add_form(self):
        """Test rendering the add message form."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            resp = c.get('/messages/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<form method="POST" action="/messages/new">', html)

    def test_messages_add(self):
        """Test adding a new message."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            resp = c.post('/messages/new', data={'text': 'New test message'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('New test message', html)
            self.assertIn('Test message', html)  # Check if old message is still there

    def test_messages_destroy(self):
        """Test deleting a message."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            resp = c.post(f'/messages/{self.message.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(self.message.text, html)
