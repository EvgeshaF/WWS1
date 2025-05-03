from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('mongo_db.mongo.MongoConnection.check_mongo_config_exists')
    @patch('mongo_db.mongo.MongoConnection.test_connection')
    def test_index_with_valid_config(self, mock_test, mock_exists):
        mock_exists.return_value = True
        mock_test.return_value = (True, "OK")

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_login_form'])
        self.assertContains(response, "OK")

    @patch('mongo_db.mongo.MongoConnection.check_mongo_config_exists')
    def test_index_no_config(self, mock_exists):
        mock_exists.return_value = False

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['show_login_form'])
        self.assertContains(response, "MongoDB configuration not found")
