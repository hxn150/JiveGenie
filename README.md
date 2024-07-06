# JiveGenie

TechJam Repo

To run main.py do the following:

1. Setup conda environment:
   `conda create --name <env> --file requirements.txt`

2. Clone the [EDGE](https://github.com/Stanford-TML/EDGE.git) and follow installation instructions for [mmhuman3d](https://mmhuman3d.readthedocs.io/en/latest/install.html#)

3. Download [checkpoint.pt](https://drive.google.com/file/d/1BAR712cVEqB8GR37fcEihRV_xOC-fZrZ/view?usp=share_link) and move it into the EDGE directory.

4. Move `EDGE_api.py` into the EDGE directory.

5. Create a directory to add your music clips and edit the the call to `run_edge_generation` accordingly.

6. Then run `python3 main.py` to generate a choreography!
