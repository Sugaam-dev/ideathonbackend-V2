import os
from app.config import settings

def resolve_secure_upload_destination(filename: str) -> str:
    """
    Validates storage paths against project layout boundaries, auto-generating
    target directories if missing.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    target_dir = settings.UPLOAD_DIR
    
    if not os.path.isabs(target_dir):
        target_dir = os.path.join(base_dir, target_dir)
        
    os.makedirs(target_dir, exist_ok=True)
    
    # Strip dangerous relative path navigation indicators from filenames
    clean_filename = os.path.basename(filename)
    return os.path.join(target_dir, clean_filename)