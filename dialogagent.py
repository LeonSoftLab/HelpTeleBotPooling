import config;
from google.cloud import dialogflow_v2

class DialogAgent:
    """Класс для работы с диалоговым ботом dialogflow"""
    def __init__(self, credentials, project_id):
        self.session_list = []
        self.credentials = credentials
        self.project_id = project_id
        self.session_client = dialogflow_v2.SessionsClient()
    
    def get_session(self, chat_id):
        result = None
        session_id = "session_"+str(chat_id)
        for session in self.session_list:
            if session[0] == chat_id:
                result = session
        if result is None:
            session = self.session_client.session_path(self.project_id, session_id)
            result = [chat_id,session]
            self.session_list.append(result)
        return result

    def send_message(self, session, language_code, text):
        text_input = dialogflow_v2.types.TextInput(text=text, language_code=language_code)
        query_input = dialogflow_v2.types.QueryInput(text=text_input)
        response = self.session_client.detect_intent(session=session, query_input=query_input)
        return response.query_result

if __name__ == '__main__':
    import os
    import google.auth
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'doc\helpbot-vinal-b25c396a08dc.json'
    language_code = "ru"
    credentials, project_id = google.auth.default()
    dialog_agent = DialogAgent(credentials, project_id)
    session = dialog_agent.get_session(12345)
    query_result = dialog_agent.send_message(session[1],language_code,"А почему нет проекта ЗП?")
    print('=' * 20)
    print('Query text: {}'.format(query_result.query_text))
    print('Detected intent: {} (confidence: {})\n'.format(query_result.intent.display_name,query_result.intent_detection_confidence))
    print('Fulfillment text: {}\n'.format(query_result.fulfillment_text))
    print('=' * 20)
    print(query_result)