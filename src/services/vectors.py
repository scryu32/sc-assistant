from openai import OpenAI
from pinecone.grpc import PineconeGRPC as Pinecone
from .logger import log_decorator

# 실질적으로 갖다쓰는함수들

# integrate_vector_upsert(input_data:list)
# 텍스트 바탕으로 벡터값 받아서 upsert까지 한번에 하는 함수. 텍스트는 리스트로받음
# ex) [{'id': 고유ID, 'message': 원본텍스트, 
#           'metadata': {'name': '이름', 'type': '무슨류(게임, 유튜버 등등)', 'characteristic': '특징'}}...]

# integrate_vector_read(input_data:str, top_k:int=3, read_with_id=False)
# input_data는 검색할 내용, top_k는 상위 몇개, read_with_id는 id로 검색

# delete_vector(['id1', 'id2'])
# 아이디로 검색해서 지우는거
class VectorStore:
    # user_namespace는 유저이름임. 데이터베이스에서 어떤 유저가 올린 벡터인지 구분하기위한 내용
    # user_namespace를 유저이름말고 유저의 UUID로 하는게 가장 안전할듯 
    # 나중에 Function calling 추가하면 host는 인자로 안받고 index 두개만들어줘야함
    def __init__(self, user_namespace, pinecone_api, openai_api, function = False, log=False):
        self.log = log
        self.client = OpenAI(api_key=openai_api)
        self.pc = Pinecone(api_key=pinecone_api)
        if function:
            self.index = self.pc.Index(host="https://function-awfhoou.svc.aped-4627-b74a.pinecone.io")
        else:
            self.index = self.pc.Index(host="https://document-awfhoou.svc.aped-4627-b74a.pinecone.io")
        self.namespace = user_namespace

    # 로깅
    # 객체에 접근하면 언제든 실행되는 함수임
    def __getattribute__(self, name):
        if name == "read_vector":
            return object.__getattribute__(self, name)
        if name == "integrate_vector_read":
            return object.__getattribute__(self, name)
        if name == "get_vector":
            return object.__getattribute__(self, name)
        log_enabled = object.__getattribute__(self, "log")
        attr = object.__getattribute__(self, name)
        if not log_enabled or not callable(attr) or name.startswith("__"):
            return attr
        if hasattr(attr, "__wrapped__"):
            return attr
        decorated = log_decorator(attr)
        object.__setattr__(self, name, decorated)
        return decorated
    
    # openai ada002한테 Vector 받아오기
    def get_vector(self, input_message:str):
        response = self.client.embeddings.create(
            input=input_message,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding

    # Pinecone에 Vector Upsert하기
    #  데이터셋 구조: [{"id": 고유ID, 'values': vector, "metadata": {"text": 원본텍스트, "distinction": 그외 특징}}...]
    #  id는 아스키 코드 변환이 가능해야하므로 영어로 작성해야함.
    def upsert_vector(self, data_sets:list):
        self.index.upsert(
            vectors=data_sets,
            namespace=self.namespace
        )
        return "Upsert Success."
        
    # Pinecone에 Vector 검색하기
    # top_k는 상위 몇개만 출력할건지 묻는것
    # 리턴 데이터 구조 {'matches': [{'id': 고유ID,'metadata': {...},'score': 0.8600222 (0.85 이상이면 보통 잘나왔음)
    #  ,'sparse_values': {'indices': [], 'values': []},'values': []}...], 'namespace': namespace,'usage': {'read_units': top_k}}
    def read_vector(self, vector:list, top_k:int):
        results = self.index.query(
            namespace=self.namespace,
            vector=vector,
            top_k=top_k,
            include_values=False,
            include_metadata=True
        )
        return results
    
    # id로 검색하는방법
    def read_vector_with_id(self, input_id:str, top_k:int):
        results = self.index.query(
            namespace=self.namespace,
            id=input_id,
            top_k=top_k,
            include_values=False
        )
        return results

    # 텍스트 바탕으로 벡터값 받아서 upsert까지 한번에 하는 함수. 텍스트는 리스트로받음
    # ex) [{'id': 고유ID, 'message': 원본텍스트, 
    #    'metadata': {'name': '이름', 'type': '무슨류(게임, 유튜버 등등)', 'characteristic': '특징'}}...]
    def integrate_vector_upsert(self, input_data:list):
        vector_data = []
        for d in input_data:
            vector = self.get_vector(d['message'])
            metadata = {"text": d['message']}
            metadata.update(d['metadata'])
            data = {'id': d['id'], 'values': vector, 'metadata': metadata}
            vector_data.append(data)
        return self.upsert_vector(vector_data)
    
    # read_with_id 키면 id로 검색
    def integrate_vector_read(self, input_data:str, top_k:int=3, read_with_id=False):
        if read_with_id:
            return self.read_vector_with_id(input_data, top_k)
        vector = self.get_vector(input_data)
        return self.read_vector(vector, top_k)
    
    # 아이디로 정보 검색해서 지우는 함수
    # 아이디 리스트임
    def delete_vector(self, input_id:list):
        self.index.delete(ids=input_id, namespace=self.namespace)
        return 'Delete success'

