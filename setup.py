import os
import subprocess
import sys
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop


def build_c_library():
    """Compiles libdaxda_core.so C++ shared library on install or build."""
    here = os.path.abspath(os.path.dirname(__file__))
    csrc_dir = os.path.join(here, "daxda_engine", "csrc")
    gate_cpp = os.path.join(csrc_dir, "governed_authority_gate.cpp")
    core_cpp = os.path.join(csrc_dir, "daxda_core.cpp")

    target_so_pkg = os.path.join(here, "daxda_guard", "libdaxda_core.so")
    target_so_root = os.path.join(here, "libdaxda_core.so")

    if os.path.exists(gate_cpp) and os.path.exists(core_cpp):
        compiler = os.environ.get("CXX", "clang++")
        cmd = [
            compiler, "-std=c++17", "-O3", "-fPIC", "-shared",
            gate_cpp, core_cpp,
            "-o", target_so_pkg
        ]
        print(f"Compiling C++ core library: {' '.join(cmd)}")
        try:
            subprocess.check_call(cmd)
            # Copy to root as well if needed
            if target_so_pkg != target_so_root:
                import shutil
                shutil.copyfile(target_so_pkg, target_so_root)
            print("✓ Built libdaxda_core.so successfully!")
        except Exception as e:
            print(f"Warning: Failed to compile C++ library: {e}")
            # Try g++ fallback if clang++ fails
            if compiler == "clang++":
                try:
                    cmd[0] = "g++"
                    subprocess.check_call(cmd)
                    print("✓ Built libdaxda_core.so using g++ fallback!")
                except Exception as e2:
                    print(f"Warning: Fallback g++ build also failed: {e2}")


class CustomBuildPy(build_py):
    def run(self):
        build_c_library()
        super().run()


class CustomDevelop(develop):
    def run(self):
        build_c_library()
        super().run()


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="daxda-guard",
    version="1.0.0",
    description="DAXDA Guard Air-Gapped Synchronous AI Security & Audit SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="DAXDA Security Engineering",
    author_email="security@daxda.ai",
    url="https://github.com/daxda/daxda-guard",
    packages=find_packages(include=["daxda_guard", "daxda_guard.*", "daxda_engine", "daxda_engine.*"]),
    package_data={
        "daxda_guard": ["*.so", "*.dylib", "*.dll"],
    },
    include_package_data=True,
    cmdclass={
        "build_py": CustomBuildPy,
        "develop": CustomDevelop,
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C++",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires=">=3.8",
    install_requires=[],
)
