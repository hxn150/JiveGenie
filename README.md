# JiveGenie

TechJam Repo

To run main.py do the following:

1. Setup conda environment:
   `conda create --name <env> --file requirements.txt`

2. Follow installation instructions for [mmhuman3d](https://mmhuman3d.readthedocs.io/en/latest/install.html#) (cpu)*.

3. Download [checkpoint.pt](https://drive.google.com/file/d/1BAR712cVEqB8GR37fcEihRV_xOC-fZrZ/view?usp=share_link) and move it into the `backend/EDGE` directory.

6. Run `npm install` to install all frontend dependencies.

7. Start the flask server by using `flask run`.

8. In a separate terminal, run `npm run dev` to see the web app in action!

The webapp is currently set to run a quick demo with pre-computed features, with `use_cached_features=True` in the `run_edge_generation` function in `main.py`. To upload custom music files, ensure that files are in `.wav`, are 10 seconds long and that `use_cached_features=True` is set to false! To reset the project and remove all demo/previous dance generation info, remove the files in the following directories:

- `backend/EDGE/custom_music`
- `backend/EDGE/cache_features`
- `backend/EDGE/renders`
- `backend/EDGE/SMPL-to-FBX`
- `frontend/outputs`

\*Note: tested on Ubuntu22.04, dependencies may not work for MacOS/Windows. For a smoother experience, also ensure that you disable cache in the devtools of whatever browser you are working from.
