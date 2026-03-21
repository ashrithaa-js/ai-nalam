import os
import shutil

def move_to_processed(file_path: str, target_dir: str = "data/processed/"):
    """
    Moves an analyzed medical report file to the processed directory for archiving.
    """
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    file_name = os.path.basename(file_path)
    new_path = os.path.join(target_dir, file_name)
    shutil.move(file_path, new_path)
    return new_path

def get_file_extension(file_path: str):
    """
    Detects file extension to decide extraction method.
    """
    _, ext = os.path.splitext(file_path)
    return ext.lower()

def safe_delete(file_path: str):
    """
    Safely delete a file if it exists.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
