import sys

print("Python version:")
print(sys.version)

print("\nArguments passed:")
print(sys.argv)

print("\nScript name:")
print(sys.argv[0])

if len(sys.argv) > 1:
    print("\nFirst argument:")
    print(sys.argv[1])

if len(sys.argv) > 2:
    print("\nSecond argument:")
    print(sys.argv[2])