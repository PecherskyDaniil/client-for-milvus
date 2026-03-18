
from ..core.logger import get_logger
from ..core.validator import validator
from pymilvus import MilvusClient, DataType
import csv
import json
from ..models.modelFactory import ModelFactory
from ..models.schemaModel import SchemaModel
from ..models.tableModel import TableModel
from ..models.columnModel import ColumnModel
from ..models.valueModel import ValueModel
class VectorDBClient:
    """
    Клиент для Milvus. Не универсальный, чисто под наши задачи - одна коллекция, пока из функций только создание коллекции, вставка данных, поиск по тексту
    """
    __host:str=None # host Milvus
    __port:int=None #port Milvus
    __token:str=None #token Milvus если че меняем на username+password
    __client:MilvusClient=None #сам клиент
    vectorize_func=None #функция для векторизации, в нашем случае будет функция что шлет апи запрос в gpustack
    def __init__(self, host:str=None,port:int=None,token:str=None):
        self.host=host
        self.port=port
        self.token=token
        self.collection_name="metadata" #предопределено
        self.logger=get_logger("vector_db_client")
    
    @staticmethod
    def required_csv_columns():
        return ["schema","table","column","data_type","value","frequency","description"]
    @property
    def host(self)->str:
        return self.__host
    
    @host.setter
    def host(self,value:str):
        validator.validate_object_type(value,str)
        self.__host=value
    
    @property
    def port(self)->int:
        return self.__port
    
    @port.setter
    def port(self,value:int):
        validator.validate_object_type(value,int)
        self.__port=value
    
    @property
    def token(self)->str:
        return self.__token
    
    @token.setter
    def token(self,value:str):
        validator.validate_object_type(value,str)
        self.__token=value

    @property
    def client(self)->MilvusClient:
        return self.__client
    
    @client.setter
    def client(self,value:MilvusClient):
        validator.validate_object_type(value,MilvusClient)
        self.__client=value

    def connect(self):
        """
        Подключаемся к Milvus. Пока не подключимся ниче не сделаем
        """
        if self.host is None or self.token is None:
            self.logger.error("Error while connect to Milvus: Cant connect without host and token")
            raise Exception("Cant connect without host and token")
        
        uri=self.host
        if not(self.port is None):
            uri+=f":{self.port}"
        self.client = MilvusClient(
            uri=uri,
            token=self.token
        )
        self.logger.info("Successfuly connected to Milvus!")
        return True
    
    def init_metadata_collection(self):
        """
        Создаем коллекцию эту с мета (и не только) данными
        """
        if self.client is None:
            self.logger.error("Error while creating collection in Milvus: Cant init collection without connection to Milvus")
            raise Exception("Cant init collection without client")
        
        """
        Вся эта часть не мной придумана но мной дополнена. Добавил поле "схема" и сделал id - auto. Не нравится - меняем
        """
        schema = MilvusClient.create_schema(
            auto_id=True,
            description="Коллекция для хранения метаданных таблиц, колонок и значений"
        )

        # Добавляем поля
        schema.add_field(
            field_name="id",              # Уникальный идентификатор
            datatype=DataType.INT64,       # Целое число
            is_primary=True,               # Первичный ключ
            description="Уникальный ID записи"
        )

        schema.add_field(
            field_name="vector",           # Векторное представление сущности
            datatype=DataType.FLOAT_VECTOR, # Вектор из float чисел
            dim=1024,                       # Размерность для Qwen3-Embedding-0.6B
            description="Эмбеддинг текстового описания сущности"
        )

        schema.add_field(
            field_name="entity_type",      # Тип сущности
            datatype=DataType.VARCHAR,      # Строка
            max_length=20,                  # "table"/"column"/"value"
            description="Тип сущности: schema, table, column или value"
        )

        schema.add_field(
            field_name="schema_name",       # Название таблицы
            datatype=DataType.VARCHAR,
            max_length=256,
            description="Название схемы (для всех типов сущностей)"
        )

        schema.add_field(
            field_name="table_name",       # Название таблицы
            datatype=DataType.VARCHAR,
            max_length=256,
            description="Название таблицы (для всех типов сущностей кроме схемы)"
        )

        schema.add_field(
            field_name="column_name",       # Название поля (для колонок и значений)
            datatype=DataType.VARCHAR,
            max_length=256,
            description="Название поля (для колонок и значений, для таблиц и схем пусто)"
        )

        schema.add_field(
            field_name="value",            # Конкретное значение (для сущностей типа value)
            datatype=DataType.VARCHAR,
            max_length=512,
            description="Конкретное значение (только для entity_type='value', иначе пусто)"
        )

        schema.add_field(
            field_name="data_type",        # Тип данных (для колонок)
            datatype=DataType.VARCHAR,
            max_length=50,
            description="Тип данных: string/int/date/etc (для колонок)"
        )

        schema.add_field(
            field_name="description",      # Описание сущности
            datatype=DataType.VARCHAR,
            max_length=1024,
            description="Текстовое описание сущности (если есть)"
        )

        schema.add_field(
            field_name="frequency",        # Частота встречаемости (для значений)
            datatype=DataType.INT64,
            description="Как часто встречается значение (только для entity_type='value')"
        )

        self.client.drop_collection(
            collection_name= self.collection_name
        )
        # Создаем коллекцию
        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema
        )

        """
        тут могут быть ошибки в зависимости от версии библиотеки
        """
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="IVF_FLAT",
            metric_type="COSINE",
            params={"nlist": 1024}
        )

        self.client.create_index(
            collection_name= self.collection_name,
            index_params=index_params
        )
        self.logger.info("Successfuly created collection 'metadata' in Milvus!")
        return True

    @staticmethod        
    def _parse_table_row(row:dict):
        parsed_row={}
        for key,value in row.items():
            if isinstance(value,str) and value.strip()=='':
                parsed_row[key]=None
            else:
                parsed_row[key]=value
        return parsed_row
    
    def insert_data_in_milvus(self,data:list):
        """
        Вставляем данные прямо в Milvus. В каком виде? - читаем доки милвуса
        """
        res = self.client.insert(
            collection_name= self.collection_name,
            data=data
        )
        self.logger.info(f"Successfully inserted data in Milvus: {res}")
        return res

    def load_all_data_from_csv(self,path:str):
        """
        Загржаем данные в милвус прямо из файла. Структура файла - example_metadata.csv
        """
        data_for_milvus=[]
        data_models=[]
        with open(path) as csvfile:
            datareader=csv.DictReader(csvfile, delimiter=',', quotechar='\n')
            for row in datareader:
                parsed_row=VectorDBClient._parse_table_row(row)
                new_obj=ModelFactory.create_model_from_row(parsed_row)
                data_models.append(new_obj)
        to_vector_data=[obj.data_to_vector() for obj in data_models]
        vector_data=self.vectorize_func(to_vector_data)
        for ind,obj in enumerate(data_models):
            obj.vector=vector_data[ind]
            data_for_milvus.append(obj.to_dict())
        return self.insert_data_in_milvus(data_for_milvus)

    
    def load_all_data_from_json(self,path:str):
        """
        Загржаем данные в милвус прямо из файла. Структура файла - example_metadata.json
        """
        data_for_milvus=[]
        data_models=[]
        with open(path) as jsonfile:
            json_dict=json.load(jsonfile)
            try:
                for schema_json in json_dict["schemas"]:
                    schema_model_value=SchemaModel(id=None,
                                             vector=None,
                                             schema=schema_json["name"],
                                             description=schema_json["description"] if "description" in schema_json.keys() else None)
                    data_models.append(schema_model_value)
                    if "tables" in schema_json.keys():
                        for table_json in schema_json["tables"]:
                            table_model_value=TableModel(id=None,
                                                        vector=None,
                                                        schema=schema_json["name"],
                                                        table=table_json["name"],
                                                        description=table_json["description"] if "description" in table_json.keys() else None)
                            data_models.append(table_model_value)
                            if "columns" in table_json.keys():
                                for column_json in table_json["columns"]:
                                    column_model_value=ColumnModel(id=None,
                                                                    vector=None,
                                                                    schema=schema_json["name"],
                                                                    table=table_json["name"],
                                                                    column=column_json["name"],
                                                                    data_type=column_json["data_type"] if "data_type" in column_json.keys() else None,
                                                                    description=column_json["description"] if "description" in column_json.keys() else None)
                                    data_models.append(column_model_value)
                                    if "values" in column_json.keys():
                                        for value_json in column_json["values"]:
                                            value_model_value=ValueModel(id=None,
                                                                        vector=None,
                                                                        schema=schema_json["name"],
                                                                        table=table_json["name"],
                                                                        column=column_json["name"],
                                                                        data_type=column_json["data_type"] if "data_type" in column_json.keys() else None,
                                                                        value=value_json["value"],
                                                                        frequency=value_json["frequency"] if "frequency" in value_json.keys() else None,
                                                                        description=value_json["description"] if "description" in value_json.keys() else None)
                                            data_models.append(value_model_value)
            except:
                raise Exception("Все плохо")  
        to_vector_data=[obj.data_to_vector() for obj in data_models]
        vector_data=self.vectorize_func(to_vector_data)
        for ind,obj in enumerate(data_models):
            obj.vector=vector_data[ind]
            data_for_milvus.append(obj.to_dict())
        return self.insert_data_in_milvus(data_for_milvus)     
    

    def semantic_search_by_text(self,text:str):
        """
        Получаем результаты поиска по тексту
        """
        query_vectors=self.vectorize_func([text])
        self.client.load_collection(self.collection_name)
        res = self.client.search(
            collection_name= self.collection_name,  
            data=query_vectors, 
            limit=10, 
            output_fields=["schema_name","table_name","description"]
        )
        return res
            
            




