from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.apple import XcodeDeps


class SystemCExampleCPP(ConanFile):
    name = "dvconchallenge"
    version = "2407"
    package_type = "application"

    # Optional metadata
    license = "MIT License"
    author = "Moritz Herzog <herzogm@rptu.de>"
    url = "https://dvconchallenge.de"
    description = ""
    topics = ("systemc", "dvcon", "challange")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": False}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "*"

    def requirements(self):
        self.requires("systemc/2.3.4")
        self.requires("systemc-cci/1.0.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC


    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.user_presets_path = 'ConanPresets.json'
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
