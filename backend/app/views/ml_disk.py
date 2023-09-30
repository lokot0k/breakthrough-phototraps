import io
import os

from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views import View
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

from googleapiclient.http import MediaIoBaseDownload
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from oauth2client.client import GoogleCredentials

from app.utils.drive_downloader import download_files
from app.utils.storage import MyStorage


class MlDiskView(View):
    def get(self, request: HttpRequest, *args,
            **kwargs) -> JsonResponse | HttpResponse:
        pass

    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        creds = None
        SCOPES = ['https://www.googleapis.com/auth/drive']
        st = MyStorage()
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(st.path('token.json')):
            creds = Credentials.from_authorized_user_file(st.path('token.json'),
                                                          SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    st.path('client_secret.json'), SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(st.path('token.json'), 'w') as token:
                token.write(creds.to_json())

        service = build('drive', 'v3', credentials=creds)
        folder_id = '1LjWvvTEKepJtJMya4kQj0MQ2hny94yyo'  # request.body.folder
        print(st.path(""))
        download_files(service, folder_id, st.path(""))

        return JsonResponse({'abcdef': "asdads"})

    def head(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'message': 'unsupported method'}, status=403)

    def put(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'me ssage': 'unsupported method'}, status=403)
