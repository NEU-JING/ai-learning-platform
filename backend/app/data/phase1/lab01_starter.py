from functools import wraps
import inspect

def validate_types(**type_specs):
    """
    参数类型验证装饰器
    
    用法:
        @validate_types(name=str, age=int, returns=str)
        def greet(name, age):
            return f"{name}今年{age}岁"
    
    支持自定义验证器:
        @validate_types(email=lambda x: "@" in x)
        def register(email):
            return "OK"
    
    支持可选参数:
        @validate_types(name=str, _optional=["age"])
    """
    # 提取特殊参数
    optional_params = type_specs.pop('_optional', [])
    return_type = type_specs.pop('returns', None)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # TODO: 1. 获取函数签名和参数绑定
            # TODO: 2. 检查每个参数的类型/验证器
            # TODO: 3. 调用原函数
            # TODO: 4. 检查返回值类型
            pass
        return wrapper
    return decorator
