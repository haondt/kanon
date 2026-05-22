from typing import Any
# deep merge two dictionaries of basic types
# when merging primitives, the one from d2 is preferred
def deep_merge(d1: dict[str, Any], d2: dict[str, Any], conflicts: str = "new", _path: str = ""):
    if conflicts not in ["new", "old", "err"]:
        raise ValueError("Unexpected conflict resolution:" + conflicts)
    def merge_list(l1: list[Any], l2: list[Any]):
        added = set()
        l: list[Any] = []
        def add_to_l(la: list[Any]):
            nonlocal added
            nonlocal l
            for v in la:
                if v not in added:
                    added.add(v)
                    l.append(v)
        add_to_l(l1)
        add_to_l(l2)
        return l
    result = d1.copy()
    for k, v in d2.items():
        if k not in result:
            result[k] = v
            continue
        if type(v) != type(result[k]):
            if conflicts == "new":
                result[k] = v
            elif conflicts == "err":
                raise KeyError(f"Multiple entries found for key: {_path}.{k}")
            continue
        if isinstance(v, dict):
            result[k] = deep_merge(result[k], v, conflicts, _path + "." + k)
            continue
        if isinstance(v, (tuple, list)):
            result[k] = merge_list(result[k], v)
            continue

        if conflicts == "new":
            result[k] = v
        elif conflicts == "err":
            raise KeyError(f"Multiple entries found for key: {_path}.{k}")
    return result

