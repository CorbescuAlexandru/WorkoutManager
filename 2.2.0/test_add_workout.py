import pytest
import wkm
import random

# sterge workout apoi day-ul lui
# volume testing limita mai mica

@pytest.mark.parametrize("toml, output",
                        [
                            ("payloads/wk_with_all_params.toml", True), # With all params
                            ("payloads/wk_with_minim_params.toml", True), # With minim params
                            ("payloads/wk_with_missing_params.toml", True), # With missing params
                            ("payloads/wk_with_invalid_params.toml", False), # With invalid params
                        ]
                        )
def test_add_workout(toml, output):
    """
    1. Create schema for TOML file
    2. Create payload with all valid params
    3. Launch post request
    4. Check API response
    """
    user = wkm.API("test+++","Test123;", toml)
    assert user.add_workout() == output
    assert user.curent_sesion_cleanup() == True

@pytest.mark.parametrize("toml, output",
                        [
                            ("payloads/subclaes_all_params.toml", True), # With days all params
                            ("payloads/subclaes_minim_params.toml", True), # With days minim params
                            ("payloads/subclaes_missing_params.toml", False), # With days missing params
                            ("payloads/subclaes_invalid_params.toml", False), # With days invalid params
                            ("payloads/all_subclaes_all_params.toml", True), # With days and sets all params
                            ("payloads/all_subclaes_minim_params.toml", True), # With days and sets minim params
                            ("payloads/all_subclaes_missing_params.toml", False), # With days and sets missing params
                            ("payloads/all_subclaes_invalid_params.toml", False), # With days and sets invalid params
                        ]
                        )
def test_add_workout_with_subclases(toml, output):
    """
    1. Create payload with missing params
    2. Launch post request
    3. Check API response
    """
    user = wkm.API("test+++","Test123;", toml)
    assert user.add_workout() == output
    assert user.curent_sesion_cleanup() == True

@pytest.mark.parametrize("toml, output",
                        [
                            ("payloads/wk_with_all_params.toml", True), # With all params
                            ("payloads/wk_with_minim_params.toml", True), # With minim params
                            ("payloads/wk_with_missing_params.toml", True), # With missing params
                            ("payloads/wk_with_invalid_params.toml", False), # With invalid params
                        ]
                        )
def test_add_workout_duplicate(toml, output):
    """
    1. Create schema for TOML file
    2. Create payload with all valid params
    3. Launch post request
    4. Check API response
    """
    user = wkm.API("test+++","Test123;", toml)
    assert user.add_workout() == output
    assert user.curent_sesion_cleanup() == True


@pytest.mark.parametrize("toml, output",
                        [
                            ("payloads/subclaes_all_params.toml", True), # With days all params
                            ("payloads/subclaes_minim_params.toml", True), # With days minim params
                            ("payloads/subclaes_missing_params.toml", False), # With days missing params
                            ("payloads/subclaes_invalid_params.toml", False), # With days invalid params
                            ("payloads/all_subclaes_all_params.toml", True), # With days and sets all params
                            ("payloads/all_subclaes_minim_params.toml", True), # With days and sets minim params
                            ("payloads/all_subclaes_missing_params.toml", False), # With days and sets missing params
                            ("payloads/all_subclaes_invalid_params.toml", False), # With days and sets invalid params
                        ]
                        )
def test_add_workout_duplicate_with_subclases(toml, output):
    """
    1. Create schema for TOML file
    2. Create payload with all valid params
    3. Launch post request
    4. Check API response
    """
    user = wkm.API("test+++","Test123;", toml)
    assert user.add_workout() == output
    assert user.curent_sesion_cleanup() == True


@pytest.mark.parametrize("toml",
                        [
                            ("payloads/all_subclaes_all_params.toml"), # With days and sets all params
                            ("payloads/all_subclaes_minim_params.toml"), # With days and sets minim params
                        ]
                        )
def test_invalid_deletes(toml):
    """
        1. Create a workout with subclasses
        2. Delete the workout
        3. Delete it's subclasses
    """
    
    for i in range (1,5):
        user = wkm.API("test+++","Test123;", toml)
        assert user.add_workout() == True
        assert user.delete_entry(user.workouts[-1]['id'], wkm.API.url_workout, user.workouts) == True
        assert user.delete_entry(user.days[-1]['id'], wkm.API.url_day, user.days) == False
        assert user.delete_entry(user.sets[-1]['id'], wkm.API.url_sets, user.sets)  == False

    for i in range (1,5):
        user = wkm.API("test+++","Test123;", toml)
        assert user.add_workout() == True
        assert user.add_day(user.workouts[-1]['id']) == True
        assert user.delete_entry(user.days[-1]['id'], wkm.API.url_day, user.days) == True
        assert user.delete_entry(user.sets[-1]['id'], wkm.API.url_sets, user.sets)  == False

    user.curent_sesion_cleanup()

@pytest.mark.parametrize("toml",
                        [
                            ("payload.toml") # With days and sets all params
                        ]
                        )
def test_volume(toml):
    """
        1. Create a workout with subclasses
        2. Delete the workout
        3. Delete it's subclasses
    """
    userX = wkm.API("test+++","Test123;", "payload.toml")
    x = True
    while x:
        x = userX.add_workout()
    
    user = wkm.API("test+++","Test123;", toml)
    assert user.add_workout() == False


    '''
    assert user.add_plan() == True
    x = True
    while x:
        x = user.add_plan()
    assert user.add_plan() == False
    
    
    user.delete_field(wkm.API.url_meal, user.meals)
    print(user.add_meal(user.plans[-1]['id']))

    print(user.meals)

    
    assert user.add_meal(user.plans[-1]['id']) == True
    x = True
    while x:
        x = user.add_meal(user.plans[-1]['id'])
    assert user.add_meal(user.plans[-1]['id']) == False
    
    user.delete_field(wkm.API.url_items, user.items)
    assert user.add_item(user.meals[-1]['id']) == True
    x = True
    while x:
        x = user.add_item(user.meals[-1]['id'])
    assert user.add_item(user.meals[-1]['id']) == False


    assert user.add_schedule() == True
    assert user.add_day(user.workouts[-1]['id']) == True
    assert user.add_sets(user.days[-1]['id']) == True
    '''
    user.curent_sesion_cleanup()
    userX.curent_sesion_cleanup()

def test_delete_workout():
    """
       1. Launch delete request
       2. Check API response
    """
    user = wkm.API("test+++", "Test123;", "payload.toml")

    for i in range(0,5):
        user.add_workout()
        assert user.delete_entry(user.workouts[-1]['id'], wkm.API.url_workout, user.workouts) == True

    for i in range(0,5):
        k = True
        while k:
            x = random.randrange(999999)
            k = False
            for lookup in user.workouts:
                if x == lookup['id']:
                    k = True
        assert user.delete_entry(x, wkm.API.url_workout, user.workouts) == False
