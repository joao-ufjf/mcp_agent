import json
from mcp.server.fastmcp import FastMCP
from datetime import datetime
import os

# Ensure alarms.json exists at server startup
alarms_file = "alarms.json"
if not os.path.exists(alarms_file):
    with open(alarms_file, "w") as f:
        json.dump({}, f)

# Initialize FastMCP server
mcp = FastMCP("alarm_server")

@mcp.tool()
def get_time_now() -> str:
    """
    Get the current time.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
def set_alarm(datetime_str: str, description: str) -> str:
    """
    Set an alarm for datetime with the description. Use the format %Y-%m-%d %H:%M:%S.
    """
    with open(alarms_file, "r") as f:
        alarms = json.load(f)

    date, time_str = datetime_str.split(" ")
    hour, minute, *_ = time_str.split(":")

    alarms.setdefault(date, {}).setdefault(hour, {})[minute] = description

    with open(alarms_file, "w") as f:
        json.dump(alarms, f, indent=2)

    return f"Alarm set for {datetime_str}"

@mcp.tool()
def get_alarm(datetime_str: str) -> dict:
    """
    Get a json with an alarm from the agenda based on the datetime. Use the format %Y-%m-%d %H:%M:%S.
    """
    with open(alarms_file, "r") as f:
        alarms = json.load(f)

    date, time_str = datetime_str.split(" ")
    hour, minute, *_ = time_str.split(":")

    try:
        description = alarms[date][hour][minute]
    except KeyError:
        return {"error": f"No alarm set for {datetime_str}"}
    
    return {
        "datetime": datetime_str,
        "description": description
    }

@mcp.tool()
def get_alarms() -> dict:
    """
    Get a json with all alarms from the user.
    """
    with open(alarms_file, "r") as f:
        alarms = json.load(f)
    return {"alarms": alarms}

@mcp.tool()
def delete_alarm(datetime_str: str) -> str:
    """
    Delete an alarm from the agenda. Use the format %Y-%m-%d %H:%M:%S.
    """
    with open(alarms_file, "r") as f:
        alarms = json.load(f)

    date, time_str = datetime_str.split(" ")
    hour, minute, *_ = time_str.split(":")

    try:
        del alarms[date][hour][minute]
        # Clean up empty dicts
        if not alarms[date][hour]:
            del alarms[date][hour]
        if not alarms[date]:
            del alarms[date]
    except KeyError:
        return f"No alarm found for {datetime_str}"

    with open(alarms_file, "w") as f:
        json.dump(alarms, f, indent=2)

    return f"Alarm deleted for {datetime_str}"

@mcp.prompt()
def generate_alarm_prompt(alarm_info: str) -> str:
    """Generate a prompt for the alarm creation tool."""
    return f"""Analyze the intruction for alarm creation.
    Return a json with the alarm information.
    The json should have the following fields:
    - datetime: the datetime of the alarm in the format %Y-%m-%d %H:%M:%S
    - description: the description of the alarm
    
    If the description is not clear, just use "4L4RM" as the description.
    If the date is not clear, just get the date with @get_time_now and use the date or the next day.
    
    # Begin of instruction
    {alarm_info}
    # End of instruction
    
    # Return the json with the alarm information
    {{
        "datetime": "2025-07-17 00:01:50",
        "description": "Alarm"
    }}
    """

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')