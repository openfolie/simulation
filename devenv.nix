{ pkgs, lib, config, inputs, ... }:
let
  pygame = true;
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
  ] else []);
  languages.python.enable = true;
  env = lib.mkMerge [
    (lib.mkIf pygame {
      SDL_VIDEODRIVER = "wayland";
      LIBGL_DRIVERS_PATH = "${pkgs.mesa.drivers}/lib/dri";
    })
  ];
}
