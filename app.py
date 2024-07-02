import streamlit as st
from langchain_core.messages.chat import ChatMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_joungna.prompts import load_prompt
from dotenv import load_dotenv
from langchain import hub
from langchain.prompts import PromptTemplate

# API KEY 정보로드
load_dotenv()

st.title("EngHan 챗GPT💬")


# 처음 1번만 실행하기 위한 코드
if "messages" not in st.session_state:
    # 대화기록을 저장하기 위한 용도로 생성한다.
    st.session_state["messages"] = []

# 사이드바 생성
with st.sidebar:
    # 초기화 버튼 생성
    clear_btn = st.button("대화 초기화")

    selected_prompt = st.selectbox(
        "번역모드를 선택해 주세요", ("영어번역모드", "잉한번역모드","중국어모드", "일본어모드"), index=0
    )


# 이전 대화를 출력
def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


# 새로운 메시지를 추가
def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


# 체인 생성
def create_chain(prompt_type):
    # prompt | llm | output_parser
    # 프롬프트(기본모드)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "당신은 뛰어난 AI 영어와 한글번역가입니다. 다음의 영어 또는 한글문장을 한글 또는 영어로 번역해 주세요. 또한 영어문장에서 5개 단어를 무작위로 선정하여 한글 뜻을 적어주세요 그리고 반대 뜻의 영어 단어를 적어주세요. ",
            ),
            ("user", "#Question:\n{question}"),
        ]
    )
    if prompt_type == "잉한번역모드":
        # Windows 사용자 only: 인코딩을 cp949로 설정
        prompt = load_prompt("prompts/sns.yaml", encoding="utf-8")
    if prompt_type == "중국어모드":
        # 직접 프롬프트 템플릿 정의
        map_template = """당신은 뛰어난 AI 중국어와 영어와 한글번역가입니다.  다음의 문서에서
        {question}
        영어 또는 한글문장에서 5개 단어를 무작위로 선정하여 한글 또는 영어로 그리고 동시에 중국어로도 번역해 주세요. 그리고 중국어 발음은 한글 자음모음으로 적어주세요:"""

        # 템플릿을 사용하여 프롬프트 생성
        prompt = PromptTemplate.from_template(map_template)
    elif prompt_type == "일본어모드":
        # 직접 프롬프트 템플릿 정의
        map_template = """당신은 뛰어난 AI 일본어와 영어와 한글번역가입니다.  다음의 문서에서
        {question}
        영어 또는 한글문장에서 5개 단어를 무작위로 선정하여 한글 또는 영어로 그리고 동시에 일본어로도 번역해 주세요. 그리고 일본어 발음은 한글 자음모음으로 적어주세요:"""

        # 템플릿을 사용하여 프롬프트 생성
        prompt = PromptTemplate.from_template(map_template)

    # GPT
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

    # 출력 파서
    output_parser = StrOutputParser()

    # 체인 생성
    chain = prompt | llm | output_parser
    return chain


# 초기화 버튼이 눌리면...
if clear_btn:
    st.session_state["messages"] = []

# 이전 대화 기록 출력
print_messages()


        
# 사용자의 입력
user_input = st.chat_input("번역할 내용을 물어보세요!")


# 만약에 사용자 입력이 들어오면...
if user_input:
    # 사용자의 입력
    st.chat_message("user").write(user_input)
    # chain 을 생성
    chain = create_chain(selected_prompt)

    # 스트리밍 호출
    response = chain.stream({"question": user_input})
    with st.chat_message("assistant"):
        # 빈 공간(컨테이너)을 만들어서, 여기에 토큰을 스트리밍 출력한다.
        container = st.empty()

        ai_answer = ""
        for token in response:
            ai_answer += token
            container.markdown(ai_answer)

    # 대화기록을 저장한다.
    add_message("user", user_input)
    add_message("assistant", ai_answer)


