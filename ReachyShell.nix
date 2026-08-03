{ pkgs ? import <nixpkgs> {} }:

let
  buildInputs = with pkgs; [
    python312
    python312.pkgs.venvShellHook
    python312.pkgs.numpy
    python312.pkgs.mujoco 
    python312.pkgs.pycairo
    uv
    git
    git-lfs
    gst_all_1.gstreamer
    gst_all_1.gst-plugins-base
    gst_all_1.gst-plugins-good
    gst_all_1.gst-plugins-bad
    gst_all_1.gst-plugins-ugly
    gst_all_1.gst-libav
    libGL
    glib
    portaudio
    alsa-utils
    zlib
    cmakeMinimal
    pkg-configUpstream
    cairo
    #cairo-lang
    cairomm_1_16

  ];
in

pkgs.mkShell {
  packages = buildInputs;

  venvDir = "./reachy_mini_env";

  postVenvCreation = ''
    uv pip install "reachy-mini"
    uv pip uninstall opencv-python opencv-contrib-python
    uv pip install opencv-python-headless
    # For simulation mode, use: uv pip install "reachy-mini[mujoco]"
    # For other extras, add them as needed, e.g., "reachy-mini[gstreamer,wireless-version]"
  '';

  postShellHook = ''
    export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath buildInputs}''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
    echo "Reachy Mini dev environment activated."
    echo "If you need to reinstall dependencies, remove the venv directory and re-enter the shell."
    uv run reachy-mini-daemon
  '';
  
}
