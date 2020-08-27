import json
import jsonschema

def check_entry(**kwargs):
    schema = json.load(open(kwargs['path']))
    try:
        jsonschema.validate(instance=kwargs['test'], schema=schema)
    except jsonschema.ValidationError as e:
        if e.schema:
            #print(e.schema.errors)
            return False
