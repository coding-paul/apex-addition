import os

def get_absolute_path(rel_path: str) -> str:
  script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
  abs_file_path = os.path.join(script_dir, rel_path)
  return abs_file_path