import json
from jsonschema import validate

def check_entry(**kwargs):
        """
            Tests a possible entry with a json schema
        """
        
        schema = json.load(open(kwargs['path']))
        validate(instance=kwargs['test'], schema=schema)