let
  lib = import <nixpkgs/lib>;

  worldData = import ./configuration/world.nix;

  result = lib.evalModules {
    modules = [
      ./configuration/world-module.nix
      { world = worldData; }
    ];
  };
in
result.config.world
