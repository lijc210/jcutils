def foo(x):
    if x > 0:
        return x
    else:
        return -x


def test_foo_positive():
    assert foo(10) == 10  # 测试 x > 0 的情况


def test_foo_negative():
    assert foo(-10) == 10  # 测试 x <= 0 的情况


def test_foo_zero():
    assert foo(0) == 0  # 测试 x = 0 的情况（如果需要考虑这个情况）
