import os
import importlib.util

class PluginManager:
    def __init__(self):
        self.plugin_dirs = ['base_plugins', 'ex_plugins', 'check_plugins']
        self.plugins = {dir_name: {} for dir_name in self.plugin_dirs}
        self.load_all_plugins()

    def load_all_plugins(self):
        for dir_name in self.plugin_dirs:
            self.load_plugins(dir_name)

    def load_plugins(self, dir_name):
        plugin_dir = os.path.join('plugins', dir_name)
        if not os.path.exists(plugin_dir):
            #print(f"警告: 插件目录不存在 {plugin_dir}")
            return

        for item in os.listdir(plugin_dir):
            plugin_path = os.path.join(plugin_dir, item)
            if os.path.isdir(plugin_path):
                init_file = os.path.join(plugin_path, "__init__.py")
                if os.path.exists(init_file):
                    try:
                        spec = importlib.util.spec_from_file_location(f"{dir_name}.{item}", init_file)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        plugin_name = getattr(module, '__plugin_name__', item)
                        plugin_description = getattr(module, '__description__', '')
                        
                        full_name = f"{plugin_name}: {plugin_description}"
                        self.plugins[dir_name][full_name] = module
                        #print(f"成功加载插件: {full_name} ({dir_name})")
                    except Exception as e:
                        print(f"加载插件 {item} 时出错: {str(e)}")

    def get_plugins(self, dir_name):
        return list(self.plugins.get(dir_name, {}).keys())

    def get_plugin(self, dir_name, plugin_name):
        return self.plugins.get(dir_name, {}).get(plugin_name)

    def refresh_plugins(self):
        self.plugins = {dir_name: {} for dir_name in self.plugin_dirs}
        self.load_all_plugins()