call "C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\VC\Auxiliary\Build\vcvars64.bat"

echo %cd%

msbuild Vectorize.sln /property:Configuration=Release /property:Platform=x64

cd Test\AccuracyTest
..\..\x64\Release\AccuracyTest.exe

cd ..\SpeedPerformanceTest
 ..\..\x64\Release\SpeedPerformanceTest.exe

 exit
