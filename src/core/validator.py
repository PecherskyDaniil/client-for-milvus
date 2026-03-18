
from enum import Enum
class validator():

    @staticmethod
    def validate_object_type(instance:any,dtype:any):
        if instance is None:
            return
        if not isinstance(instance,dtype):
            if dtype.__bases__[0]==Enum and instance in [member.value for member in dtype]:
                return
            raise Exception(f"Wrong object data type. Expected {dtype}, but received {type(instance)}.")
    
    @staticmethod
    def required_keys(keys:list,obj:dict):
        for key in keys:
            if not(key in obj.keys()):
                raise Exception(f"Object doesnt have key {key}")