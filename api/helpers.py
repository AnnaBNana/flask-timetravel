from api.exceptions import ResourceKeyInvalidError

def validate_record_id(id: str) -> int:
    print(id)
    try:
        int_id = int(id)
        assert int_id > 0
    except (ValueError, AssertionError) as e:
        raise ResourceKeyInvalidError from e
    
    return int_id