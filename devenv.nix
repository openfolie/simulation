{ pkgs, lib, config, inputs, ... }:

{
  packages = with pkgs; [
    git
    uv
    zlib
    clinfo
    opencl-headers
    ocl-icd
    SDL2
    wayland
    libxkbcommon
    libdrm
    mesa
    libGL
    libGLU
  ];
  languages.python.enable = true;
  env = {
    LD_LIBRARY_PATH = "/run/opengl-driver/lib";
    OCL_ICD_VENDORS = "/run/opengl-driver/etc/OpenCL/vendors";
    SDL_VIDEODRIVER = "wayland";
    LIBGL_DRIVERS_PATH = "${pkgs.mesa.drivers}/lib/dri";
  };
}
