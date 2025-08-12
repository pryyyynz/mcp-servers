#!/usr/bin/env python3
from .auth import authenticate
import io
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import mcp.types as types
from pydantic import AnyUrl
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import asyncio
import json
import os
import sys
from typing import Any, Sequence

# Add the parent directory to the Python path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


# Import from the same directory

server = Server("gdrive-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available Google Drive tools."""
    return [
        types.Tool(
            name="list_files",
            description="List files in Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (optional)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of files to return",
                        "default": 10
                    }
                }
            }
        ),
        types.Tool(
            name="upload_file",
            description="Upload a file to Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Local path to file to upload"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name for the file in Drive (optional)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        types.Tool(
            name="download_file",
            description="Download a file from Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "Google Drive file ID"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Local path to save the file"
                    }
                },
                "required": ["file_id", "output_path"]
            }
        ),
        types.Tool(
            name="delete_file",
            description="Delete a file from Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "Google Drive file ID"
                    }
                },
                "required": ["file_id"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Handle tool calls."""
    try:
        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)

        if name == "list_files":
            files = await list_drive_files(service, arguments)
            return [types.TextContent(type="text", text=json.dumps(files, indent=2))]

        elif name == "upload_file":
            result = await upload_file_to_drive(service, arguments)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "download_file":
            result = await download_file_from_drive(service, arguments)
            return [types.TextContent(type="text", text=result)]

        elif name == "delete_file":
            result = await delete_file_from_drive(service, arguments)
            return [types.TextContent(type="text", text=result)]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def list_drive_files(service, arguments: dict) -> dict:
    """List files in Google Drive."""
    query = arguments.get("query", "")
    max_results = arguments.get("max_results", 10)

    results = service.files().list(
        pageSize=max_results,
        fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)",
        q=query if query else None
    ).execute()

    return results.get('files', [])


async def upload_file_to_drive(service, arguments: dict) -> dict:
    """Upload file to Google Drive."""
    file_path = arguments["file_path"]
    file_name = arguments.get("name", os.path.basename(file_path))

    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_path)

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return {"file_id": file.get('id'), "message": "File uploaded successfully"}


async def download_file_from_drive(service, arguments: dict) -> str:
    """Download file from Google Drive."""
    file_id = arguments["file_id"]
    output_path = arguments["output_path"]

    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while done is False:
        status, done = downloader.next_chunk()

    with open(output_path, 'wb') as f:
        f.write(fh.getvalue())

    return f"File downloaded to {output_path}"


async def delete_file_from_drive(service, arguments: dict) -> str:
    """Delete file from Google Drive."""
    file_id = arguments["file_id"]
    service.files().delete(fileId=file_id).execute()
    return f"File {file_id} deleted successfully"


async def main():
    from mcp.server.stdio import stdio_server

    print("Starting Google Drive MCP server...", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        print("Google Drive server ready for MCP connections", file=sys.stderr)
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gdrive-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
