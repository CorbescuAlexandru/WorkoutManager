import requests
import json
from wget import download
from re import findall
from toml import load
from jsonschema import validate

cfg = load("payload.toml")

"""
ToDo:
    functionalitate separata ca sa verifice toml pt username si password

    json schema => testeaza daca toml are toti parametrii doriti

"""

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
        self.weights = requests.get(API.url_weight, headers=self.headers).json()
        self.exercises = requests.get(API.url_exercise, headers=self.headers).json() # list on dictionaries that contains all the information about a exercice
        self.links = requests.get(API.url_link, headers=self.headers).json() # list on dictionaries that contains all the links between a workout and a schedule
        self.comments = [] # list of dictionaries that cointains all the comments about exercises

    def construct_payload(self, **kwargs):
        """
            Construct the payload for the current operation
        """
        
        payload = kwargs['parse']
        excude = kwargs['dele']
        payload.pop(excude, None)
        return payload

    def check_entry(self, **kwargs):
        """
            Tests a possible entry with a json schema
        """
        
        schema = json.load(open('C:/Users/ACorbescu/Desktop/workout/2.0.0/workout.json'))
        validate(instance=kwargs['test'], schema=schema)

    def check_post(self, url, info):
        """
        Cheks if the last post was correct
        """
    
        test = requests.get(url, headers = self.headers).json()
        if info == test:
            return True
        return False
    
    def add_post(self, payload, url, info):
        """
        Generic function that launches a post request based on the params given
        After the post request, it calls check_post function  
        """

        check = requests.post(url, data = payload, headers = self.headers, timeout = 2)
        app = check.json()
        info.append(app)
        if check.ok == True:
            # Checking post request
            if self.check_post(url, info) == False:
                print("Couldn't add " + str(payload) + " properly")
                info.pop()
            else:
                return True

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

        # Test the entry with it's json schema
        self.check_entry(path='schemas/login.json', test=payload)

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
                # Test the entry with it's json schema
                self.check_entry(path='schemas/weight.json', test=payload)
                # Post request
                self.add_post(payload, API.url_weight, self.weights)
        
        # Eliminates the referer from the headers
        self.headers.pop('Referer')

    def add_plan(self):
        """ 
        Adds a new nutrition plan and stores information about it in the class dictionary
        Params needed for post request's payload 
        """

        # Take the weight entries from TOML file
        plans = cfg.get('payload', {}).get('plan')
        # Check for valid entries
        if plans :
            # Construct payload 
            for payload in plans:
                # Parse the payload
                ready = self.construct_payload(parse = payload, dele='meal')
                # Check the entry vs a json schema
                self.check_entry(path='schemas/plan.json', test=ready)
                # Post request
                self.add_post(ready, API.url_plan, self.plans)
                

    def add_meal(self):
        """ 
        Adds a new meal to a nutrition plan and stores information about it in the class dictionary
        Params needed for post request's payload 
        """
        
        # Take the plans entires from TOML file
        plans = cfg.get('payload',{}).get('plan')
        # For each meal in each plan
        for entries in plans:
            # Check for valid entires
            if entries:
                for payload in entries.get('meal',{}):
                    # Parse the payload
                    ready = self.construct_payload(parse = payload, dele='item')
                    # Check the entry vs a json schema
                    self.check_entry(path='schemas/meal.json', test=ready)
                    # Post request
                    self.add_post(ready, API.url_meal, self.meals)

    def add_item(self):
        """ 
        Adds a new item to a meal and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : meal_id(str), amount(str), ingredient(str) 
        """

        # Take the meals entires from TOML file
        meals = cfg.get('payload',{}).get('plan',{})[0].get('meal',{})
        for entries in meals:
            # Check for valid entires
            if entries:
                # Construct payload 
                for payload in entries.get('item',{}):
                    # Check the entry vs a json schema
                    self.check_entry(path='schemas/item.json', test=payload)
                    # Post request
                    self.add_post(payload, API.url_items, self.items)
    
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
                # Check the entry vs a json schema
                self.check_entry(path='schemas/exercise.json', test=payload)
                # Post request
                requests.post(API.url_exercise, data = payload, headers = self.headers, timeout = 2)
        
    def add_workout(self, toml):
        """ 
        Adds a new workout and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : creation_date (str YYYY-MM-DD)
        """

        cfg = load(toml)

        # Take the workout entires from TOML file
        workouts = cfg.get('payload',{}).get('workout')
        # Check for valid entires
        if workouts :
            # Construct payload 
            for payload in workouts:
                # Parse the workout payload
                ready = self.construct_payload(parse=payload, dele='day')
                # Check the entry vs a json schema
                self.check_entry(path='schemas/workout.json', test=ready)
                # Post request
                return self.add_post(ready, API.url_workout, self.workouts)
    
    def add_day(self):
        """ 
        Adds a new day to a workout and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : workout_id (str), description (str), training (str), day (str)
        """

        # Take the weight entries from TOML file
        workouts = cfg.get('payload',{}).get('workout')
        # Check for valid entries
        if workouts:
            for entries in workouts:
                if entries:
                    # Construct payload 
                    for payload in entries.get('day',{}):
                        # Parse the day payload
                        ready = self.construct_payload(parse = payload, dele='sets')
                        # Check the entry vs a json schema
                        self.check_entry(path='schemas/day.json', test=ready)
                        # Post request
                        self.add_post(ready, API.url_day, self.days)

    def add_sets(self):
        """ 
        Adds a new set of a exercise to a day and stores information about it in the class dictionary
        Params needed for post request's payload 
        Params : day_id (str), exercice (str), sets (str)
        """

        # Take the weight entires from TOML file
        days = cfg.get('payload',{}).get('workout',{})[0].get('day',{})
        # Check for valid entires
        if days:
            for entires in days:
                # Construct payload 
                for payload in entires.get('sets',{}):
                    # Check the entry vs a json schema
                    self.check_entry(path='schemas/set.json', test=payload)
                    # Post request
                    self.add_post(payload, API.url_sets, self.sets)

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
                # Parse schedule payload
                ready = self.construct_payload(parse = payload, dele = 'link')
                # Check the entry vs a json schema
                self.check_entry(path='schemas/schedule.json', test=ready)
                # Post request
                self.add_post(ready, API.url_schl, self.schedules)

    def link(self):
        """ 
        Links a wokrout with a schedule
        Params needed for post request's payload 
        Params : schedule_id (str), workout_id (str YYYY-MM-DD)
        """

        # Take the link entires from TOML file
        schedules = cfg.get('payload',{}).get('schedule')
        # Check for valid entires
        if schedules:
            for entries in schedules:
                # Construct payload 
                for payload in entries.get('link'):
                    # Check the entry vs a json schema
                    self.check_entry(path='schemas/link.json', test=payload)
                    # Post request
                    self.add_post(payload, API.url_link, self.links)


    def get_image(self, index):
        """
        Download the image of a exercice by index
        """
        
        # Get request to get all the links for all exercises
        image = requests.get(API.url_image, headers = self.headers).json()
        filename  = download(image[index]['image'])


    def get_comment(self, index):
        """
        Gets the comment from a exercice by index
        """

        # Get request to get all the comments for all exercises
        comments = requests.get(API.url_comment, headers = self.headers).json()
        # Parse the response
        for my_comment in comments:
            if my_comment['id'] == index:
                print(my_comment['comment'])

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

    def delete_field(self, url, data):
        """
        Deletes all the entries from a field in the class
        """
        
        for field in data:
            if 'id' in field:
                requests.delete(url + str(field['id']), headers=self.headers)
        data.clear()

    def cleanup(self):
        """ 
        Calls the delete_field function for the main fields in the class
        """

        delete_this = [(API.url_plan, self.plans), (API.url_workout, self.workouts), (API.url_schl, self.schedules), (API.url_link, self.links)]
        for delete in delete_this:
            self.delete_field(delete[0], delete[1])


if __name__ == "__main__":

    user = API(cfg['payload']['login'][0]['username'], cfg['payload']['login'][0]['password'])

    user.add_workout("payload.toml")
    