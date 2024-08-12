from typing import Dict, Optional
from .ui.tui import ForgeLogsApp

def launch_forge_logs_tui(params: Optional[Dict]):
    ForgeLogsApp(params).run()
