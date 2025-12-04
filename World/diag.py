import sys, os, pkgutil, importlib

print("=== PYTHON RUNTIME DIAGNOSTIC ===")
print("Executable:", sys.executable)
print("CWD:", os.getcwd())

print("\n--- sys.path ---")
for p in sys.path:
    print("   ", p)

print("\n--- site-packages contents related to ptcgengine ---")
for p in sys.path:
    if p.endswith("site-packages"):
        print("site-packages:", p)
        for name in os.listdir(p):
            if "ptcgengine" in name.lower():
                print("   FOUND:", name)

print("\n--- Attempting import ptcgengine ---")
try:
    import ptcgengine
    print("IMPORT SUCCESS")
    print("ptcgengine.__file__ =", ptcgengine.__file__)
except Exception as e:
    print("IMPORT FAILURE:", type(e).__name__, str(e))

print("\n--- Checking pkgutil.find_loader ---")
try:
    mod = pkgutil.find_loader("ptcgengine")
    print("pkgutil.find_loader:", mod)
except Exception as e:
    print("pkgutil error:", e)

print("\n--- Checking importlib.util.find_spec ---")
try:
    spec = importlib.util.find_spec("ptcgengine")
    print("find_spec:", spec)
except Exception as e:
    print("find_spec error:", e)

print("\n=== END OF DIAGNOSTIC ===")