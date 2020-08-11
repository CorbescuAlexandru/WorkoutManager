import requests
import json
import wget
import re

class API:
    
    url_login   = 'https://wger.de/en/user/login'
    url_weight  = 'https://wger.de/api/v2/weightentry/'
    url_plan = 'https://wger.de/api/v2/nutritionplan/'
    url_items = 'https://wger.de/api/v2/mealitem/'
    url_meal = 'https://wger.de/api/v2/meal/'
    url_exercise = 'https://wger.de/api/v2/exercise/'
    url_workout = 'https://wger.de/api/v2/workout/'
    url_day = 'https://wger.de/api/v2/day/'
    url_sets = 'https://wger.de/api/v2/set/'
    url_schl = 'https://wger.de/api/v2/schedule/'
    url_link = 'https://wger.de/api/v2/schedulestep/'
    url_image = 'https://wger.de/api/v2/exerciseimage/'
    url_comment = 'https://wger.de/api/v2/exercisecomment/'

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.login()
        self.headers = {'Authorization': 'Token 14aa12cc4bbdd0a016cee1fb36ce3e15b4dc3587'}
        self.plans = requests.get(API.url_plan, headers = self.headers).json() # list on dictionaries that contains all the information about a plan
        self.meals = requests.get(API.url_meal, headers = self.headers).json() # list on dictionaries that contains all the information about a meal
        self.items = requests.get(API.url_items, headers = self.headers).json() # list on dictionaries that contains all the information about a item
        self.workouts = requests.get(API.url_workout, headers = self.headers).json() # list on dictionaries that contains all the information about a workout
        self.days = requests.get(API.url_day, headers = self.headers).json() # list on dictionaries that contains all the information about a day of a workout
        self.sets = requests.get(API.url_sets, headers = self.headers).json() # list on dictionaries that contains all the information about a exercise of a certain day
        self.schedules = requests.get(API.url_schl, headers = self.headers).json() # list on dictionaries that contains all the information about a schedule
        self.exercises = [] # list on dictionaries that contains all the information about a exercice
        self.links = [] # list on dictionaries that contains all the links between a workout and a schedule
        self.urls = []
        self.comments = [] # list of dictionaries that cointains all the comments about exercises

    def extract_csrf(self, url):
        """ 
        Extracts the csrf token from a url 
        """

        with requests.Session() as client:
            client.get(url) 
            csrf = client.cookies['csrftoken']
        return csrf
    
    def construct_payload(self, **kwargs):
        """ 
        Constructs custom paylods from given arguments 
        """

        payload = {}
        for key,value in kwargs.items():
            payload[key] = value
        return payload

    def login(self):
        """ 
        Logs in into the main page of the API
        """
        
        # Get the csrf token from the main URL
        csrf = self.extract_csrf(API.url_login)
        
        # Construnct the payload
        payload = self.construct_payload(username = self.username, password = self.password, csrfmiddlewaretoken = csrf)

        # Login request       
        requests.post(API.url_login, payload, headers={'Referer' : API.url_login})
    
    def add_weight(self, date, weight):
        """ 
        Adds a new weight; params needed for post request's payload 
        """
        
        # Check if given params are suitable
        if type(date) != str or type(weight) != str:
            print("Params need to be strings")
            exit(1)

        # Used for request result check
        ante = requests.get(API.url_weight, headers=self.headers)
        # Calls the login functions
        self.login()
        # Get the csrf token
        csrf = self.extract_csrf('https://wger.de/en/weight/add/')
        # Construnct the payload
        payload = self.construct_payload(date = date, weight = weight, csrfmiddlewaretoken = csrf)
        # Adding referer to the headers
        self.headers['Referer'] =  API.url_weight
        # Adding weight request
        weight = requests.post(API.url_weight, data = payload,  headers = self.headers, timeout = 2)
        # Eliminates the referer from the headers
        self.headers.pop('Referer')

        # Check for succes
        post = requests.get(API.url_weight, headers=self.headers)
        if post.text != ante.text and weight.ok == True:
            print("Weight added succeded")
        else:
            print("Weight added failed")

    def add_plan(self, description, goal):
        """ 
        Adds a new nutrition plan and stores information about it in the class dictionary
        Params needed for post request's payload 
        """
        
        # Check if given params are suitable
        if type(description) != str or type(goal) != str:
            print("Params need to be strings")
            exit(1)

        # Used for request result check
        ante = requests.get(API.url_plan, headers=self.headers)
        # Construct payload 
        payload = self.construct_payload(description = description, has_goal_calories = goal)
        # Adding nutrition plan request
        plan = requests.post(API.url_plan, data = payload, headers = self.headers, timeout = 2)
        
        # Check for succes
        post = requests.get(API.url_plan, headers=self.headers)
        if post.text != ante.text and plan.ok == True:
            print("Plan added succeded")
            # Adding information in the list
            self.plans.append(plan.json())
        else:
            print("Plan added failed")

    def add_meal(self, plan_id):
        """ 
        Adds a new meal to a nutrition plan and stores information about it in the class dictionary
        Params needed for post request's payload 
        """

        # Check if the parameter given is suitable
        if type(plan_id) != str:
            print("Parameter need to be strings")
            exit(1)
        
        # Used for request result check
        ante = requests.get(API.url_meal, headers=self.headers)
        # Construct payload
        payload = self.construct_payload(plan = plan_id)
        # Adding meal request
        meal = requests.post(API.url_meal, data = payload, headers = self.headers, timeout = 2)

        # Check for succes
        post = requests.get(API.url_meal, headers=self.headers)
        if post.text != ante.text and meal.ok == True:
            print("Meal added succeded")
            # Adding information in the list
            self.meals.append(meal.json())
        else:
            print("Meal added failed")

    def add_item(self, meal_id, amount, ingredient):
        """ 
        Adds a new item to a meal and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : meal_id(str), amount(str), ingredient(str) 
        """
        
        # Check if the parameter given is suitable
        if type(meal_id) != str or type(amount) != str or type(ingredient) != str:
            print("Parameter need to be strings")
            exit(1)

        # Used for request result check
        ante = requests.get(API.url_items, headers=self.headers)
        # Construnct payload
        payload = self.construct_payload(meal = meal_id, amount = amount, ingredient = ingredient)
        # Adding a item request
        item = requests.post(API.url_items, data = payload, headers = self.headers, timeout = 2)

        # Check for succes
        post = requests.get(API.url_items, headers=self.headers)
        if post.text != ante.text and item.ok == True:
            print("Item added succeded")
            # Add information in the list
            self.items.append(item.json())
        else:
            print("Item added failed")
    
    def add_exercise(self, description, name, category, language):
        """ 
        Adds a new exercise and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : description(str, min 50 charaters), name(str), category(str, 0-9) language(str, 2= English)
        """

        # Check if the parameter given is suitable
        if type(description) != str or type(name) != str or type(category) != str or type(language) != str:
            print("Parameter need to be strings")
            exit(1)
        
        # Used for request result check
        ante = requests.get(API.url_exercise, headers=self.headers)
        # Construct payload for request
        payload = self.construct_payload(description = description, name = name, category = category, language = language)
        # Adding a exercise request
        exercise = requests.post(API.url_exercise, data = payload, headers = self.headers, timeout = 2)

        # Check for succes
        post = requests.get(API.url_exercise, headers=self.headers)
        if post.text != ante.text and exercise.ok == True:
            print("Exercise added succeded")
            # Add information in the list
            self.exercises.append(exercise.json())
        else:
            print("Exercise added failed")
        
    def add_workout(self, creation_date):
        """ 
        Adds a new workout and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : creation_date (str YYYY-MM-DD)
        """

        # Check if the parameter given is suitable
        if type(creation_date) != str :
            print("Parameter need to be strings")
            exit(1)

        # Used for request result check
        ante = requests.get(API.url_workout, headers=self.headers)
        #Construnctpayload for request
        payload = self.construct_payload(creation_date = creation_date)
        # Adding a workout request
        workout = requests.post(API.url_workout, data = payload, headers = self.headers, timeout = 2)

        # Check for succes
        post = requests.get(API.url_workout, headers=self.headers)
        if post.text != ante.text and workout.ok == True:
            print("Workout added succeded")
            # Add information in the list
            self.workouts.append(workout.json())
        else:
            print("Workout added failed")
    
    def add_day(self, workout_id, description, training, day):
        """ 
        Adds a new day to a workout and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : workout_id (str), description (str), training (str), day (str)
        """
        # Check if the parameter given is suitable
        if type(workout_id) != str or type(description) != str or type(training) != str or type(day) != str:
            print("Parameter need to be strings")
            exit(1)

        # Used for request result check
        ante = requests.get(API.url_day, headers=self.headers)
        #Construnctpayload for request
        payload = self.construct_payload(workout_id = workout_id, description = description, training = training, day = day)
        # Adding a day to the workout request
        day = requests.post(API.url_day, data = payload, headers = self.headers, timeout = 2)
        
        # Check for succes
        post = requests.get(API.url_day, headers=self.headers)
        if post.text != ante.text and day.ok == True:
            print("Day added succeded")
            # Add information in the list
            self.days.append(day.json())
        else:
            print("Day added failed")

    def add_sets(self, exerciseday, exercice, sets):
        """ 
        Adds a new set of a exercise to a day and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : day_id (str), exercice (str), sets (str)
        """

        # Check if the parameter given is suitable
        if type(exerciseday) != str or type(exercice) != str or type(sets) != str :
            print("Parameter need to be strings")
            exit(1)
        
        # Used for request result check
        ante = requests.get(API.url_sets, headers=self.headers)
        #Construnctpayload for request
        payload = self.construct_payload(exerciseday = exerciseday, exercises = exercice, sets = sets)
        # Adding a set to a day request
        sets = requests.post(API.url_sets, data = payload, headers = self.headers, timeout = 2)
        
        # Check for succes
        post = requests.get(API.url_sets, headers=self.headers)
        if post.text != ante.text and sets.ok == True:
            print("Set added succeded")
            # Add information in the list
            self.sets.append(sets.json())
        else:
            print("Set added failed")

    def add_schedule(self, name, start_date):
        """ 
        Adds a new schedule and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : name (str), start_date (str YYYY-MM-DD)
        """

        # Check if the parameter given is suitable
        if type(name) != str or type(start_date) != str :
            print("Parameter need to be strings")
            exit(1)

        # Used for request result check
        ante = requests.get(API.url_schl, headers=self.headers)
        #Construnctpayload for request
        payload = self.construct_payload(name = name, start_date = start_date)
        # Adding a workout
        schedule = requests.post(API.url_schl, data = payload, headers = self.headers, timeout = 2)

        # Check for succes
        post = requests.get(API.url_schl, headers=self.headers)
        if post.text != ante.text and schedule.ok == True:
            print("Set added succeded")
            # Add information in the list
            self.schedules.append(schedule.json())
        else:
            print("Set added failed")

    def link(self, schedule_id, workout_id):
        """ 
        Links a wokrout with a schedule
        Params needed for post request's payload 
        Params : schedule_id (str), workout_id (str YYYY-MM-DD)
        """

        # Check if the parameter given is suitable
        if type(schedule_id) != str or type(workout_id) != str :
            print("Parameter need to be strings")
            exit(1)

        # Used for request result check
        ante = requests.get(API.url_link, headers=self.headers)
        # Construnctpayload for request
        payload = self.construct_payload(schedule = schedule_id, workout = workout_id)
        # Linking request
        link = requests.post(API.url_link, data = payload, headers = self.headers, timeout = 2)

        # Check for succes
        post = requests.get(API.url_link, headers=self.headers)
        if post.text != ante.text and link.ok == True:
            print("Link added succeded")
        else:
            print("Link added failed")


    def get_image(self, index):
        """
        Download the image of a exercice by index
        """
        
        # Get request to get all the links for all exercises
        image = requests.get(API.url_image, headers = self.headers)
        # Parse the links
        self.urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', image.text)
        # Download and save the image
        filename  = wget.download(self.urls[index-1])

    def get_comment(self, index):
        """
        Gets the comment from a exercice by index
        """

        # Get request to get all the comments for all exercises
        comment = requests.get(API.url_comment, headers = self.headers)
        
        # Parse the response
        aux = re.sub(",\"exercise" , "comment", comment.text)
        self.comments = re.split('comment":', aux)
        for i in self.comments:
            if '{' in i:
                self.comments.remove(i)
        
        # Print the comment
        print(self.comments[index])

    def delete_workout(self, index):
        """
        Deletes a workout fom the workouts list
        """

        # Used for request result check
        ante = requests.get(API.url_workout, headers=self.headers)
        # Get workout's id
        workout_id = self.workouts[index]['id']
        # Delete request
        deleted = requests.delete(API.url_workout + workout_id, headers = self.headers)

        # Check for succes
        post = requests.get(API.url_workout, headers=self.headers)
        if post.text == ante.text and deleted.ok == True:
            print("Deleted workout was a succes")
        else:
            print("Deleted workout was a succes failed")

    def cleanup(self):
        """ 
        Deletes all main entries
        (If a nutrition plan is deleted all the meals associated with it are deleted as well)
        (This goes for all the main entries with their sub entires)
        """

        for i in self.plans:
            if 'id' in i:
                requests.delete(API.url_plan + str(i['id']), headers = self.headers)
        self.plans.clear()
        for i in self.workouts:
            if 'id' in i:
                requests.delete(API.url_workout + str(i['id']), headers = self.headers)
        self.workouts.clear()
        for i in self.schedules:
            if 'id' in i:
                requests.delete(API.url_schl + str(i['id']), headers = self.headers)
        self.schedules.clear()
        for i in self.links:
            if 'id' in i:
                requests.delete(API.url_link + str(i['id']), headers = self.headers)
        self.links.clear()

        

if __name__ == "__main__":

    user = API('test+++', 'Test123;')