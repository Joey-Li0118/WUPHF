from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth.models import User
from .models import Wuphf, WuphfReceiver

class WuphfTestCase(TestCase):
    def setUp(self):
        """Set up test data before each test"""
        self.user = User.objects.create(username="test_user")  # Create a test sender
        self.receiver1 = WuphfReceiver.objects.create(name="Receiver One", email="receiver1@example.com")
        self.receiver2 = WuphfReceiver.objects.create(name="Receiver Two", email="receiver2@example.com")
        
        # Create a Wuphf with receivers
        self.wuphf = Wuphf.objects.create(sender=self.user, message= "Test message")
        self.wuphf.receivers.add(self.receiver1, self.receiver2)  # Add receivers

    @patch("wuphf.utils.notify.sendEmail")  # Mock sendEmail function
    def test_send_wuphf_emails(self, mock_send_email):
        """Test that sendEmail is called for receivers with emails"""
        self.wuphf.send_wuphf()

        # Assert that sendEmail was called twice (once for each receiver with an email)
        self.assertEqual(mock_send_email.call_count, 2)

        # Assert specific calls with correct arguments
        mock_send_email.assert_any_call("receiver1@example.com", "Test message")
        mock_send_email.assert_any_call("receiver2@example.com", "Test message")
