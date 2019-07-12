"""Define utils for the taskmanager app."""


def log_tail(log, n_lines=10):
    """Return the last lines of a log text."""
    lines = log.split("\n")
    hidden_lines = len(lines) - n_lines
    if hidden_lines > 0:
        lines = [f"{hidden_lines} lines hidden ..."] + lines[hidden_lines:]
    return "\n".join(lines)
