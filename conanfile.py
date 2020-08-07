import os

from conans import ConanFile, CMake, tools

class OpenmeshConan(ConanFile):
    name = "openmesh"
    description = "OpenMesh is a generic and efficient data structure for " \
                  "representing and manipulating polygonal meshes."
    license = "BSD-3-Clause"
    topics = ("conan", "openmesh", "mesh", "structure", "geometry")
    homepage = "https://www.graphics.rwth-aachen.de/software/openmesh"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("OpenMesh-" + self.version, self._source_subfolder)

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "if(\"${PROJECT_NAME}\" STREQUAL \"\")",
                              "if(TRUE)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "ACGCommon.cmake"),
                              "set (ACG_PROJECT_BINDIR \".\")",
                              "set (ACG_PROJECT_BINDIR \"bin\")")
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.settings.os == "Windows":
            self._cmake.definitions["OPENMESH_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["BUILD_APPS"] = False
        self._cmake.definitions["OPENMESH_DOCS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "libdata"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        # TODO: components shouldn't be namespaced
        self.cpp_info.names["cmake_find_package"] = "OpenMesh"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenMesh"
        self.cpp_info.names["pkg_config"] = "openmesh"
        # OpenMeshCore
        self.cpp_info.components["openmeshcore"].names["cmake_find_package"] = "OpenMeshCore"
        self.cpp_info.components["openmeshcore"].names["cmake_find_package_multi"] = "OpenMeshCore"
        self.cpp_info.components["openmeshcore"].libs = [self._get_decorated_lib("OpenMeshCore")]
        # OpenMeshTools
        self.cpp_info.components["openmeshtools"].names["cmake_find_package"] = "OpenMeshTools"
        self.cpp_info.components["openmeshtools"].names["cmake_find_package_multi"] = "OpenMeshTools"
        self.cpp_info.components["openmeshtools"].libs = [self._get_decorated_lib("OpenMeshTools")]
        self.cpp_info.components["openmeshtools"].requires = ["openmeshcore"]

    def _get_decorated_lib(self, name):
        libname = name
        if self.settings.build_type == "Debug":
            libname += "d"
        return libname
