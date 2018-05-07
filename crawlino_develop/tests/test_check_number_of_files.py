def test_check_all_required_files(plugins_files: list):
    for plugin in plugins_files:
        plugin_name, plugin_files = plugin

        assert "__init__.py" in plugins_files, \
            f"Plugin {plugin_name} must contain a __init__.py file"

        assert "README.rst" in plugins_files, \
            f"Plugin {plugin_name} must contain a README.rst file"

        assert "requirements.txt" in plugins_files, \
            f"Plugin {plugin_name} must contain a readme.rst file"


def test_check_all_required():
    assert 1 == 1
