pyinstaller --log-level=DEBUG ^
    --noconsole ^
    --add-data="C:\Users\Luca\github\backCor\data\sampleData\sample_1_multi.wdf;data\sampleData" ^
    --add-data="C:\Users\Luca\github\backCor\data\sampleData\sample_2_single.wdf;data\sampleData" ^
    --add-data="C:\Users\Luca\github\backCor\data\userData\settings.json;data\userData" ^
    --add-data="C:\Users\Luca\github\backCor\img\ico\backCor_BB.ico;img\ico" ^
    --add-data="C:\Users\Luca\github\backCor\img\ico\backCor_WB.ico;img\ico" ^
    --icon="C:\Users\Luca\github\backCor\img\ico\backCor_BB.ico" ^
    backCor.py
