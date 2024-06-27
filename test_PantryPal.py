import unittest
from unittest.mock import patch, MagicMock
from pantryPal import extract_input, request_recipe, insert_recipe, create_database

class TestPantryPal(unittest.TestCase):
    def test_extract_input_valid_option(self):
        options = ["Option1", "Option2"]
        answer, result = extract_input("Please enter your choice:", "Option1", options)
        self.assertTrue("Options:\nOption1   Option2   " in answer)  
        self.assertEqual(result, "option1")

    @patch('pantryPal.requests.get')
    def test_request_recipe_valid(self, mock_get):
        mock_search_response = MagicMock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {
            "results": [{"id": 123}],
            "totalResults": 1
        }

        mock_details_response = MagicMock()
        mock_details_response.status_code = 200
        mock_details_response.json.return_value = {
            "title": "Some Recipe Title",
            "extendedIngredients": [{"original": "carrots"}],
            "instructions": "Chop and cook."
        }

        def side_effect(url, params):
            if "complexSearch" in url:
                return mock_search_response
            elif "recipes/" in url and "/information" in url:
                return mock_details_response

        mock_get.side_effect = side_effect

        
        title, ingredients, output = request_recipe("gluten", "vegan", "carrots, tomatoes")
        self.assertEqual(title, "Some Recipe Title")  

    @patch('pantryPal.sqlite3.connect')
    def test_insert_recipe(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = [1]  

        result = insert_recipe(["carrots"], "none", "vegan", "Recipe Text", "Carrot Soup")
        self.assertTrue(result)  

if __name__ == '__main__':
    unittest.main()