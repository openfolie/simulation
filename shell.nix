{ pkgs ? import <nixpkgs> {} }:
let
  pygame = true;
in
pkgs.mkShell {
  packages = with pkgs; [
      git
      uv
      zlib
      python3
    ] ++ (if pygame then [
      SDL2
      wayland
      libxkbcommon
      libdrm
      mesa
      libGL
      libGLU
    ] else []);

  SDL_VIDEODRIVER = if pygame then "wayland" else null;
  LIBGL_DRIVERS_PATH = if pygame
    then "${pkgs.mesa}/lib/dri"
    else null;
  LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (
    [
      pkgs.zlib
    ] ++ (if pygame then [
      pkgs.SDL2
      pkgs.libGL
      pkgs.libGLU
      pkgs.mesa
    ] else [])
  );

  shellHook = ''
python --version
uv sync
  '';
}
