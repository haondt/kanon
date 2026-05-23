import pytest

from spek.core.utils import deep_merge


def test_deep_merge_new_wins_on_collision():
    result = deep_merge({"a": 1}, {"a": 2})
    assert result["a"] == 2


def test_deep_merge_old_preserved_on_collision():
    result = deep_merge({"a": 1}, {"a": 2}, conflicts="old")
    assert result["a"] == 1


def test_deep_merge_err_raises_on_collision():
    with pytest.raises(KeyError):
        deep_merge({"a": 1}, {"a": 2}, conflicts="err")


def test_deep_merge_type_mismatch_new_takes_incoming():
    result = deep_merge({"a": 1}, {"a": "string"}, conflicts="new")
    assert result["a"] == "string"


def test_deep_merge_type_mismatch_old_keeps_original():
    result = deep_merge({"a": 1}, {"a": "string"}, conflicts="old")
    assert result["a"] == 1


def test_deep_merge_list_deduplicates():
    result = deep_merge({"a": [1, 2]}, {"a": [2, 3]})
    assert result["a"] == [1, 2, 3]


def test_deep_merge_list_with_dicts():
    d1 = {"a": [{"x": 1}]}
    d2 = {"a": [{"x": 1}, {"x": 2}]}
    result = deep_merge(d1, d2)
    assert result["a"] == [{"x": 1}, {"x": 2}]


def test_deep_merge_nested_dicts():
    result = deep_merge({"a": {"b": 1, "c": 2}}, {"a": {"c": 3, "d": 4}})
    assert result["a"] == {"b": 1, "c": 3, "d": 4}


def test_deep_merge_non_overlapping_keys_merged():
    result = deep_merge({"a": 1}, {"b": 2})
    assert result == {"a": 1, "b": 2}
