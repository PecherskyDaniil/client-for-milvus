
from .tableModel import TableModel
from ..core.validator import validator
class ColumnModel(TableModel):
    """
    Модель колонки
    """
    __column:str=None
    __data_type:str=None
    def __init__(self,id:int=None,vector=None,schema:str=None,table:str=None,column:str=None,data_type:str=None,description:str=None):
        super().__init__(id,vector,schema,table,description)
        self.column=column
        self.data_type=data_type
        self.entity_type="column"
    
    @property
    def column(self)->str:
        return self.__column
    
    @column.setter
    def column(self,value:str):
        validator.validate_object_type(value,str)
        self.__column=value

    @property
    def data_type(self)->str:
        return self.__data_type
    
    @data_type.setter
    def data_type(self,value:str):
        validator.validate_object_type(value,str)
        self.__data_type=value
    
    def data_to_vector(self)->str:
        result=self.column
        if not(self.description is None):
            result+=f" {self.description}"
        return result
    
    def to_dict(self):
        result=super().to_dict()
        result["column_name"]=self.column
        result["data_type"]=self.data_type
        return result