from datetime import datetime
from sqlalchemy.exc import IntegrityError

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        """Does the repr method for User work as expected?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(repr(u), f"<User #{u.id}: {u.username}, {u.email}>")

    def test_follows(self):
        """Does the is_following and is_followed_by methods work?"""

        u1 = User(
            email="user1@test.com",
            username="user1",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="user2@test.com",
            username="user2",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        # User1 follows User2
        u1.following.append(u2)
        db.session.commit()

        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertFalse(u2.is_following(u1))

    def test_signup(self):
        """Does the signup class method work?"""

        username = "newuser"
        email = "newuser@test.com"
        password = "newpassword"

        user = User.signup(username, email, password, None)

        db.session.commit()

        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.image_url, "/static/images/default-pic.png")

    def test_authentication(self):
        """Does the authenticate class method work?"""

        username = "authuser"
        email = "authuser@test.com"
        password = "authpassword"

        user = User.signup(username, email, password, None)

        db.session.commit()

        authenticated_user = User.authenticate(username, password)

        self.assertEqual(authenticated_user, user)

        wrong_password_user = User.authenticate(username, "wrongpassword")

        self.assertFalse(wrong_password_user)

    def test_duplicate_username_signup(self):
        """Does signup prevent a duplicate username?"""

        username = "newuser"
        email = "newuser@test.com"
        password = "newpassword"

        user = User.signup(username, email, password, None)
        db.session.commit()

        # Attempt to create a user with the same username
        duplicate_user = User.signup(username, "differentemail@test.com", "differentpassword", None)

        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_duplicate_email_signup(self):
        """Does signup prevent a duplicate email?"""

        username1 = "user1"
        email = "newuser@test.com"
        password1 = "password1"

        user1 = User.signup(username1, email, password1, None)
        db.session.commit()

        # Attempt to create a user with the same email
        username2 = "user2"
        user2 = User.signup(username2, email, "password2", None)

        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_user_likes(self):
        """Does the likes relationship work?"""

        user = User(
            email="user@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        message = Message(
            text="Test message",
            timestamp=datetime.utcnow(),
            user_id=user.id
        )

        db.session.add_all([user, message])
        db.session.commit()

        # User likes a message
        user.likes.append(message)
        db.session.commit()

        self.assertEqual(len(user.likes), 1)
        self.assertEqual(user.likes[0], message)

    def test_user_repr(self):
        """Does the repr method for Message work as expected?"""

        user = User(
            email="user@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(user)
        db.session.commit()

        message = Message(
            text="Test message",
            timestamp=datetime.utcnow(),
            user_id=user.id
        )

        db.session.add(message)
        db.session.commit()

        self.assertEqual(repr(message), f"<Message #{message.id}: {message.text}>")

if __name__ == '__main__':
    unittest.main()
