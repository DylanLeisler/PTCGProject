import sys

TRACE_ENABLED = True

def trace(*args):
    """Simple debug logger."""
    if TRACE_ENABLED:
        print("[TRACE]", *args, file=sys.stderr)
