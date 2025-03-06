import urllib.request
import json
from pytrends.request import TrendReq
from openai import OpenAI
from .logger import log_decorator


class AssistantFunctions:
    def __init__(self, openai_api, naver_id, naver_pw, log=False):
        self.client = OpenAI(api_key=openai_api)
        self.naver_client_id = naver_id
        self.naver_client_secret = naver_pw
        self.log = log

    def __getattribute__(self, name):
        log_enabled = object.__getattribute__(self, "log")
        attr = object.__getattribute__(self, name)
        if not log_enabled or not callable(attr) or name.startswith("__"):
            return attr
        if hasattr(attr, "__wrapped__"):
            return attr
        decorated = log_decorator(attr)
        object.__setattr__(self, name, decorated)
        return decorated

    #search_web 함수는 네이버 검색 엔진을 활용한 검색엔진으로, type 부분에 webkr, news, doc 등이 들어갈수있으며, query는 검색할 단어임.
    #리턴할때 겁나큰 json파일 들어감.
    def search_web(self, query: str, type='webkr'):
        encText = urllib.parse.quote(query)
        url = f"https://openapi.naver.com/v1/search/{type}?query=" + encText 
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id",self.naver_client_id)
        request.add_header("X-Naver-Client-Secret",self.naver_client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if(rescode==200):
            response_body = response.read()
            parsed_data = json.loads(response_body.decode('utf-8'))
            content = parsed_data["items"]
            temp_mss = [{"role": "system", "content": f"당신은 여러가지 기사들을 짧게 요약하는 봇입니다. 검색 단어는 {query}이고, 다양한 기사 혹은 웹 문서 제목과 짧은 내용, 링크가 주어질것입니다. 그 내용을 3줄 이내로 요약하고 필요한 링크를 남기세요."}, {"role": "user", "content": f'{content}'}]
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=temp_mss,
                temperature=0.7,
                max_tokens=1600,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            return completion.choices[0].message.content
        else:
            return rescode
        
    def set_query(self, user_input: str):
        temp_mss = [{"role": "system", "content": f"사용자가 말한 내용에서 웹서치할 내용을 한문장으로 바꾸세요. \n ex) user: 한국전력 주가를 알려줘 \n assistant: 한국전력 주가"}, {"role": "user", "content": f'{user_input}'}]
        completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=temp_mss,
                temperature=0.7,
                max_tokens=1600,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
        return completion.choices[0].message.content
        
    
    #실시간 트랜드 뽑아내는거, US, japan, south_korea 등의 파라미터 들어갈수있음
    #리턴값은 문자열임
    def crawl_google_trends_rss(self, location='south_korea'):
        pytrends = TrendReq(hl='ko-KR', tz=540)
        trend_search = pytrends.trending_searches(pn=location)
        trend_search = str(trend_search)
        return trend_search
    

    
