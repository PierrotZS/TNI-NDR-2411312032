# Website Trading Analysis Project
This website is respresent for project in ENG-494 Extra Curriculum Activity in Engineering 4.
<br>
The website is using data from The Stock Exchange of Thailand (SET) to show SMART Marketplace that will be helpful for Inverstor. This website can show the Stock Real-time Price and Trend of the price. 
Invertor can using the Technical Analysis like MACD, RSI or Parabolic SAR for their consider.

## Example
You can visit at : [PierrotTrade](https://stockpierrot.streamlit.app/) 
Slide Presentation : [Slide](https://www.canva.com/design/DAGofQh4nHo/jVZIaPWUaDjhoJvqLnaKVA/edit?utm_content=DAGofQh4nHo&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)

## Team Members
| Name       |      Student ID   |     GitHub ID     |
|------------|------------------|:-----------------:|
| Nawapol Piyatanaporn     |    2411312032   |      [PierrotZS](https://github.com/PierrotZS)      |

## Requirements
* Language: Python ![Python](https://img.shields.io/badge/Python-3.13.3-blue?logo=python&logoColor=white)
* Module for Website:
    * Streamlit ![Streamlit](https://img.shields.io/pypi/v/streamlit.svg?logo=streamlit&logoColor=white&label=Streamlit)
    * Pandas    ![Pandas](https://img.shields.io/pypi/v/pandas.svg?logo=pandas&logoColor=white&label=Pandas)
    * Numpy     ![Numpy](https://img.shields.io/pypi/v/numpy.svg?logo=numpy&logoColor=white&label=Numpy)
    * Scikit-learn     ![Numpy](https://img.shields.io/pypi/v/scikit-learn.svg?logo=scikit-learn&logoColor=white&label=Scikit-learn)
    * Altair     ![Altair](https://img.shields.io/pypi/v/altair.svg?logo=altair&logoColor=white&label=Altair)
    * st-Annotated Text     ![st-Annotated_text](https://img.shields.io/pypi/v/st-annotated-text.svg?logo=st-annotated-text&logoColor=white&label=st-Annotated_Text)

### Steps for starting application
1. Clone this project and change directory to be `TNI-NDR-2411312032`.
       
        $ git clone https://github.com/PierrotZS/TNI-NDR-2411312032.git
        $ cd TNI-NDR-2411312032/

2. Download and Install Python

    Link for download : [Python](https://www.python.org/downloads/)

3. Update python pip to the current version

        $ python.exe -m pip install --upgrade pip

4. Install modules in [requirements.txt](requirements.txt) using 
  
        $ pip install -r requirements.txt

5. Run the website

        $ streamlit run web.py

    or in case it doesn't work

        $ python -m streamlit run web.py