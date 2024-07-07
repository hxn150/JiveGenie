# JiveGenie

TechJam Repo

To run main.py do the following:

1. Setup conda environment:
   `conda create --name <env> --file requirements.txt`

2. Clone the [EDGE](https://github.com/Stanford-TML/EDGE.git) and follow installation instructions for [mmhuman3d](https://mmhuman3d.readthedocs.io/en/latest/install.html#) (cpu).

3. Download [checkpoint.pt](https://drive.google.com/file/d/1BAR712cVEqB8GR37fcEihRV_xOC-fZrZ/view?usp=share_link) and move it into the EDGE directory.

4. Move `EDGE_api.py` into the EDGE directory.

5. Run `npm install` to install all frontend dependencies

6. Start the flask server by using `flask run`

7. In a separate terminal, run `npm run dev` to see the web app in action!

If you would like a quick demo, go into `main.py` and set `use_cached_features=True` to generate dances from our sample set. To upload custom music files, ensure that files are in `.wav`, are 10 seconds long and that `use_cached_features=True` is set to false!

\*Note: tested on Ubuntu22.04, dependencies may not work for MacOS/Windows
