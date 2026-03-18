
from .abstractModel import AbstractModel
from ..core.validator import validator
class SchemaModel(AbstractModel):
    """
    Модель схемы
    """
    __schema:str=None
    def __init__(self,id:int=None,vector=None,schema:str=None,description:str=None):
        super().__init__(id,vector,description)
        self.schema=schema
        self.entity_type="schema"
    
    @property
    def schema(self)->str:
        return self.__schema
    
    @schema.setter
    def schema(self,value:str):
        validator.validate_object_type(value,str)
        self.__schema=value
    
    def data_to_vector(self)->str:
        result=self.schema
        if not(self.description is None):
            result+=f" {self.description}"
        return result
    
    def to_dict(self):
        result=super().to_dict()
        result["schema_name"]=self.schema
        return result
