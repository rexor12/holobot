# Adapted from https://github.com/dotnet/runtime/blob/main/src/libraries/Common/src/Roslyn/Hash.cs

def combine(newKey: int, currentKey: int) -> int:
    return ((currentKey * 0xA5555529) + newKey) & 0xFFFFFFFF

def combine2(
    v1: object | None,
    v2: object | None
) -> int:
    return combine(
        v1.__hash__() if v1 is not None else 0,
        v2.__hash__() if v2 is not None else 0
    )

def combine3(
    v1: object | None,
    v2: object | None,
    v3: object | None
) -> int:
    combined_hash = v1.__hash__() if v1 is not None else 0
    combined_hash = combine(combined_hash, v2.__hash__() if v2 is not None else 0)
    return combine(combined_hash, v3.__hash__() if v3 is not None else 0)

def combine4(
    v1: object | None,
    v2: object | None,
    v3: object | None,
    v4: object | None
) -> int:
    combined_hash = v1.__hash__() if v1 is not None else 0
    combined_hash = combine(combined_hash, v2.__hash__() if v2 is not None else 0)
    combined_hash = combine(combined_hash, v3.__hash__() if v3 is not None else 0)
    return combine(combined_hash, v4.__hash__() if v4 is not None else 0)

def combine5(
    v1: object | None,
    v2: object | None,
    v3: object | None,
    v4: object | None,
    v5: object | None
) -> int:
    combined_hash = v1.__hash__() if v1 is not None else 0
    combined_hash = combine(combined_hash, v2.__hash__() if v2 is not None else 0)
    combined_hash = combine(combined_hash, v3.__hash__() if v3 is not None else 0)
    combined_hash = combine(combined_hash, v4.__hash__() if v4 is not None else 0)
    return combine(combined_hash, v5.__hash__() if v5 is not None else 0)
