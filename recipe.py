import DBbase as db
import csv

class Recipe(db.DBbase):

    def __init__(self):
        super().__init__("recipeDB.sqlite")

    def add_recipe(self, name, category_id, ingredients):
        try:
            super().get_cursor.execute("INSERT INTO Recipes (name, category_id) VALUES (?, ?);", (name, category_id))
            recipe_id = super().get_cursor.lastrowid

            for ingredient in ingredients:
                super().get_cursor.execute("INSERT INTO Ingredients (recipe_id, name) VALUES (?, ?);",
                                           (recipe_id, ingredient))

            super().get_connection.commit()
            print(f"Recipe '{name}' added successfully.")
        except Exception as e:
            print("An error has occurred while adding the recipe.", e)

    def update_recipe(self, recipe_id, name=None, category_id=None, ingredients=None):
        try:
            if name:
                super().get_cursor.execute("UPDATE Recipes SET name = ? WHERE id = ?;", (name, recipe_id))
            if category_id:
                super().get_cursor.execute("UPDATE Recipes SET category_id = ? WHERE id = ?;", (category_id, recipe_id))
            if ingredients is not None:
                super().get_cursor.execute("DELETE FROM Ingredients WHERE recipe_id = ?;", (recipe_id,))
                for ingredient in ingredients:
                    super().get_cursor.execute("INSERT INTO Ingredients (recipe_id, name) VALUES (?, ?);",
                                               (recipe_id, ingredient))
            super().get_connection.commit()
            print(f"Recipe ID {recipe_id} updated successfully.")
        except Exception as e:
            print("An error has occurred while updating the recipe.", e)

    def delete_recipe(self, recipe_id):
        try:
            super().get_cursor.execute("DELETE FROM Recipes WHERE id = ?;", (recipe_id,))
            super().get_cursor.execute("DELETE FROM Ingredients WHERE recipe_id = ?;", (recipe_id,))
            super().get_connection.commit()
            print(f"Recipe ID {recipe_id} and associated ingredients successfully deleted.")
        except Exception as e:
            print("An error has occurred while deleting the recipe.", e)

    def fetch_recipes(self, id=None):
        try:
            if id is not None:
                return super().get_cursor.execute("""
                                SELECT Recipes.id, Recipes.name, Categories.name AS category,
                                       GROUP_CONCAT(Ingredients.name) AS ingredients
                                FROM Recipes
                                JOIN Categories ON Recipes.category_id = Categories.id
                                LEFT JOIN Ingredients ON Recipes.id = Ingredients.recipe_id
                                WHERE Recipes.id = ?
                                GROUP BY Recipes.id;
                            """, (id,)).fetchone()
            else:
                return super().get_cursor.execute("""
                                SELECT Recipes.id, Recipes.name, Categories.name AS category,
                                       GROUP_CONCAT(Ingredients.name) AS ingredients
                                FROM Recipes
                                JOIN Categories ON Recipes.category_id = Categories.id
                                LEFT JOIN Ingredients ON Recipes.id = Ingredients.recipe_id
                                GROUP BY Recipes.id;
                            """).fetchall()
        except Exception as e:
            print("An error has occurred while fetching recipes.", e)

    def fetch_recipes_by_category(self, category_id=None):
        try:
            if category_id is not None:
                return super().get_cursor.execute("""
                                SELECT Recipes.id, Recipes.name, Categories.name AS category,
                                       GROUP_CONCAT(Ingredients.name) AS ingredients
                                FROM Recipes
                                JOIN Categories ON Recipes.category_id = Categories.id
                                LEFT JOIN Ingredients ON Recipes.id = Ingredients.recipe_id
                                WHERE Recipes.category_id = ?
                                GROUP BY Recipes.id;
                            """, (category_id,)).fetchall()
            else:
                return super().get_cursor.execute("""
                                SELECT Recipes.id, Recipes.name, Categories.name AS category,
                                       GROUP_CONCAT(Ingredients.name) AS ingredients
                                FROM Recipes
                                JOIN Categories ON Recipes.category_id = Categories.id
                                LEFT JOIN Ingredients ON Recipes.id = Ingredients.recipe_id
                                GROUP BY Recipes.id;
                            """).fetchall()
        except Exception as e:
            print("An error has occurred while fetching recipes.", e)

    def get_valid_category(self):
        while True:
            try:
                category = int(input("Enter category ID (1: Breakfast, 2: Lunch, 3: Dinner, 4: Dessert, 5: Snack): "))
                if category not in range(1, 6):
                    print("Invalid category. Please enter a number between 1 and 5.")
                else:
                    return category
            except ValueError:
                print("Invalid input. Please enter a number.")

    def reset_database(self):
        try:
            sql = """
                DROP TABLE IF EXISTS Recipes;
                DROP TABLE IF EXISTS Ingredients;
                DROP TABLE IF EXISTS Categories;
                
                CREATE TABLE Categories (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    name TEXT NOT NULL UNIQUE
                );

                CREATE TABLE Recipes (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    name TEXT UNIQUE,
                    category_id INTEGER,
                    FOREIGN KEY (category_id) REFERENCES Categories(id)
                );

                CREATE TABLE Ingredients (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    recipe_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    FOREIGN KEY (recipe_id) REFERENCES Recipes(id)
                );
            """
            super().execute_script(sql)

            with open('seed.csv', newline='', encoding='utf-8-sig') as categories_file:
                reader = csv.DictReader(categories_file)

                for row in reader:
                    super().get_cursor.execute("INSERT INTO Categories (name) VALUES (?);", (row['name'],))

            super().get_connection.commit()
            print("Database reset and populated with initial data from CSV.")
        except Exception as e:
            print("An error occurred while resetting the database.", e)
        finally:
            super().close_db()


class Project:
    def run(self):
        recipe_manager = Recipe()

        recipe_options = {
            "1": "Get all recipes",
            "2": "Get recipe by ID",
            "3": "Get recipe by category",
            "4": "Add a new recipe",
            "5": "Update a recipe",
            "6": "Delete a recipe",
            "reset": "Reset database",
            "exit": "Exit program"
        }

        print("Welcome to the Recipe Manager program, please choose a selection")

        user_selection = ""
        while user_selection != "exit":
            print("*** Option List ***")
            for option in recipe_options.items():
                print(option)

            user_selection = input("Select an option: ")

            if user_selection == "1":
                results = recipe_manager.fetch_recipes()
                for item in results:
                    print(item)
                input("Press return to continue")

            elif user_selection == "2":
                recipe_id = input("Enter recipe ID: ")
                result = recipe_manager.fetch_recipes(recipe_id)
                print(result)
                input("Press return to continue")


            elif user_selection == "3":
                category = recipe_manager.get_valid_category()
                result = recipe_manager.fetch_recipes_by_category(category)
                print(result)
                input("Press return to continue")

            elif user_selection == "4":
                name = input("Enter recipe name: ")
                category = recipe_manager.get_valid_category()
                ingredients = input("Enter ingredients (comma separated): ").split(',')
                ingredients = [ingredient.strip() for ingredient in ingredients]
                recipe_manager.add_recipe(name, category, ingredients)
                input("Press return to continue")

            elif user_selection == "5":
                recipe_id = input("Enter recipe ID: ")
                name = input("Enter new recipe name (leave blank to skip): ")
                category = recipe_manager.get_valid_category() if input("Update category? (y/n): ").lower() == "y" else None
                ingredients = input("Enter new ingredients (comma separated) (leave blank to skip): ")
                ingredients = [ingredient.strip() for ingredient in ingredients.split(',')] if ingredients else None
                recipe_manager.update_recipe(recipe_id, name if name else None, category if category else None, ingredients)
                input("Press return to continue")

            elif user_selection == "6":
                recipe_id = input("Enter recipe ID: ")
                recipe_manager.delete_recipe(recipe_id)
                input("Press return to continue")

            elif user_selection == "reset":
                confirm = input("This will delete all records in recipes and ingredients. Continue? (y/n): ").lower()
                if confirm == "y":
                    recipe_manager.reset_database()
                    input("Reset complete")
                else:
                    print("Reset aborted")
            else:
                if user_selection != "exit":
                    print("Invalid selection, please try again\n")


project = Project()
project.run()
