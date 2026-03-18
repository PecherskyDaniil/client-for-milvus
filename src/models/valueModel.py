
from .columnModel import ColumnModel
from ..core.validator import validator
class ValueModel(ColumnModel):
    """
    Модель значения
    """
    __value:str=None
    __frequency:int=None
    def __init__(self,id:int=None,vector=None,schema:str=None,table:str=None,column:str=None,value:str=None,frequency:int=None,data_type:str=None,description:str=None):
        super().__init__(id,vector,schema,table,column,data_type,description)
        self.value=value
        self.frequency=frequency
        self.entity_type="value"
    
    @property
    def value(self)->str:
        return self.__value
    
    @value.setter
    def value(self,value:str):
        validator.validate_object_type(value,str)
        self.__value=value

    @property
    def frequency(self)->int:
        return self.__frequency
    
    @frequency.setter
    def frequency(self,value:int):
        validator.validate_object_type(value,int)
        self.__frequency=value
    
    def data_to_vector(self)->str:
        result=self.value
        if not(self.description is None):
            result+=f" {self.description}"
        return result
    
    def to_dict(self):
        result=super().to_dict()
        result["value"]=self.value
        result["frequency"]=self.frequency
        return result