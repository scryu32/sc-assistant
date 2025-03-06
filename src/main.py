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

vector_store = services.VectorStore(
    user_namespace='scryu32',
    pinecone_api=os.environ.get('PINECONE_KEY'),
    openai_api=os.environ.get('OPENAI_KEY'), 
    log=True
)
vector_store_function = services.VectorStore(
    user_namespace='scryu32', 
    pinecone_api=os.environ.get('PINECONE_KEY'), 
    openai_api=os.environ.get('OPENAI_KEY'), 
    function=True, 
    log=True
)
assistant_model = services.AssistantModel(
    user_information, 
    openai_api=os.environ.get('OPENAI_KEY'), 
    log=True
)
assistant_function = services.AssistantFunctions(
    openai_api=os.environ.get('OPENAI_KEY'),
    naver_id=os.environ.get('NAVER_CLIENT_ID'),
    naver_pw=os.environ.get('NAVER_CLIENT_PW'),
    log=True
)


messages = [{"role": "system", "content": "당신은 반말로 친근하게 대화하는 봇 호두입니다. 사용자 질문에 대한 Vector Store 상위 검색결과가 시스템 프롬프트로 전달됩니다. 대화와 관련없으면 대답에 이용하지 않는것이 좋습니다."}]


print("Sc-assistant에 오신것을 환영합니다! 봇 이름: 호두")
while True:
    user_input = input('[유성찬]')
    messages.append({"role": "user", "content": user_input})
    function = vector_store_function.integrate_vector_read(user_input, top_k=1, read_with_id=False)
    score = function['matches'][0]['score']
    print(f"\033[1m{score}\033[0m")
    #나중에는 스코어낮으면 웹서치, 높으면 document로 바꿔야함. 일상적인 대화를 모두 function_call에 등록하고 예외처리하면 될거같음
    if score > 0.84:
        function_call = function['matches'][0]['metadata']['function']
        print(function_call)
        if function_call == "Document_Search":
            vector_store_data = vector_store.integrate_vector_read(user_input, top_k=3, read_with_id=False)
            information = ["문서 상위 검색어:"] + [
                [
                    match["metadata"]["name"],
                    match["metadata"]["information"],
                    match["metadata"]["text"]
                ]
                for match in vector_store_data["matches"]
            ]
        else:
            query = assistant_function.set_query(user_input)
            res = assistant_function.search_web(user_input)
            
            information = "웹서치 결과:"
            information += res
        messages.append({"role": "system", "content": f"{information}"})
    assistant_response = ""
    for part in assistant_model.stream_chat(messages):
        print(part, end='', flush=True)
        assistant_response += part
    print()
    messages.append({"role": "assistant", "content": assistant_response})

