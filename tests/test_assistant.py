from bobot.ai.assistant import LocalAssistant


def test_local_assistant_response():
    assistant = LocalAssistant()
    result = assistant.answer("teste")
    assert "Integração" in result
