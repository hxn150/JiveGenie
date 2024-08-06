# JiveGenie
![](https://github.com/hxn150/JiveGenie/blob/main/banner.png)
Submission for TikTok Techjam 2024!

## Setup Instructions

To run our app do the following:

1. Create a conda environment with `conda create -n env_name python=3.10`.

2. Activate conda environment with `conda activate env_name`.

3. Setup conda environment by running `bash setup_conda.sh`.

4. Download [checkpoint.pt](https://drive.google.com/file/d/1BAR712cVEqB8GR37fcEihRV_xOC-fZrZ/view?usp=share_link) and move it into the `backend/EDGE` directory.

5. Run `npm install` inside the `frontend` directory to install all frontend dependencies.

6. Start the flask server by using `python main.py` in the `backend` directory.

7. In a separate terminal, run `npm run dev` to see the web app in action!

\*Note: tested on Ubuntu22.04, dependencies may not work for MacOS/Windows. 

For a smoother experience, also ensure that you disable cache in the devtools of whatever browser you are working from.

## Short Demo

![](https://github.com/hxn150/JiveGenie/blob/main/app_demo.gif)


## References
- [EDGE](https://github.com/Stanford-TML/EDGE/tree/main?tab=readme-ov-file)
- [MMHuman3D](https://github.com/open-mmlab/mmhuman3d)

