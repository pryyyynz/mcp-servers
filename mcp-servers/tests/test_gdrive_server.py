import unittest
import asyncio
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from src.gdrive_server.handlers import upload_file_to_drive, download_file_from_drive, list_drive_files, delete_file_from_drive


class TestGDriveServer(unittest.TestCase):

    @patch('src.gdrive_server.handlers.MediaFileUpload')
    @patch('src.gdrive_server.handlers.authenticate')
    @patch('src.gdrive_server.handlers.build')
    @patch('os.path.exists')
    def test_upload_file(self, mock_exists, mock_build, mock_auth, mock_media_upload):
        # Mock file existence
        mock_exists.return_value = True

        # Mock authentication and service
        mock_creds = MagicMock()
        mock_auth.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock MediaFileUpload
        mock_media = MagicMock()
        mock_media_upload.return_value = mock_media

        # Mock file upload response
        mock_file_response = {'id': 'test_file_id',
                              'name': 'test_file.txt', 'size': '100'}
        mock_service.files().create().execute.return_value = mock_file_response

        # Test the upload file functionality
        result = upload_file_to_drive('test_file.txt')

        self.assertIsInstance(result, dict)
        self.assertIn('file_id', result)
        self.assertEqual(result['file_id'], 'test_file_id')

    @patch('src.gdrive_server.handlers.MediaIoBaseDownload')
    @patch('src.gdrive_server.handlers.authenticate')
    @patch('src.gdrive_server.handlers.build')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_download_file(self, mock_makedirs, mock_file_open, mock_build, mock_auth, mock_download):
        # Mock authentication and service
        mock_creds = MagicMock()
        mock_auth.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock file metadata
        mock_file_meta = {'name': 'test_file.txt', 'size': '100'}
        mock_service.files().get.return_value.execute.return_value = mock_file_meta

        # Mock download functionality
        mock_request = MagicMock()
        mock_service.files().get_media.return_value = mock_request

        # Mock downloader
        mock_downloader = MagicMock()
        mock_download.return_value = mock_downloader
        mock_downloader.next_chunk.side_effect = [(None, False), (None, True)]

        # Mock BytesIO
        with patch('src.gdrive_server.handlers.io.BytesIO') as mock_bytesio:
            mock_fh = MagicMock()
            mock_bytesio.return_value = mock_fh
            mock_fh.getvalue.return_value = b'test file content'

            # Test the download file functionality
            result = download_file_from_drive('test_file_id', 'output.txt')

            self.assertIsNotNone(result)
            self.assertIn('File downloaded to', result)

    @patch('src.gdrive_server.handlers.authenticate')
    @patch('src.gdrive_server.handlers.build')
    def test_list_files(self, mock_build, mock_auth):
        # Mock authentication and service
        mock_creds = MagicMock()
        mock_auth.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock file list response
        mock_files_response = {
            'files': [
                {'id': '1', 'name': 'file1.txt'},
                {'id': '2', 'name': 'file2.txt'}
            ]
        }
        mock_service.files().list().execute.return_value = mock_files_response

        # Test the list files functionality
        files = list_drive_files()

        self.assertIsInstance(files, list)
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]['name'], 'file1.txt')

    @patch('src.gdrive_server.handlers.authenticate')
    @patch('src.gdrive_server.handlers.build')
    def test_delete_file(self, mock_build, mock_auth):
        # Mock authentication and service
        mock_creds = MagicMock()
        mock_auth.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock file metadata for name retrieval
        mock_file_meta = {'name': 'test_file.txt'}
        mock_service.files().get.return_value.execute.return_value = mock_file_meta

        # Mock delete response
        mock_service.files().delete().execute.return_value = None

        # Test the delete file functionality
        result = delete_file_from_drive('test_file_id')

        self.assertIsInstance(result, str)
        self.assertIn('deleted successfully', result)


if __name__ == '__main__':
    unittest.main()
