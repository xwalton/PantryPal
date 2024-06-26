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
	api_key = "my-api-key"
	api_url = 'https://api.spoonacular.com/recipes/complexSearch'

	parameters = {
		'apiKey': api_key,
		'includeIngredients': ingredients,
		'diet': diet,
		'intolerances': dietary_intolerances,
		'number': 1,
		'addRecipeInformation': True
	}

	try:
		response = requests.get(api_url, params=parameters)
		response.raise_for_status()
		data = response.json()

		if data['results']:
			recipe = data['results'][0]
			recipe_title = recipe.get('title', 'No title')
			recipe_steps = recipe.get('instructions', 'No instructions')
			recipe_text = f"Title: {recipe_title}\nInstructions: {recipe_steps}"
			return recipe_text
		else:
			return "No recipes found based on the provided ingredients and dietary preferences/restrictions."
	except Exception as error:
		print(f"An error has occurred: {error}")
		return "Due to an error, recipe generation has failed."



def insert_recipe(ingredients, dietary_intolerances, diet, recipe_text):
# This will insert the recipe into Database
	conn = sqlite3.connect('pantryPartner.db') 
	cursor = conn.cursor() 

	cursor.execute("SELECT MAX(recipe_number) FROM recipes;")
	result = cursor.fetchone()
	recipe_number = result[0] + 1 if result[0] else 1

	cursor.execute('''
	INSERT INTO recipes (recipe_number, ingredients, dietary_intolerances, diet, recipe_text) 
	VALUES (?, ?, ?, ?, ?)
	 ''', (recipe_number, ingredients, dietary_intolerances, diet, recipe_text)) 
	conn.commit() 
	conn.close()

def create_database():
# This will create the database and table that we want to insert the recipe and related information into.
	conn = sqlite3.connect('pantryPartner.db') #connects to database, if pantryPartner.db doesn’t exist, will be created
	cursor = conn.cursor()
	cursor.execute('DROP TABLE IF EXISTS recipes;')
	cursor.execute( ''' 
		CREATE TABLE IF NOT EXISTS recipes (
			recipe_number INTEGER PRIMARY KEY,
			ingredients TEXT,
			dietary_intolerances TEXT,
			diet TEXT,
			recipe_text TEXT
		)
	''')
	print("Table successfully created...") # This is to check code’s success
	conn.commit()
	conn.close()

def main():
	create_database()

	dietary_intolerances = extract_input("What dietary intolerances do you have? Enter as a comma separated list (e.g. dairy, peanut, gluten, etc.)")
	diet = extract_input("Do you follow any particular diet? Enter as a comma separated list (e.g. gluten free, vegetarian, etc.) If not, write None.")
	ingredients = extract_input("What ingredients do you have on hand? Enter as a comma separated list.")

	recipe_text = request_recipe(dietary_intolerances, diet, ingredients)
	print("\nGenerated Recipe:\n", recipe_text)

	insert_recipe(ingredients, dietary_intolerances, diet, recipe_text)

if __name__ == "__main__":
	main()