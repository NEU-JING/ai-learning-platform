import sys
sys.path.insert(0, '.')

# === 测试1: 基础类型检查 ===
@validate_types(name=str, age=int, returns=str)
def greet(name, age):
    return f"{name}今年{age}岁"

# 正常调用
result = greet("Alice", 25)
assert result == "Alice今年25岁", f"期望 Alice今年25岁, 得到 {result}"
print("测试1.1: 基础类型检查-正常调用 PASSED")

# 类型错误
try:
    greet("Alice", "25")
    assert False, "应该抛出TypeError"
except TypeError:
    print("测试1.2: 基础类型检查-参数类型错误 PASSED")

# === 测试2: 自定义验证器 ===
@validate_types(
    email=lambda x: "@" in x,
    age=lambda x: 0 < x < 150
)
def register(email, age):
    return "registered"

result = register("a@b.com", 25)
assert result == "registered"
print("测试2.1: 自定义验证器-正常调用 PASSED")

try:
    register("invalid", 25)
    assert False, "应该抛出ValueError"
except ValueError:
    print("测试2.2: 自定义验证器-email验证失败 PASSED")

try:
    register("a@b.com", 200)
    assert False, "应该抛出ValueError"
except ValueError:
    print("测试2.3: 自定义验证器-age验证失败 PASSED")

# === 测试3: 可选参数 ===
@validate_types(name=str, age=int, _optional=["age"])
def greet_optional(name, age=None):
    return f"Hello {name}"

result = greet_optional("Alice")
assert "Alice" in result
print("测试3.1: 可选参数-省略可选参数 PASSED")

result = greet_optional("Alice", 25)
assert "Alice" in result
print("测试3.2: 可选参数-传入可选参数 PASSED")

# === 测试4: 返回值检查 ===
@validate_types(x=int, returns=int)
def bad_return(x):
    return "not an int"

try:
    bad_return(42)
    assert False, "应该抛出TypeError"
except TypeError:
    print("测试4: 返回值类型检查 PASSED")

print("所有测试通过!")
