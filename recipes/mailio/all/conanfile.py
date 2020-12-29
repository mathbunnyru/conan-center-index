from conans import ConanFile, CMake, tools
import glob
import os


class mailioConan(ConanFile):
    name = "mailio"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/karastojko/mailio"
    description = "mailio is a cross platform C++ library for MIME format and SMTP, POP3 and IMAP protocols."
    topics = ("conan", "smpt", "imap", "email", "mail", "libraries", "cpp")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "shared": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False
    }
    requires = ["boost/1.75.0", "openssl/1.1.1i"]
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    short_paths = True
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["MAILIO_BUILD_SHARED_LIBRARY"] = self.options.shared
            self._cmake.definitions["MAILIO_BUILD_DOCUMENTATION"] = False
            self._cmake.definitions["MAILIO_BUILD_EXAMPLES"] = False
            if not self.settings.compiler.cppstd:
                self._cmake.definitions["CMAKE_CXX_STANDARD"] = 17
            else:
                tools.check_min_cppstd(self, 17)
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("mailio-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build(self):
        patches = self.conan_data["patches"][self.version]
        for patch in patches:
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
