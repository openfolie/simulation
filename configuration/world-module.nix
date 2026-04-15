{ lib, config, ... }:

with lib;

let
  cfg = config.world;
  validWinds = ["north" "south" "east" "west" "clockwise" "anticlockwise"];
  materialSet = builtins.listToAttrs (map (m: { name = m; value = true; }) cfg.materials);
in {
  options.world = {
    map = mkOption {
      type = types.submodule {
        options = {
          seed = mkOption {
            type = types.int;
          };
          size = mkOption {
            type = types.listOf types.int;

            apply = v:
              if builtins.length v == 2
              then v
              else throw "map.size must contain exactly 2 integers";
          };
          cellcapacity = mkOption {
            type = types.int;
          };
          wind = mkOption {
            type = types.str;
            apply = v:
              if builtins.elem v validWinds 
              then v
              else throw "Invalid map wind set, expected one of {${builtins.concatStringsSep ", " validWinds}}. Got ${v}";
          };
        };
      };
    };
    materials = mkOption {
      type = types.listOf types.str;
    };

    biomes = mkOption {
      type = types.listOf (types.submodule {
        options = {
          name = mkOption {
            type = types.str;
          };

          materials = mkOption {
            type = types.listOf types.str;
          };
        };
      });
    };
  };

  config = let
    validMaterials =
      builtins.all (biome:
        builtins.all (m:
          builtins.hasAttr m materialSet
        ) biome.materials
      ) cfg.biomes;
  in
  {
    _module.check =
      (validMaterials || throw "Biome uses undefined material");
  };
}
