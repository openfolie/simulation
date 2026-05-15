{ lib, config, ... }:

with lib;

let
  cfg = config.world;
  materialSet = builtins.listToAttrs (map (m: { name = m; value = true; }) cfg.materials);
  number = types.either types.int types.float;
  range = t: mkOption {
    type = types.listOf t;

    apply = v:
      if builtins.length v == 2
      then v
      else throw "range must contain exactly 2 entries";
  };
in {
  options.world = {
    map = mkOption {
      type = types.submodule {
        options = {
          seed = mkOption {
            type = number;
          };
          size = range types.int;
          cellcapacity = mkOption {
            type = types.int;
          };
          wind = mkOption {
            type = types.enum [
              "north" "south" "east" "west"
              "clockwise" "anticlockwise"
            ];
          };
        };
      };
    };
    materials = mkOption {
      type = types.listOf types.str;
    };

    biomes = mkOption {
      type = types.attrsOf (types.submodule ({ ... }: {
        options = {
          materials = mkOption {
            type = types.listOf types.str;
          };
          elevation = range number;
          rainfall = range number;
          temperature = range types.int;
        };
      }));
    };
  };

  config = let
    validMaterials =
      builtins.all (biome:
        builtins.all (m:
          builtins.hasAttr m materialSet
        ) biome.materials
      ) (builtins.attrValues cfg.biomes);
  in
  {
    _module.check =
      (validMaterials || throw "Biome uses undefined material");
  };
}
