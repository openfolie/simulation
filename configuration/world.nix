{
  map = {
    seed = 3;
    size = [ 256 256 ];
    cellcapacity = 400;
    wind = "clockwise";
  };
  materials = [ "sand" "dirt" "wood" "coal" "gold" ];
  biomes = {
    polar = {
      materials = [];
      points = [
          [4000 0 250]
          [8000 0 250]
      ];
    };
    tundra = {
        materials = [];
        points = [
            [0 10 250]
        ];
    };
    boreal = {
        materials = [];
        points = [
            [0 30 250]
        ];
    };
    oceanic = {
        materials = [];
        points = [
            [0 100 290]
        ];
    };
    continental = {
        materials = [];
        points = [
            [400 50 270]
        ];
    };
    tropical = {
        materials = [];
        points = [
            [80 100 300]
        ];
    };
    arid_desert = {
        materials = ["sand" "gold"];
        points = [
            [0 0 323]
        ];
    };
    cold_desert = {
        materials = [];
        points = [
            [0 0 250]
        ];
    };
  };
}
