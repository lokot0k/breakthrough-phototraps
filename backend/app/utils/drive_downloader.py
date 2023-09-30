import os


def download_files(service, folder_id, output_dir):
    page_token = None
    while True:
        response = service.files().list(
            q=f"'{folder_id}' in parents",
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType)',
            pageToken=page_token
        ).execute()

        for file in response.get('files', []):
            file_id = file['id']
            file_name = file['name']
            mime_type = file['mimeType']

            if mime_type == 'application/vnd.google-apps.folder':
                # If the file is a subfolder, recursively call the function to download its contents.
                download_files(service, file_id,
                               os.path.join(output_dir, file_name))
            else:
                # If the file is not a folder, download it.
                request = service.files().get_media(fileId=file_id)
                file_path = os.path.join(output_dir, file_name)
                with open(file_path, 'wb') as f:
                    f.write(request.execute())

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break