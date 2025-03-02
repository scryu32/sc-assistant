import services
import os

user_information = {
    "name" : "유성찬",
    "namespace" : "scryu32",
    "email": "scryu32@gmail.com",
    #밑에 싹다 벡터db에 들어갈거임 ㅅㄱ
    "age" : "18",
    "birthday": "2008-09-19",
    "location": "suwon",
    "like_things": "게임 원신을 즐겨하고, 음식은 치킨과 연어를 좋아함. 좋아하는 연예인은 호시마치 스이세이로, 홀로라이브의 버츄얼 유튜버이자 아이돌임.",
    "hate_things": "가식적인 내용을 싫어하며, 절대적인 혐오를 싫어함.",
    "live_pattern": "평소에 9시~10시 기상하며 13시부터 22시까지 스터디 카페와 학원을 감. 집에선 원신과 코딩, 숙제를 하고 1~2시에 잠.",
    "personality": "어떠한 문제를 집요하게 파고들어 탐구하고자하는 성격이 강함.",
    "hobby": "한국에서 개최하는 서울 코믹월드 등 서브컬쳐 축제에 방문하는것을 좋아함. 서브컬쳐 문화에 관심이 많음.",
    "interested": "최근 AI연구와 개발에 흥미가 많으며, 경제와 주식에도 큰 관심을 가짐.",
    "tmi": "대평고등학교에 고등학생 2학년 9반에 재학중이며, 수학과 과학을 잘함."
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