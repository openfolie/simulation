{ pkgs, lib, config, inputs, ... }:

{
  packages = with pkgs; [
    git
    uv
    zlib
    clinfo
    opencl-headers
    ocl-icd
  ];
  languages.python.enable = true;
  env = {
    LD_LIBRARY_PATH = "/run/opengl-driver/lib";
    OCL_ICD_VENDORS = "/run/opengl-driver/etc/OpenCL/vendors";
  };
}
