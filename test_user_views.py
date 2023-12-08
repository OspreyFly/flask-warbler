import os
from unittest import TestCase
from models import db, User, Message, Follows
from app import app, CURR_USER_KEY

# Use a different database for testing
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Create our tables
db.create_all()

class UserViewsTestCase(TestCase):
    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        # Add a test user
        self.user = User.signup("testuser", "test@test.com", "password", None)
        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transactions."""
        db.session.rollback()

    def test_signup_form(self):
        """Test rendering the signup form."""
        with self.client as c:
            resp = c.get('/signup')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<form method="POST" action="/signup">', html)

    def test_signup(self):
        """Test user signup."""
        with self.client as c:
            resp = c.post('/signup', data={'username': 'newuser', 'email': 'new@test.com', 'password': 'password'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Hello, newuser!', html)

    def test_login_form(self):
        """Test rendering the login form."""
        with self.client as c:
            resp = c.get('/login')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<form method="POST" action="/login">', html)

    def test_login(self):
        """Test user login."""
        with self.client as c:
            resp = c.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Hello, testuser!', html)

    def test_logout(self):
        """Test user logout."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            resp = c.get('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Logout Successful', html)

    def test_users_show(self):
        """Test showing a user profile."""
        with self.client as c:
            resp = c.get(f'/users/{self.user.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<p>@{self.user.username}</p>', html)

    def test_list_users(self):
        """Test listing users."""
        with self.client as c:
            resp = c.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<a href="/users/{self.user.id}">@{self.user.username}</a>', html)
