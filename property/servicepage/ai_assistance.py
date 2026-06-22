from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status 
import requests
import json

HF_TOKEN = settings.HF_TOKEN
HF_API_URL = settings.HF_API_URL


@api_view(['POST'])
def chat_bot(request):
    if request.method == 'POST':
        try:
            text  = json.loads(request.body)
            user_message = text.get('message', '')
            headers = {
                'Authorization': f'Bearer {HF_TOKEN}',
                'Content-Type': 'application/json'
            }

            payload = {
                'model' : 'mistralai/Mistral-7B-Instruct-v0.2:featherless-ai',
                'messages' :[
                    {
                        'role': 'system',
                        'content':"""
                            You are Jarvis, a helpful AI assistant.
                            Always detect the user's language and respond in the same language.
                            """
                    },
                    {
                        'role':'user',
                        'content':user_message
                    }
                ],
                'max_tokens':500,
                'temperature':0.7

            }

            response = requests.post(
                HF_API_URL,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                response_data = response.json()

                bot_reply = response_data['choices'][0]['message']['content']
                return Response({'message':bot_reply},status=status.HTTP_200_OK)
            else:
                return Response({'error': f'api error {response.text}'},
                status=response.status_code)
            
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)