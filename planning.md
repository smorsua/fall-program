## Cálculo parámetros

-   $SV = \sqrt{A_x^2+A_y^2+A_z^2}$
-   $SV_D = HPF(\sqrt{A_x^2+A_y^2+A_z^2})$
-   $SV_{MaxMin}$: diferencia entre máximo y mínimo de SV en una ventana de 0.1s.
-   $\huge{Z_2=\frac{SV_{TOT}^2-SV_D^2-G^2}{2G}}$
-   $v_o$: integrada from the pit, at the beginning of the fall, until the impact, where the
    signal value is lower than 1g.

## Clase: FallDetector

-   Buffer de 2s. El primer algoritmo no necesita buffer (excepto para la detección de postura) y el segundo algoritmo espera durante un segundo.
-   Socket que se conecta al telefono

## Interfaz App

-   Gráfica deslizante de los componentes de acceleración
-   Marcadores verticales que indican el intervalo de detección de caída.
-   Cuadro de texto que indica si se detecta caída.
-   Estado de conexión TCP + socket actual
-   Formulario para elegir socket
-   Boton de start y stop

## Roadmap

-   [x] Conectarnos a movil y recibir datos (Sergio)
-   [x] Mostrar datos sin procesar (Sergio)
-   [ ] Componente estado de conexión (Sergio)
-   [ ] Desplegable elegir sample rate
-   [ ] Calculo de parametros (Alex)
-   [ ] Algoritmo detección de caida (Alex, solo thresholds)
-   [ ] Adicional: marcadores verticales, formulario de conexión
