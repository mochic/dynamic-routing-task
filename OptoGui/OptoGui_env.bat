call conda create --name OptoGui python=3.9.5 --yes
call activate OptoGui
call python -m pip install PyQt5==5.15.6 --index-url https://pypi.org/simple
call python -m pip install numpy==1.22.3 --index-url https://pypi.org/simple
call python -m pip install scipy==1.8.0 --index-url https://pypi.org/simple
cmd /k