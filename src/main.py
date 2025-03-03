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

vector_store = services.VectorStore(user_namespace='rsc', pinecone_api=os.environ.get('PINECONE_KEY'), openai_api=os.environ.get('OPENAI_KEY'), host="https://sc-assistant-awfhoou.svc.aped-4627-b74a.pinecone.io", log=True)
assistant_model = services.AssistantModel(user_information, openai_api=os.environ.get('OPENAI_KEY'), log=True)

messages = [{"role": "system", "content": "당신은 반말로 친근하게 대화하는 봇 호두입니다. 사용자 질문에 대한 Vector Store 상위 검색결과가 시스템 프롬프트로 전달됩니다. 대화와 관련없으면 대답에 이용하지 않는것이 좋습니다."}]


print("Sc-assistant에 오신것을 환영합니다! 봇 이름: 호두")
print("데이터 업로드모드는 Data를 입력해서 실행해주세요.")
while True:
    user_input = input('[유성찬]')
    if user_input == 'Data':
        break
    messages.append({"role": "user", "content": user_input})
    vector_store_data = vector_store.integrate_vector_read(user_input, top_k=3, read_with_id=False)
    information_list = [match["metadata"]["information"] for match in vector_store_data["matches"]]
    messages.append({"role": "system", "content": f"{information_list}"})
    assistant_response = ""
    for part in assistant_model.stream_chat(messages):
        print(part, end='', flush=True)
        assistant_response += part
    print()
    messages.pop(-1)
    messages.append({"role": "assistant", "content": assistant_response})



# vector_store.integrate_vector_upsert(input_data:list)
# 텍스트 바탕으로 벡터값 받아서 upsert까지 한번에 하는 함수. 텍스트는 리스트로받음
# ex) [{'id': 고유ID, 'message': 원본텍스트, 
#           'metadata': {'name': '이름', 'type': '무슨류(게임, 유튜버 등등)', 'characteristic': '특징'}}...]

# vector_store.delete_vector(['id1', 'id2'])
# 아이디로 검색해서 지우는거
data = []
while True:
    print("데이터 업로드 규칙")
    print("데이터 아이디는 한글쓰면안됨")
    print("질문에 대한 답은 최대한 다양한 정보 가지는게 좋음")
    pc_id = input('데이터 아이디를 입력하세요(종료 입력시 종료):')
    if pc_id == '종료':
        break
    message = input('질문을 입력하세요:')
    metadata = {}
    answer_of_q = input('질문에 대한 답을 입력하세요:')
    metadata['information'] = answer_of_q
    while True:
        metadata_key = input('metadata의 key를 입력하세요(종료 입력시 종료):')
        if metadata_key == '종료':
            break
        metadata_value = input('metadata의 value를 입력하세요:')
        metadata[metadata_key] = metadata_value
    data.append({'id': pc_id, 'message': message, 'metadata': metadata})

vector_store.integrate_vector_upsert(data)
print("Success!")