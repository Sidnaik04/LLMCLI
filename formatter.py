import json

from rich.console import Console
from rich.panel import Panel

console = Console()

def print_json(response_dict: dict)->None:
    print(json.dumps(response_dict, indent=2, ensure_ascii=False))
    
def print_pretty(response_dict: dict)-> None:
    provider = response_dict["provider"]
    model = response_dict['model']
    response = response_dict["response"]
    
    header = f"{provider} / {model}"
    
    console.print(
        Panel(
            response,
            title=header,
            border_style="blue"
        )
    )
    
