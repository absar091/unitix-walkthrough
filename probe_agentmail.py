import sys
print("python:", sys.executable)
try:
    import agentmail
    print("agentmail OK:", agentmail.__file__)
except Exception as e:
    print("agentmail ERR:", e)
