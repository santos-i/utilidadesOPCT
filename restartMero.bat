@echo off 

set url=192.168.92.18


For /F %%G In ('%__AppDir__%curl.exe -s -o NUL "%url%" -w "%%{http_code}\n"') Do Set "response=%%G"
echo response code is %response%


IF %response% == 200 (
    ECHO 'SERVER OK!  - %date% %time%' >> log_restartMero.txt
	
) ELSE (
    ECHO 'RESTARTING SERVER! - %date% %time%'>>log_restartMero.txt
	cmd /k "cd /d C:\Users\oceanografia\Envs\meroWeb\Scripts & activate & cd /d    D:\Boia Geo\Boia_Mero_Python\pboiaMero & flask run --host 0.0.0.0 --port 80"
)
