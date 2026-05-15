{
  map = {
    seed = 3;
    size = [ 256 256 ];
    cellcapacity = 400;
    wind = "clockwise";
  };
  materials = [ "sand" "dirt" "wood" "coal" "gold" ];
  biomes = {
    hot_desert = {
      materials = [ "sand" "gold" ];
      elevation = [ 0.4 0.48 ];
      rainfall = [ 0 0.1 ];
      temperature = [ 310 400 ];
    };
  };
}
