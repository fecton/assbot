from dataclasses import dataclass

@dataclass()
class ReportStructure:
    chat_id:        int
    chat_title:     str
    user_id:        int
    user_name:      str
    user_firstname: str
    message:        str

