# 육하원칙 조사/어미 등 수정 함수
def modify_answer(answer, index):
    sentences = answer.split('. ')
    if len(sentences) > 1:
        answer = sentences[1]
    if answer.endswith('.'):
        answer = answer[:-1]
    if '주체는 ' in answer:
        answer = answer.split('주체는 ')[1]
    answer = answer.replace("이 기사는 ", "")
    answer = answer.split('이다')[0].strip()
    answer = answer.split('되었음')[0].strip()
    answer = answer.split('입니다')[0].strip()
    if '됩' in answer:
        answer = answer.split('됩')[0].strip() + '됨'
    if '됐' in answer:
        answer = answer.split('됐')[0].strip() + '됨'
    if '된' in answer:
        answer = answer.split('된')[0].strip() + '됨'
    if '했' in answer:
        answer = answer.split('했')[0].strip() + '함'
    if '하였' in answer:
        answer = answer.split('하였')[0].strip() + '함'
    answer = answer.split('되었')[0].strip()
    answer = answer.split('합니다')[0].strip()
    if answer.endswith('목적으로'):
        answer = answer.split('목적으로')[0].strip() + ' 목적으로'
    if answer.endswith('때문에'):
        answer = answer.split('때문에')[0].strip() + ' 때문에'
    if answer.endswith('습니다'):
        answer = answer.split('습니다')[0].strip() + '음'
    # 누가
    if index == 0:
        answer = answer.split('이 ')[0].strip()
        answer = answer.split('가 ')[0].strip()
    # 언제
    if index == 1:
        answer = answer.split('에서')[0].strip()
        answer = answer.split('에 ')[0].strip()
        if '은 ' in answer:
            answer = answer.split('은 ')[1].strip()
        if '는 ' in answer:
            answer = answer.split('는 ')[1].strip()
        if '일' in answer:
            answer = answer.split('일')[0].strip() + '일'
    if index == 2:
        answer = answer.split('에서')[0].strip()
        if '은 ' in answer:
            answer = answer.split('은 ')[1].strip()
        if '는 ' in answer:
            answer = answer.split('는 ')[1].strip()
    if index == 4:
        if '위해' in answer:
            answer = answer.split('위해')[0].strip() + ' 위해'
    if answer.endswith('다'):
        answer = answer.split('다')[0].strip() + '음'

    return answer
    

class ChatGPT:
    def __init__(self, summary_content):
        self.content = f"Content: {summary_content}"

    def run_gpt(self, questions):
        MAX_RETRIES = 3
        RETRY_DELAY = 10
        answers = []  # 답변을 모을 리스트

        for question in questions:
            gpt_standard_messages = [
                {"role": "system", "content": self.content},
                {"role": "user", "content": question}
            ]

            for attempt in range(MAX_RETRIES):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo-0125",
                        messages=gpt_standard_messages,
                        temperature=0.8
                    )
                    break
                except:
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                    else:
                        raise

            answer = response['choices'][0]['message']['content']
            answers.append(answer)  # 답변을 리스트에 추가

        return answers

    # 핵심 사건 추출
    def extract_key(self, content):
        # 전처리(error/ blank 있는 row 제거)
        if content.strip() == "" or content.startswith("Error"):
            return "none"

        chat_bot_instance = ChatGPT(content)
        key_question = ["이 기사는 어떤 사건에 대한 거야? 한국어 단답형 명사로 끝나도록 답해줘. 최대한 짧게."]
        answer = chat_bot_instance.run_gpt(key_question)
        answer = answer[0]

        answer = answer.replace("이 기사는 ", "")
        answer = answer.split('에 대한')[0].strip()
        answer = answer.split('에 관한')[0].strip()
        answer = answer.split('한 사건')[0].strip()
        answer = answer.split('와 관련된')[0].strip()
        answer = answer.split('과 관련된')[0].strip()
        answer = answer.split('한다는')[0].strip()
        answer = answer.split('을 하고')[0].strip()
        if answer.endswith('.'):
            answer = answer[:-1]

        return answer

    def extract_5w1h(self, content, key):

        additional_content = "육하원칙에 대응하는 답을 짧게 단답형으로 대답해. 문장 말고 단답!!"
        modified_answers = []

        if key is not None:  # key가 null이 아니면

            content = f"Content: {content}\nAdditional Content: {additional_content}"
            self.content = content

            questions = [f"{key} 주체가 누구야?",
                         f"{key} 언제 일어났어?",
                         f"{key} 어디에서 일어났어?",
                         f"{key} 어떻게 일어났어?",
                         f"{key} 왜 일어났어?"]

            answers = self.run_gpt(questions)

            for index, answer in enumerate(answers):
                modified_answers.append(modify_answer(answer, index))

        result = {
            "누가": modified_answers[0],
            "언제": modified_answers[1],
            "어디서": modified_answers[2],
            "어떻게": modified_answers[3],
            "왜": modified_answers[4],
            "무엇을": key
        }

        return result
