
from ..core.validator import validator
class AbstractModel:
    """
    Абстрактная модель
    """
    __id:int=None
    __vector=None
    __entity_type:str=None
    __description:str=None
    def __init__(self,id:int=None,vector=None,description:str=""):
        self.id=id
        self.vector=vector
        self.entity_type="abstract"
        self.description=description
    @property
    def id(self)->int:
        return self.__id
    
    @id.setter
    def id(self,value:int):
        validator.validate_object_type(value,int)
        self.__id=value    
    

    @property
    def entity_type(self)->int:
        return self.__entity_type
    
    @entity_type.setter
    def entity_type(self,value:int):
        validator.validate_object_type(value,str)
        self.__entity_type=value 

    @property
    def vector(self):
        return self.__vector
    
    @vector.setter
    def vector(self,value:str):
        self.__vector=value   

    @property
    def description(self)->str:
        return self.__description
    
    @description.setter
    def description(self,value:str):
        validator.validate_object_type(value,str)
        self.__description=value

    def data_to_vector(self)->str:
        pass

    def to_dict(self)->dict:
        result={}
        result["vector"]=self.vector
        result["entity_type"]=self.entity_type
        result["schema_name"]=""  # Милвус
        result["table_name"]=""   # None
        result["column_name"]=""  # не
        result["value"]=""        # воспринимает
        result["data_type"]=""    # возвращаем
        result["frequency"]=0     # пустые строки
        result["description"]=self.description if self.description!=None else ""
        return result