{ pkgs, lib, config, inputs, ... }:
let
  pygame = true;
  opencl = {
    enable = true;
    gpu = "nvidia";
  };
  env_ocl_vendors = {
    intel = "${pkgs.intel-compute-runtime}/etc/OpenCL/vendors";
    old-intel = "${pkgs.intel-compute-runtime}/etc/OpenCL/vendors";
    amd = "${pkgs.rocmPackages.clr.icd}/etc/OpenCL/vendors";
    # nvidia = "${pkgs.cudaPackages.cudatoolkit}/etc/OpenCL/vendors";
    nvidia = "/run/opengl-driver/etc/OpenCL/vendors";
  };
in
{
  packages = with pkgs; [
    git
    uv
    zlib
  ] ++ (if pygame then [
    SDL2
    wayland
    libxkbcommon
    libdrm
    mesa
    libGL
    libGLU
  ] else []) ++ (if opencl.enable then [
    ocl-icd
  ] else []) ++
  (if opencl.enable && opencl.gpu == "intel" then [
    intel-compute-runtime
  ] else []) ++
  (if opencl.enable && opencl.gpu == "old-intel" then [
    intel-compute-runtime
    beignet intel-ocl
  ] else []) ++
  (if opencl.enable && opencl.gpu == "amd" then [
    rocmPackages.clr.icd
  ] else []) ++
  (if opencl.enable && opencl.gpu == "nvidia" then [
    # cudaPackages.cudatoolkit
    linuxPackages.nvidia_x11
  ] else []);
  languages.python.enable = true;
  env = lib.mkMerge [
    (lib.mkIf pygame {
      SDL_VIDEODRIVER = "wayland";
      LIBGL_DRIVERS_PATH = "${pkgs.mesa.drivers}/lib/dri";
    })
    (lib.mkIf opencl.enable {
      OCL_ICD_VENDORS = env_ocl_vendors."${opencl.gpu}";
    })
    ({
      OCL_ICD_DEBUG = "7";
    })
  ];
    # LD_LIBRARY_PATH = "/run/opengl-driver/lib:/run/opengl-driver-32/lib";
    # OCL_ICD_VENDORS = "/run/opengl-driver/etc/OpenCL/vendors";
    # LD_LIBRARY_PATH = "/run/opengl-driver/lib";
    # OCL_ICD_VENDORS = "/run/opengl-driver/etc/OpenCL/vendors:${pkgs.pocl}/etc/OpenCL/vendors";
    # OPENCL_VENDOR_PATH = "${pkgs.pocl}/etc/OpenCL/vendors";
}
