
from .schemaModel import SchemaModel
from ..core.validator import validator
class TableModel(SchemaModel):
    """
    Модель таблицы
    """
    __table=None
    def __init__(self,id:int=None,vector=None,schema:str=None,table:str=None,description:str=None):
        super().__init__(id,vector,schema,description)
        self.table=table
        self.entity_type="table"
    
    @property
    def table(self)->str:
        return self.__table
    
    @table.setter
    def table(self,value:str):
        validator.validate_object_type(value,str)
        self.__table=value
    
    def data_to_vector(self)->str:
        result=self.table
        if not(self.description is None):
            result+=f" {self.description}"
        return result
    
    def to_dict(self):
        result=super().to_dict()
        result["table_name"]=self.table
        return result
