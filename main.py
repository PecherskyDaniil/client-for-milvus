from src.milvus.vectorDBClient import VectorDBClient
import os
#os.environ['HF_ENDPOINT']

"""

ЭТА ЧАСТЬ НЕ НУЖНА С ВЕКТОРИЗАЦИЕЙ, ВСЕ ЭТО ЗАМЕНИТ ЭМБЕДЕР QWEN
"""
from sklearn.feature_extraction.text import TfidfVectorizer

# Глобальная переменная для хранения векторизатора
_VECTORIZER = None
_VECTORIZER_PARAMS = None

def vectorize_texts_smart(texts, max_features=50, force_retrain=False):
    """
    Умная векторизация с автоматическим сохранением состояния
    
    Args:
        texts: список текстов или строка
        max_features: максимальное количество признаков
        force_retrain: принудительно переобучить модель
    
    Returns:
        numpy array: векторы текстов
    """
    global _VECTORIZER, _VECTORIZER_PARAMS
    
    # Преобразуем строку в список
    if isinstance(texts, str):
        texts = [texts]
    
    current_params = {'max_features': max_features}
    
    # Если нужно переобучить или векторизатор еще не создан
    if force_retrain or _VECTORIZER is None or _VECTORIZER_PARAMS != current_params:
        print("🔄 Обучение нового векторизатора...")
        _VECTORIZER = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2)
        )
        vectors = _VECTORIZER.fit_transform(texts)
        _VECTORIZER_PARAMS = current_params
        print(f"✅ Векторизатор обучен. Размерность: {vectors.shape[1]}")
    else:
        print("🔄 Использование сохраненного векторизатора...")
        vectors = _VECTORIZER.transform(texts)
    
    return vectors.toarray()

def get_vectorizer_info():
    """Информация о текущем векторизаторе"""
    global _VECTORIZER, _VECTORIZER_PARAMS
    
    if _VECTORIZER is None:
        return "Векторизатор еще не обучен"
    
    return {
        'параметры': _VECTORIZER_PARAMS,
        'размер словаря': len(_VECTORIZER.vocabulary_) if _VECTORIZER.vocabulary_ else 0,
        'обучен': True
    }

def clear_vectorizer():
    """Очистка сохраненного векторизатора"""
    global _VECTORIZER, _VECTORIZER_PARAMS
    _VECTORIZER = None
    _VECTORIZER_PARAMS = None
    print("🔄 Векторизатор очищен")
"""
ЭТА ЧАСТЬ НЕ НУЖНА С ВЕКТОРИЗАЦИЕЙ, ВСЕ ЭТО ЗАМЕНИТ ЭМБЕДЕР QWEN
"""



"""
Пример работы клиента MILVUS. Если подключение к файлу просто не указывайте порт, а в хост - путь к файлу. Не сработает - меняйте в коде клиента (функция connect)
"""
newVDBClient=VectorDBClient("http://localhost",19530,"root:Milvus")
newVDBClient.vectorize_func=vectorize_texts_smart
newVDBClient.connect()
newVDBClient.init_metadata_collection()
newVDBClient.load_all_data_from_csv("./metadata_example.csv")
#newVDBClient.load_all_data_from_json("./metadata_example.json")

print(newVDBClient.semantic_search_by_text("Товар"))
