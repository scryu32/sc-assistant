import services
import os

user_information = {
    "name" : "유성찬",
    "namespace" : "scryu32",
    "email": "scryu32@gmail.com",
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

messages = [{"role": "system", "content": "당신은 반말로 친근하게 대화하는 봇 호두입니다."}]


print("Sc-assistant에 오신것을 환영합니다! 봇 이름: 호두")
while True:
    user_input = input('[유성찬]')
    messages.append({"role": "user", "content": user_input})
    # vector_store_data : vector_store.integrate_vector_read(input_data:str, top_k:int=3, read_with_id=False)
    # messages.append({"role": "system", "content": vector_store_data})
    for part in assistant_model.stream_chat(messages):
        print(part, end='', flush=True)
    print()