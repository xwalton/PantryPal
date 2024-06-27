import sqlite3
import os
import requests
import re

def extract_input(answer):
# This will extract user input, making sure that it isn’t an empty string or contains integer characters.
		user_input = input(answer).strip()
		if not user_input or any(char.isdigit() for char in user_input):
			print("Input not valid. Please try again.")
		else: 
			return user_input.lower()

def request_recipe(dietary_intolerances, diet, ingredients):
# This will query the Spoonacular API for recipes that match the user input.
	api_key = "2b25d116497643558cfdf92ed2026398"
	api_url = 'https://api.spoonacular.com/recipes/complexSearch'
	recipe_info_url = 'https://api.spoonacular.com/recipes/{id}/information'

	parameters = {
		'apiKey': api_key,
		'includeIngredients': ingredients,
		'diet': diet,
		'intolerances': dietary_intolerances,
		'number': 1,
	}

	try:
		response = requests.get(api_url, params=parameters)
		response.raise_for_status()
		api_data = response.json()

		if api_data['results']:
			recipe_id = api_data['results'][0]['id']
			info_params = {'apiKey': api_key}
			info_response = requests.get(recipe_info_url.format(id=recipe_id), params=info_params)
			info_response.raise_for_status()
			recipe = info_response.json()

			recipe_title = recipe.get('title', 'No title')
			recipe_ingredients = [ingredient['original'] for ingredient in recipe.get('extendedIngredients', [])]
			recipe_instructions = recipe.get('instructions', 'No instructions')
			cleaned_instructions = recipe_instructions.replace('</li>', '').replace('</ol>', '')

			recipe_instructions_text = re.sub(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.)(?!\d)', '\n', cleaned_instructions)
			ingredients_text = "Ingredients:\n" + "\n".join(recipe_ingredients)
			output_text = f"Title: {recipe_title}\n\n{ingredients_text}\n\nInstructions:\n{recipe_instructions_text}"

			return recipe_title, recipe_ingredients, output_text
		else:
			return "", [], "No recipes found based on the provided ingredients and dietary preferences/restrictions."
	except Exception as error:
		print(f"An error has occurred: {error}")
		return "", [], "Due to an error, recipe generation has failed."



def insert_recipe(api_ingredients, dietary_intolerances, diet, recipe_text, recipe_title):
# This will insert the recipe into Database
	conn = sqlite3.connect('pantryPartner.db') 
	cursor = conn.cursor() 
	cursor.execute("SELECT MAX(recipe_number) FROM recipes;")
	result = cursor.fetchone()
	recipe_number = result[0] + 1 if result[0] else 1

	str_ingredients = ', '.join(api_ingredients)
	cursor.execute('''
	INSERT INTO recipes (recipe_number, title, ingredients, dietary_intolerances, diet, recipe_text) 
	VALUES (?, ?, ?, ?, ?, ?)
	 ''', (recipe_number, recipe_title, str_ingredients, dietary_intolerances, diet, recipe_text)) 
	conn.commit() 
	conn.close()

def print_recipes(recipes):
	if not recipes:
		print("Recipe history does not exist.")
		return
	print("\n{:<12} {:<30} {:<20} {:<20} {:<20}".format('Recipe No.', 'Title', 'Intolerances', 'Diet', 'Ingredients'))
	print('-' * 104)

	for recipe in recipes:
		print("{:<12} {:<30} {:<20} {:<20} {:<20}".format(
			recipe[0],
			recipe[1][:28] + '...' if len(recipe[1]) > 28 else recipe[1],
			recipe[3][:18] + '...' if len(recipe[3]) > 18 else recipe[3],
            recipe[4][:18] + '...' if len(recipe[4]) > 18 else recipe[4],
            recipe[2][:18] + '...' if len(recipe[2]) > 18 else recipe[2]
        ))


def create_database():
# This will create the database and table that we want to insert the recipe and related information into.
	conn = sqlite3.connect('pantryPartner.db') #connects to database, if pantryPartner.db doesn’t exist, will be created
	cursor = conn.cursor()
	cursor.execute( ''' 
		CREATE TABLE IF NOT EXISTS recipes (
			recipe_number INTEGER PRIMARY KEY,
			title TEXT,
			ingredients TEXT,
			dietary_intolerances TEXT,
			diet TEXT,
			recipe_text TEXT
		)
	''')
	print("Database ready.") # This is to check code’s success
	conn.commit()
	conn.close()

def view_recent_recipe_history():
#Enables user to view their search history
	conn = sqlite3.connect('pantryPartner.db')
	cursor = conn.cursor()
	cursor.execute("""
        SELECT recipe_number, title, ingredients, dietary_intolerances, diet 
        FROM recipes 
        ORDER BY recipe_number DESC 
        LIMIT 15
    """)
	recipes = cursor.fetchall()
	conn.close()
	print_recipes(recipes)


def search_recipe_history():
	search_query = input("Enter a keyword to search in recipes (title, ingredients, diet, or intolerances): ").lower()
	conn = sqlite3.connect('pantryPartner.db')
	cursor = conn.cursor()
	query = f"SELECT recipe_number, title, ingredients, dietary_intolerances, diet FROM recipes WHERE \
		title LIKE '%{search_query}%' OR \
		ingredients LIKE '%{search_query}%' OR \
		dietary_intolerances LIKE '%{search_query}%' OR \
		diet LIKE '%{search_query}%'"
	cursor.execute(query)
	results = cursor.fetchall()
	conn.close()
	print_recipes(results)
			

def main():
	create_database()
	
	dietary_intolerances = extract_input("What dietary intolerances do you have? Enter as a comma separated list (e.g. dairy, peanut, gluten, etc.)")
	diet = extract_input("Do you follow any particular diet? Enter as a comma separated list (e.g. gluten free, vegetarian, etc.) If not, write None.")
	ingredients = extract_input("What ingredients do you have on hand? Enter as a comma separated list.")

	recipe_title, api_ingredients, recipe_text = request_recipe(dietary_intolerances, diet, ingredients)
	print("\nGenerated Recipe:\n", recipe_text)

	if recipe_text != "No recipes found based on the provided ingredients and dietary preferences/restrictions." and recipe_text != "Due to an error, recipe generation has failed.":
		insert_recipe(api_ingredients, dietary_intolerances, diet, recipe_text, recipe_title)

	if input("Would you like to see your recipe history? (yes/no): ").lower() == 'yes':
		view_recent_recipe_history()
		if input("Would you like to search through the recipes? (yes/no): ").lower() == 'yes':
			search_recipe_history()

if __name__ == "__main__":
	main()