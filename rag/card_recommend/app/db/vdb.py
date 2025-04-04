import weaviate
import weaviate.classes as wvc
from weaviate.classes.init import AdditionalConfig, Timeout
from weaviate.classes.config import Reconfigure
from weaviate.classes.query import MetadataQuery
from weaviate.exceptions import BackupFailedException
from weaviate.classes.config import (
    Configure, Property, DataType, VectorDistances, VectorFilterStrategy, Tokenization
    )

from weaviate.exceptions import UnexpectedStatusCodeError
from weaviate.util import generate_uuid5
import functools


class VDB:
    def __init__(self, host, port, grpc_port):
        self.host = host
        self.port = port
        self.grpc_port = grpc_port

    def client_connect(self):
        client = weaviate.connect_to_local(
            self.host,
            port=self.port,
            grpc_port=self.grpc_port,
            additional_config=AdditionalConfig(
                timeout=Timeout(init=30, query=60, insert=120)
                )
        )
        if client.is_ready():
            pass
        return client
    

    def _connect_and_close(func):
        """
        메서드 호출 전후로 client를 연결하고 종료하는 데코레이터.
        """
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            client = self.client_connect()  # 호출 전: client 연결
            try:
                # 원래의 메서드(create_collection 등)에게 client를 넘겨줌
                return func(self, client, *args, **kwargs)
            finally:
                # 호출 후: client 종료
                client.close()
        return wrapper
    
    @_connect_and_close
    def create_collection(self, client, collection_name: str, properties):
        """
            링크: https://weaviate.io/developers/weaviate/manage-data/collections
            Collection을 생성할 때 다양한 config를 설정하여 생성한다.
            properties
            vector_index_config: vector화 한 데이터들을 어떤 방식으로 찾을지 설정
            vectorizer_config: text2vec 모델 설정 (property마다 따로 적용가능)
            reranker_config: reranker 모델 설정
            generative_config: LLM 모델 설정 (openai, )
            sharding_config: distributed, memory 관련 설정
            multi_tenancy_config: 멀티 테넌시 관련 설정
        Args:
            collection_name
            properties
        """
        try:
            client.collections.create(
            collection_name,
            properties=properties,
            vector_index_config=Configure.VectorIndex.hnsw(
                    quantizer=Configure.VectorIndex.Quantizer.bq(),
                    ef_construction=300,
                    distance_metric=VectorDistances.COSINE,
                    filter_strategy=VectorFilterStrategy.SWEEPING 
                )
            )
        except UnexpectedStatusCodeError as e:
            print("Error:", e)

    @_connect_and_close
    def update_collection_config(self, client, collection_name):
        """
            Collection의 config를 수정할 때 사용
            # NOTE 어떤 값으로 수정할지 추가 개발 필요
        """
        collection = client.collections.get(collection_name)

        collection.config.update(
            generative_config=Reconfigure.Generative.cohere()  # Sample
        )

    @_connect_and_close
    def get_collection(self, client, collection_name):
        coll = client.collections.get(collection_name)
        return coll


    @_connect_and_close
    def read_all_collection(self, client):
        response = client.collections.list_all(simple=False)
        return response


    @_connect_and_close
    def delete_collection(self, client, collection_name):
        client.collections.delete(collection_name)


    @_connect_and_close
    def insert_data(self, client, collection_name: str, data: dict, vector=None, uuid=None):
        """
            data 에 맞춰서 vector 값이나 uuid를 넣어준다. collection에 vector config 넣어준 key만 적용가능
            ex)
            data = {
                "name": "test",
                "path": "/path"
            }
            vector = {
                "name": [0.123] * 64
            }
            uuid_in = generate_uuid5(data)
            uuid_out = vdb.insert_data('Test', data, vector)
        """
        collection = client.collections.get(collection_name)

        uuid = collection.data.insert(
            properties=data,
            vector=vector,
            uuid=uuid
            )
        return uuid
    

    @_connect_and_close
    def read_data(self, client, collection_name, id, include_vector=True):
        collection = client.collections.get(collection_name)
        data_object = collection.query.fetch_object_by_id(
            id,
            include_vector=include_vector,
            )
        return data_object

    
    @_connect_and_close
    def read_all_data(self, client, collection_name, number):
        result = []
        collection = client.collections.get(collection_name)
        for idx, item in enumerate(collection.iterator()):
            if idx == number:
                break
            result.append(item)
        return result

    
    @_connect_and_close
    def check_existed_data(self, client, collection_name, data):
        object_uuid = generate_uuid5(data)
        collection = client.collections.get(collection_name)
        author_exists = collection.data.exists(object_uuid)
        return author_exists


    # Search #
    @_connect_and_close
    def query_with_bm25(self, client, collection_name, query, limit, query_properties=None):
        collection = client.collections.get(collection_name)
        response = collection.query.bm25(
            query=query,
            query_properties=query_properties,
            limit=limit
        )
        return response

    @_connect_and_close
    def query_with_near_text(self, client, collection_name, query, limit, vector=None):
        collection = client.collections.get(collection_name)
        if vector is not None:
            response = collection.query.near_vector(
                near_vector=vector,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )
        else:
            response = collection.query.near_text(
                query=query,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )
        return response


    @_connect_and_close
    def retrieve_with_text(self, client, text_embed, target):
        if target == 'text':
            collection = client.collections.get("Text_DB")
        elif target == 'image':
            collection = client.collections.get("Image_DB")

        response = collection.query.near_vector(
            near_vector=text_embed.detach().cpu().numpy()[0],
            limit=2,
            return_metadata=wvc.query.MetadataQuery(distance=True)
        )

        print(response)
        return response
    
    @_connect_and_close
    def retrieve_with_image(self, client, image_embed, target):
        if target == 'text':
            collection = client.collections.get("Text_DB")
        elif target == 'image':
            collection = client.collections.get("Image_DB")

        response = collection.query.near_vector(
            near_vector=image_embed.detach().cpu().numpy()[0],
            limit=2,
            return_metadata=wvc.query.MetadataQuery(distance=True)
        )
        return response
    
    @_connect_and_close
    def retrieve_with_both(self, client, text_embed, image_embed, target):
        if target == 'text':
            collection = client.collections.get("Text_DB")
        elif target == 'image':
            collection = client.collections.get("Image_DB")

        response = collection.query.near_vector(
            near_vector=text_embed.detach().cpu().numpy()[0],
            limit=2,
            return_metadata=wvc.query.MetadataQuery(distance=True)
        )
        return response
    


if __name__ == "__main__":
    vdb = VDB(
        host="192.168.74.167", # Use a string to specify the host
        port=8080,
        grpc_port=50051,
    )
    collection_name = "Test"
    properties = [
        Property(
            name="title", 
            data_type=DataType.TEXT,
            vectorize_property_name=True,  # Use "title" as part of the value to vectorize
            tokenization=Tokenization.LOWERCASE
            ),
        Property(name="body", data_type=DataType.TEXT),
    ]
    vdb.create_collection(collection_name, properties)
    response = vdb.read_all_collection()
    print(response.keys()) # ex: response.keys = ['Text_DB', 'JeopardyQuestion', 'Test', 'TestArticle', 'Image_DB']
    