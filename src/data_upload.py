import services
import os

user_information = {
    "name" : "유성찬",
    "namespace" : "scryu32",
    "email": "scryu32@gmail.com",
    "age" : "18",
    "birthday": "2008-09-19",
    "location": "suwon",
}

assistant_model = services.AssistantModel(user_information, openai_api=os.environ.get('OPENAI_KEY'), log=True)

# vector_store.integrate_vector_upsert(input_data:list)
# 텍스트 바탕으로 벡터값 받아서 upsert까지 한번에 하는 함수. 텍스트는 리스트로받음
# ex) [{'id': 고유ID, 'message': 원본텍스트, 
#           'metadata': {'name': '이름', 'type': '무슨류(게임, 유튜버 등등)', 'characteristic': '특징'}}...]

# vector_store.delete_vector(['id1', 'id2'])
# 아이디로 검색해서 지우는거
data = []
print("데이터 업로드 규칙")
print("데이터 아이디는 한글쓰면안됨")
print("데이터 정보가 function인가요? (Y/N)")
data_where = input()
if data_where == "Y":
    vector_store = services.VectorStore(user_namespace='scryu32', pinecone_api=os.environ.get('PINECONE_KEY'), openai_api=os.environ.get('OPENAI_KEY'), function=True, log=True)
    mett = 'function'
if data_where == "N":
    vector_store = services.VectorStore(user_namespace='scryu32', pinecone_api=os.environ.get('PINECONE_KEY'), openai_api=os.environ.get('OPENAI_KEY'), function=False, log=True)
    mett = 'information'
while True:
    pc_id = input('데이터 아이디를 입력하세요(종료 입력시 종료):')
    if pc_id == '종료':
        break
    answer_of_q = input('정보에 대한 설명을 입력하세요:')
    message = input('정보를 입력하세요:')
    metadata = {}
    metadata[mett] = answer_of_q
    while True:
        metadata_key = input('metadata의 key를 입력하세요(종료 입력시 종료):')
        if metadata_key == '종료':
            break
        metadata_value = input('metadata의 value를 입력하세요:')
        metadata[metadata_key] = metadata_value
    data.append({'id': pc_id, 'message': message, 'metadata': metadata})

with open("ids.txt", "a", encoding="utf-8") as file:
    file.write("\n")
    for entry in data:
        file.write(entry['id'] + "\n")
print("아이디가 ids.txt 파일에 저장되었습니다.")

vector_store.integrate_vector_upsert(data)
print("Document Upsert Success.")
if data_where == "N":
    vector_store_function = services.VectorStore(user_namespace='scryu32', pinecone_api=os.environ.get('PINECONE_KEY'), openai_api=os.environ.get('OPENAI_KEY'), function=True, log=True)
    for item in data:
        item['metadata'].clear()
        item['metadata']['type'] = 'function'
        item['metadata']['function'] = 'Document_Search'

    vector_store_function.integrate_vector_upsert(data)



print("Success!")