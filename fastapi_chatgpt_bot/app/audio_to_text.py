# from google.cloud import speech_v1p1beta1 as speech
#
#
# client = speech.SpeechClient()


async def audio_to_text(voice_bytes: bytes) -> str:
    # audio = speech.RecognitionAudio(content=voice_bytes)
    # config = speech.RecognitionConfig(
    #     encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
    #     sample_rate_hertz=48000,
    #     language_code="ru-RU",
    #     enable_automatic_punctuation=True,
    #     alternative_language_codes=["en-US", "es-ES", "fr-FR"],
    # )
    # response = client.recognize(config=config, audio=audio)
    # text = ""
    # for result in response.results:
    #     text += "{lang}: {text}".format(result.language_code, result.alternatives[0].transcript)
    text = "скоро научусь распозновать аудио сообщение, терпение мой юный Оби-Ван"
    return text

# TODO: use chatGPT API to convert voice instead of google
