# LovelyRitoru 插件开发说明书

## 1. 插件结构

每个插件应该是一个独立的 Python 包,包含一个 `__init__.py` 文件。插件应该放置在以下三个目录之一中:

- `plugins/base_plugins/`: 基础工具模块
- `plugins/ex_plugins/`: 进阶工具模块
- `plugins/check_plugins/`: 检测插件

## 2. 必需的属性

每个插件的 `__init__.py` 文件中必须定义以下属性:

```python
__plugin_name__ = "插件名称"
__description__ = "插件描述"
```

这些属性用于在用户界面中显示插件信息。

## 3. 必需的方法

### 3.1 __checktype__(file_path)

- 功能: 检查文件是否适用于该插件
- 参数: 
  - `file_path`: 文件路径
- 返回值: 
  - `True`: 如果文件适用于该插件
  - `False`: 如果文件不适用于该插件

示例:
```python
def __checktype__(file_path):
    return file_path.lower().endswith('.zip')
```

### 3.2 __start__(file_path, password_list=None)

- 功能: 执行插件的主要处理逻辑
- 参数:
  - `file_path`: 要处理的文件路径
  - `password_list`: 可选的密码列表,用于需要密码的操作
- 返回值: 
  - 成功时: `(log_message, output_files)`
    - `log_message`: 字符串,描述处理结果
    - `output_files`: 列表,包含输出文件路径或处理结果
  - 失败时: `(error_message, None)`
    - `error_message`: 字符串,描述错误信息

示例:
```python
def __start__(file_path, password_list=None):
    try:
        # 处理逻辑
        return "处理成功", [output_file_path]
    except Exception as e:
        return f"处理文件 {file_path} 时出错：{str(e)}", None
```

### 3.3 __result__(result)

- 功能: 处理和格式化 `__start__` 方法的返回结果
- 参数:
  - `result`: `__start__` 方法的返回值
- 返回值:
  - 字符串: 格式化后的结果,将显示在结果窗口中
  - `None`: 如果不需要在结果窗口中显示任何内容

示例:
```python
def __result__(result):
    if isinstance(result, tuple) and len(result) == 2:
        _, data = result
        if isinstance(data, list) and len(data) > 0:
            return f"处理结果: {data[0]}"
    return None
```

## 4. 注意事项

1. 插件应该处理可能出现的异常,并在 `__start__` 方法中返回适当的错误信息。

2. 对于需要生成输出文件的插件,应该将文件保存在 `output` 目录下的相应子目录中。

3. 插件应该尽可能地独立,避免对主程序的其他部分产生依赖。

4. 如果插件需要使用第三方库,请确保在插件的文档中说明这些依赖。

5. 插件的性能应该得到优化,特别是对于可能处理大文件的插件。

6. 插件应该遵循 Python 的编码规范(PEP 8)。

## 5. 示例插件

以下是一个简单的示例插件,用于解码 Base64 编码的内容:

```python
import base64
import os

__plugin_name__ = "Base64解码"
__description__ = "解码Base64编码的内容"

def __checktype__(file_path):
    return file_path.lower().endswith(('.b64', '.base64', '.txt'))

def __start__(file_path, password_list=None):
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
        
        decoded_content = base64.b64decode(content)
        
        output_dir = os.path.join("output", "base64_decoded")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_decoded.txt"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'wb') as f:
            f.write(decoded_content)
        
        return f"成功解码 Base64 内容,已保存到 {output_path}", [output_path]
    except Exception as e:
        return f"处理文件 {file_path} 时出错：{str(e)}", None

def __result__(result):
    if isinstance(result, tuple) and len(result) == 2:
        log_message, output_files = result
        if output_files:
            return f"Base64 解码结果已保存到: {output_files[0]}"
    return None
```

这个示例展示了一个基本的插件结构,包括所有必需的方法和属性。您可以根据这个模板来开发自己的插件。
