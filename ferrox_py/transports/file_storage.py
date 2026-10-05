from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator
import aiofiles
import os
from fastapi import UploadFile
from ferrox_py.core.provider import injectable
from ferrox_py.core.errors import FerroxError

@injectable()
class FileStorageTransport:
    async def handle_upload(self, upload_file: UploadFile, destination_dir: str, chunk_size: int = 1024 * 1024) -> str:
        """
        Saves an uploaded file to disk in chunks to prevent memory overflow.
        """
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir, exist_ok=True)
            
        file_path = os.path.join(destination_dir, upload_file.filename)
        
        try:
            async with aiofiles.open(file_path, 'wb') as out_file:
                while content := await upload_file.read(chunk_size):
                    await out_file.write(content)
            return file_path
        except Exception as e:
            raise FerroxError(message=f"File upload failed: {e}", status_code=500)
