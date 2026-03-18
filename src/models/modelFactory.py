from .schemaModel import SchemaModel
from .tableModel import TableModel
from .columnModel import ColumnModel
from .valueModel import ValueModel

class ModelFactory:
    """
    Фабрика для моделей
    """
    @staticmethod
    def create_model_from_row(json_obj:dict):
        if json_obj["value"] is not None:
            result=ValueModel(id=None,
                              vector=None,
                              schema=json_obj["schema"],
                              table=json_obj["table"],
                              column=json_obj["column"],
                              value=json_obj["value"],
                              frequency=int(json_obj["frequency"]),
                              data_type=json_obj["data_type"],
                              description=json_obj["description"])
            return result
        elif json_obj["column"] is not None:
            result=ColumnModel(id=None,
                              vector=None,
                              schema=json_obj["schema"],
                              table=json_obj["table"],
                              column=json_obj["column"],
                              data_type=json_obj["data_type"],
                              description=json_obj["description"])
            return result
        elif json_obj["table"] is not None:
            result=TableModel(id=None,
                              vector=None,
                              schema=json_obj["schema"],
                              table=json_obj["table"],
                              description=json_obj["description"])
            return result
        elif json_obj["schema"] is not None:
            result=SchemaModel(id=None,
                              vector=None,
                              schema=json_obj["schema"],
                              description=json_obj["description"])
            return result
        else:
            raise Exception("Schema column is missing")
        