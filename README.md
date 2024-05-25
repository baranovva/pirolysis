﻿
# Pirolysis
Данное программное обеспечение предназначено для моделирования процесса пиролиза и подбора данных скоростей реакций, основываясь на  ранее полученных экспериментальных данных при использовании метода кислородной микрокалориметрии.

# Модель

Результатом измерения в методе КМК является зависимость удельной мощности тепловыделения при окислении летучих  от температуры образца . Аналитическое уравнение удельной мощности тепловыделения имеет вид:

$\dot{q} = \Delta\overline{q'} \frac{d\alpha}{dt} = \Delta \overline{q'} A f(\alpha) \exp\left( -\frac{E_a}{R T} \right)$

Где $\overline{q'}$ – интегральная теплота сгорания летучих, отнесенная к массе образца, вычисляется по формуле:

$\overline{q'} =\int_{0}^{t} \dot{q}(t) \, dt =\frac{1}{\beta}\int_{T_0}^{T_max} \dot{q}(T) \, dT$

$\alpha$ – тепловая глубина превращения:

$\alpha = \frac{\int_{0}^{t} \dot{q}(t) \, dt}{\int_{0}^{t_{\text{max}}} \dot{q}(t) \, dt} = \frac{1}{\beta \Delta q'} \int_{T_0}^{T} \dot{q}(T) \, dT$

f($\alpha$) – конверсионная функция, которая аппроксимируется следующим образом:

$f(\alpha) = (1 - \alpha)^n \left( \alpha^m + \alpha_* \right)$

А также скорость реакции $\dot{r}=\dot{q}/\Delta\overline{q'}$.

# Особенности

- Загрузка и обработка экспериментальных файлов данных, содержащих информацию о температуре и скорости выделения тепла (HRR).
  
- Извлечение и отображение информации из заголовка файлов данных.
  
- Подбор модели скорости реакции к экспериментальным данным.
  
- Отображение оптимизированных параметров модели.
  
- Построение графиков экспериментальных данных и предсказаний модели.
  
# Использование

1. Открыть файл: Нажмите кнопку "Открыть файл", чтобы открыть диалоговое окно выбора файла и выбрать файл данных (в текстовом формате). Информация из заголовка файла будет отображена в текстовом поле под кнопкой.
2. Обработать данные: После загрузки файла нажмите кнопку "Обработать данные", чтобы обработать данные. Оптимизированные параметры модели будут отображены в текстовом поле с результатами.
3. Показать график: Нажмите кнопку "Показать график", чтобы открыть новое окно с графиком экспериментальных данных и предсказаний модели.

# Формат файла данных

Файлы данных должны быть в текстовом формате и содержать информацию о температуре и HRR. В заголовке файла должна быть указана скорость нагрева, например, `# Heating Rate: 10.0`.

# Методы

scipy.optimize.differential_evolution - метод, используемый в эволюционных вычислениях, который стремится итеративно улучшать кандидатное решение относительно заданного критерия качества.

# Структура

`main.py`: Основной скрипт для запуска приложения.

`models.py`: Содержит класс `Models` для обработки и подбора данных.

`file_processor.py`: Содержит класс `FileProcessor` для чтения и обработки файлов данных.

`gui.py`: Содержит класс `App` для графического интерфейса пользователя.

![image](https://github.com/baranovva/pirolysis/assets/170364565/62982e8b-5086-464f-832e-9eda2f0ca9a7)


