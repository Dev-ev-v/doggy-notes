from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel

class Console:
	def __init__(self, console: Console=Console()):
		self.console = console
		
	def write(self, *content, **kwargs):
	    self.console.print(*content, **kwargs)   
	    	
	def title(self, text: str):
	     return f"[bold]{text}[/bold]"        
              
	def success(self, text: str):
	   self.console.print(f"[bold green]OK:[/bold green] {text}")    
                
	def error(self, text: str):
	   self.write(
            Panel(f"[bold red]ERROR:[/bold red] {text}", border_style="red")
        )
             
	def note(self, text: str, title: str = None):
	   self.write(
            Panel(text, border_style="blue", title=title)
        )
	   
	def confirm(self, text: str) -> bool:
	   answer = input(f"{text} [y/n]: ")
	   return answer.strip().lower() in {
            "y",
            "yes",
        }                  