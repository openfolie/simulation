{ pkgs, lib, config, inputs, ... }:

{
  packages = with pkgs; [ git uv ];
  languages.python.enable = true;
}
