import pytest
import wkm
import glob, os
from toml import load

user = None
tomls = None

def setup_module(module):
    global user 
    user = wkm.API("test+++","Test123;")
    global tomls 
    tomls = []
    os.chdir("C:/Users/ACorbescu/Desktop/workout/2.0.0/tomls")
    for file in glob.glob("*.toml"):
        tomls.append(file)


def test_post_workout():
    for workout in tomls:
        assert user.add_workout(workout) == True