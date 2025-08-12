from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import os
import io
from .auth import authenticate


def upload_file_to_drive(file_path: str, name: str = None) -> dict:
    """Upload a file to Google Drive."""
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    file_name = name or os.path.basename(file_path)
    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_path)

    try:
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        return {'file_id': uploaded_file.get('id'), 'message': 'File uploaded successfully'}
    except HttpError as error:
        raise Exception(f"Upload failed: {str(error)}")


def download_file_from_drive(file_id: str, output_path: str) -> str:
    """Download a file from Google Drive."""
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()

        with open(output_path, 'wb') as f:
            f.write(fh.getvalue())

        return f"File downloaded to {output_path}"
    except HttpError as error:
        raise Exception(f"Download failed: {str(error)}")


def list_drive_files(query: str = None, max_results: int = 10) -> list:
    """List files in Google Drive."""
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    try:
        results = service.files().list(
            pageSize=max_results,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)",
            q=query if query else None
        ).execute()
        return results.get('files', [])
    except HttpError as error:
        raise Exception(f"List files failed: {str(error)}")


def delete_file_from_drive(file_id: str) -> str:
    """Delete a file from Google Drive."""
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    try:
        service.files().delete(fileId=file_id).execute()
        return f"File {file_id} deleted successfully"
    except HttpError as error:
        raise Exception(f"Delete failed: {str(error)}")
