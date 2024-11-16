import sys
import os
from datetime import datetime
import unittest
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import VideoSearcher, SearchConfig, WordpressAPI, FirebaseConnection

class TestMain(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
def test_load_environment_variables_not_in_colab(self):
    # Mock sys.modules to simulate not being in Google Colab
    with patch.dict('sys.modules', {'google.colab': None}):
        # Mock os.environ to simulate environment variables
        mock_env = {
            'GROQ_API_KEY': 'test_groq_key',
            'MODE': 'production',
            'WP_USER_PROD': 'test_user',
            'WP_PASS_PROD': 'test_pass',
            'WP_URL_PROD': 'http://test.com'
        }
        with patch.dict('os.environ', mock_env):
            # Mock load_dotenv to ensure it's called
            with patch('dotenv.load_dotenv') as mock_load_dotenv:
                # Re-import the module to trigger the code execution
                import importlib
                import main
                importlib.reload(main)

                # Assert that load_dotenv was called
                mock_load_dotenv.assert_called_once()

                # Assert that environment variables were correctly loaded
                self.assertEqual(main.groq_api_key, 'test_groq_key')
                self.assertEqual(main.mode, 'production')
                self.assertEqual(main.wpuser, 'test_user')
                self.assertEqual(main.wppass, 'test_pass')
                self.assertEqual(main.wpurl, 'http://test.com')