pyinstaller --log-level=DEBUG ^
    --noconsole ^
    --add-data="C:\Users\Luca\github\backCor\backCor\data\sampleData\sample_1_multi.wdf;data\sampleData" ^
    --add-data="C:\Users\Luca\github\backCor\backCor\data\sampleData\sample_2_single.wdf;data\sampleData" ^
    --add-data="C:\Users\Luca\github\backCor\backCor\data\sampleData\sample_3_multi.txt;data\sampleData" ^
    --add-data="C:\Users\Luca\github\backCor\backCor\data\sampleData\sample_4_single.txt;data\sampleData" ^
    --add-data="C:\Users\Luca\github\backCor\backCor\data\userData\settings.json;data\userData" ^
    --add-data="C:\Users\Luca\github\backCor\backCor\img\ico\backCor_BB.ico;img\ico" ^
    --add-data="C:\Users\Luca\github\backCor\backCor\img\ico\backCor_WB.ico;img\ico" ^
    --add-binary="C:\Users\Luca\github\backCor\backCor\fonts\Poppins-Regular.ttf;fonts" ^
    --add-binary="C:\Users\Luca\github\backCor\backCor\fonts\Poppins-Bold.ttf;fonts" ^
    --icon="C:\Users\Luca\github\backCor\backCor\img\ico\backCor_BB.ico" ^
    backCor.py
