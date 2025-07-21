from flask import Flask
from setuptools import setup, Extension
from Cython.Build import cythonize
import os
import sys

# Define the path to the directory containing python312.lib
# This assumes your setup.py is in the project root, and RPS_Venv is a subdirectory.
project_root = os.path.dirname(os.path.abspath(__file__))
# print(f"Project root directory: {project_root}")
python_lib_dir = os.path.join(project_root, "RPS_WebApp_Back", "Lib")

# Ensure this path is added to library_dirs only if it exists
# and contains the required .lib file.
extra_library_dirs = []
if os.path.exists(os.path.join(python_lib_dir, "python312.lib")):
    extra_library_dirs.append(python_lib_dir)
else:
    # As a fallback, also check the standard 'libs' directory within the venv
    # in case the file is actually there or the user was mistaken.
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        standard_lib_path = os.path.join(venv_path, 'libs')
        if os.path.exists(os.path.join(standard_lib_path, 'python312.lib')):
            extra_library_dirs.append(standard_lib_path)
    print(f"Warning: python312.lib not found in {python_lib_dir}. Check the path.")
    print(f"Attempting with automatically detected library paths. Current extra_library_dirs: {extra_library_dirs}")


# Define the extension module explicitly
extensions = [
    Extension(
        "iocaine_powder.IocainePowder_Cython",  # Name of the extension including package
        ["iocaine_powder/IocainePowder_Cython.pyx"], # List of source files with correct path
        library_dirs=extra_library_dirs     # Add your specific library directory here
    )
]

# Define the path to the pyx file relative to setup.py
# pyx_file = os.path.join("C:\VS Code\Rock-Paper-Scissors using Iocaine Powder\Iocaine_RPS.py", "C:\VS Code\Rock-Paper-Scissors using Iocaine Powder\iocaine_cython_parts.pyx")
# pyx_file = os.path.join("iocaine_powder", "IocainePowder_Cython.pyx")

# setup(
#     name='iocaine_powder',
#     ext_modules=cythonize(extensions),
#     zip_safe=False,
#     packages=['iocaine_powder'],  # Add this to include the package
# )

setup(
    name='iocaine_powder',
    ext_modules=cythonize(
        extensions,
        compiler_directives={'language_level': "3"},
        annotate=True  # Generates an HTML annotation file
    ),
    zip_safe=False,
    packages=['iocaine_powder'],
)