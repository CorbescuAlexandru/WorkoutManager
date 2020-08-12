import requests
import json
import wget
import re
import toml

cfg = toml.load("payload.toml")

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
        self.weights = requests.get(API.url_weight, headers=self.headers)
        self.exercises = [] # list on dictionaries that contains all the information about a exercice
        self.links = [] # list on dictionaries that contains all the links between a workout and a schedule
        self.urls = []
        self.comments = [] # list of dictionaries that cointains all the comments about exercises

    def check_post(self, url, data):
        """
        Cheks if the last post was correct
        """
    
        test = requests.get(url, headers = self.headers)
        if data[-1] in test.json():
            return True
        return False

    def extract_csrf(self, url):
        """ 
        Extracts the csrf token from a url 
        """

        with requests.Session() as client:
            client.get(url) 
            csrf = client.cookies['csrftoken']
        return csrf

    def login(self):
        """ 
        Logs in into the main page of the API
        """
        
        # Get the csrf token from the main URL
        csrf = self.extract_csrf(API.url_login)
        
        # Construnct the payload
        payload = cfg['payload']['login'][0]
        payload['csrfmiddlewaretoken'] = csrf

        # Login request       
        requests.post(API.url_login, payload, headers={'Referer' : API.url_login})
    
    def add_weight(self):
        """ 
        Adds a new weight; params needed for post request's payload 
        """

        # Get the csrf token
        csrf = self.extract_csrf('https://wger.de/en/weight/add/')
        # Adding referer to the headers
        self.headers['Referer'] =  API.url_weight

        # Take the weight entires from TOML file
        entries = cfg.get('payload', {}).get('weight')
        # Check for valid entires
        if entries:
            for payload in entries:
                # Add csrf token to payload
                payload['csrfmiddlewaretoken'] = csrf
                # Adding weight request
                weight = requests.post(API.url_weight, data = payload,  headers = self.headers, timeout = 2)
                # Savinf info
                self.weights.append(weight.json())
                # Checking post request
                if self.check_post(API.url_plan, self.weights) == False:
                    print("Weight no " + str(entries.index(payload)) + " couldn't be added")
                    self.weights.remove(weight.json())
        
        # Eliminates the referer from the headers
        self.headers.pop('Referer')

    def add_plan(self):
        """ 
        Adds a new nutrition plan and stores information about it in the class dictionary
        Params needed for post request's payload 
        """

        # Take the weight entries from TOML file
        entries = cfg.get('payload', {}).get('plan')
        # Check for valid entries
        if entries :
            # Construct payload 
            for payload in entries:
                # Adding nutrition plan request
                plan = requests.post(API.url_plan, data = payload, headers = self.headers, timeout = 2)
                # Savinf info
                self.plans.append(plan.json())
                # Checking post request
                if self.check_post(API.url_plan, self.plans) == False:
                    print("Plan no " + str(entries.index(payload)) + " couldn't be added")
                    self.plans.remove(plan.json())

    def add_meal(self):
        """ 
        Adds a new meal to a nutrition plan and stores information about it in the class dictionary
        Params needed for post request's payload 
        """
        
        # Take the meal entires from TOML file
        entries = cfg.get('payload',{}).get('meal')
        # Check for valid entires
        if entries:
            # Construct payload 
            for payload in entries:
                payload['plan'] = self.plans[0]['id']
                # Adding meal request
                meal = requests.post(API.url_meal, data = payload, headers = self.headers, timeout = 2)
                # Saving info
                self.meals.append(meal.json())
                # Checking post request
                if self.check_post(API.url_meal, self.meals) == False:
                    print("Meal no " + str(entries.index(payload)) + " couldn't be added")
                    self.meals.remove(meal.json())

    def add_item(self):
        """ 
        Adds a new item to a meal and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : meal_id(str), amount(str), ingredient(str) 
        """

        # Take the weight entires from TOML file
        entries = cfg.get('payload', {}).get('item')
        # Check for valid entires
        if entries:
            # Construct payload 
            for payload in entries:
                payload['meal'] = self.meals[0]['id']
                # Adding item request
                item = requests.post(API.url_items, data = payload, headers = self.headers, timeout = 2)
                # Saving info
                self.items.append(item.json())
                # Checking post request
                if self.check_post(API.url_items, self.items) == False:
                    print("Item no " + str(entries.index(payload)) + " couldn't be added")
                    self.items.remove(item.json())
    
    def add_exercise(self):
        """ 
        Adds a new exercise and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : description(str, min 50 charaters), name(str), category(str, 0-9) language(str, 2= English)
        """

        # Take the exercise entires from TOML file
        entries = cfg.get("payload",{}).get("exercise")
        # Check for valid entires
        if entries:
            # Construct payload 
            for payload in entries:
                # Adding item exercise
                exercise = requests.post(API.url_exercise, data = payload, headers = self.headers, timeout = 2)
                # Saving info
                self.exercises.append(exercise.json())
                # Checking post request
                if self.check_post(API.url_exercise, self.exercises) == False:
                    print("Exercise no " + str(entries.index(payload)) + " couldn't be added")
                    self.exercises.remove(exercise.json())
        
    def add_workout(self):
        """ 
        Adds a new workout and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : creation_date (str YYYY-MM-DD)
        """

        # Take the workout entires from TOML file
        entries = cfg.get('payload',{}).get('workout')
        # Check for valid entires
        if entries :
            # Construct payload 
            for payload in entries:
                # Adding a workout request
                workout = requests.post(API.url_workout, data = payload, headers = self.headers, timeout = 2)
                # Saving info
                self.workouts.append(workout.json())
                # Checking post request
                if self.check_post(API.url_workout, self.workouts) == False:
                    print("Workout no " + str(entries.index(payload)) + " couldn't be added")
                    self.workouts.remove(workout.json())
    
    def add_day(self):
        """ 
        Adds a new day to a workout and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : workout_id (str), description (str), training (str), day (str)
        """

        # Take the weight entries from TOML file
        entries = cfg.get('payload',{}).get('day')
        # Check for valid entries
        if entries:
            # Construct payload 
            for payload in entries:
                payload['training'] = self.workouts[0]['id']
                # Adding a day request
                day = requests.post(API.url_day, data = payload, headers = self.headers, timeout = 2)
                # Saving info
                self.days.append(day.json())
                # Checking post request
                if self.check_post(API.url_day, self.days) == False:
                    print("Day no " + str(entries.index(payload)) + " couldn't be added")
                    self.days.remove(day.json())

    def add_sets(self):
        """ 
        Adds a new set of a exercise to a day and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : day_id (str), exercice (str), sets (str)
        """

        # Take the weight entires from TOML file
        entries = cfg.get('payload',{}).get('sets')
        # Check for valid entires
        if entries:
            # Construct payload 
            for payload in entries:
                payload['exerciseday'] = self.days[0]['id']
                # Adding a sets request
                sets = requests.post(API.url_sets, data = payload, headers = self.headers, timeout = 2)
                # Saving info
                self.sets.append(sets.json())
                # Checking post request
                if self.check_post(API.url_sets, self.sets) == False:
                    print("Set no " + str(entries.index(payload)) + " couldn't be added")
                    self.sets.remove(sets.json())

    def add_schedule(self):
        """ 
        Adds a new schedule and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : name (str), start_date (str YYYY-MM-DD)
        """

        # Take the schedule entires from TOML file
        entries = cfg.get('payload',{}).get('schedule')
        # Check for valid entires
        if entries:
            # Construct payload 
            for payload in entries:
                # Adding a schedule request
                schedule = requests.post(API.url_schl, data = payload, headers = self.headers, timeout = 2)
                # Saving info
                self.schedules.append(schedule.json())
                # Checking post request
                if self.check_post(API.url_schl, self.schedules) == False:
                    print("Schedule no " + str(entries.index(payload)) + " couldn't be added")
                    self.schedules.remove(schedule.json())

    def link(self):
        """ 
        Links a wokrout with a schedule
        Params needed for post request's payload 
        Params : schedule_id (str), workout_id (str YYYY-MM-DD)
        """

        # Take the link entires from TOML file
        entries = cfg.get('payload',{}).get('link')
        # Check for valid entires
        if entries:
            # Construct payload 
            for payload in entries:
                payload['schedule'] = self.schedules[0]['id']
                payload['workout'] = self.workouts[0]['id']
                # Adding a link request
                link = requests.post(API.url_link, data = payload, headers = self.headers, timeout = 2)
                # Saving info
                self.links.append(link.json())
                # Checking post request
                if self.check_post(API.url_link, self.links) == False:
                    print("link no " + str(entries.index(payload)) + " couldn't be added")
                    self.links.remove(link.json())


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

        # Get workout's id
        workout_id = self.workouts[index]['id']
        # Delete request
        deleted = requests.delete(API.url_workout + str(workout_id), headers = self.headers)
        # Checking post request
        if self.check_post(API.url_workout, self.workouts) == True:
            print("Workout no " + str(index) + " couldn't be deleted")


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

    user = API(cfg['payload']['login'][0]['username'], cfg['payload']['login'][0]['password'])

    user.cleanup()
