let 
  pkgs = import <nixpkgs> {};
  name = "streamdeck_addon";
in pkgs.stdenv.mkDerivation {
  buildInputs = [
    pkgs.python3
    pkgs.xxd
    pkgs.imhex
  ];
  inherit name;
  shellHook = ''
   # export QT_QPA_PLATFORM="wayland"
  '';
 }
