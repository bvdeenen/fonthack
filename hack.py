import sys

# real digit -> digit written in the HTML (the obfuscated font maps it back)
REAL = "123456789"
ENCODED = "234567891"
table = str.maketrans(REAL, ENCODED)


def encode(s: str) -> str:
    return s.translate(table)


if __name__ == "__main__":
    i = sys.argv[1]
    res = encode(i)
    print(f"{i} -> {res}")
