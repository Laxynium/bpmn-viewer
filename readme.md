# Projekt zaliczeniowy
Aplikacja webowa do wyświetlania diagramu bpmn na podstawie śladów procesu

## Budowa projektu
W skład projektu wchodzi aplikacja frontendowa, która znajduje się w folderze `client` 
oraz aplikacja backendowa, która znajduje się w folderze `server`

Do projektu zostały również dołączone skrypty bash budujące cały projekt, które są opisane poniżej.

## Uruchomienie projektu
W celu zbudowania projektu należy wykonać skrypt `build-app.bash`.
Następnie można już uruchomić samą aplikację wykonując skrypt `run-app.bash`.

## Użyte biblioteki
W celu utworzenia pliku xml z BPMN 2.0 wykorzystano bibliotekę `https://github.com/KrzyHonk/bpmn-python`.
Do samej prezentacji diagramu BPMN wykoarzystano bibliotekę `https://github.com/bpmn-io/bpmn-js` oraz do automatycznego ułożenia elementów skorzystano z biblioteki `https://github.com/bpmn-io/bpmn-auto-layout`.

## Opis działania
Poniżej jest krótkie demo aplikacji:
<!-- blank line -->
<figure class="video_container">
  <video controls="true" allowfullscreen="true" poster="images/demp.mp4">
    <source src="path/to/video.mp4" type="video/mp4">
    <source src="path/to/video.ogg" type="video/ogg">
    <source src="path/to/video.webm" type="video/webm">
  </video>
</figure>
<!-- blank line -->

Jak widać na nim, można wybrać odpowiedni plik i jeżli jest to plik csv pojawiają się dodatkowe pola do wprowadzenia informacji na temat struktury tego pliku. Po kliknięciu przycisku submit na serwer są wysłyane dane z formularza, które następnie są procesowane.

Po stronie serwera po otrzymaniu danych i ich wstępnej walidacji, rozpoznajemy rozszerzenie pliku i na jego podstawie jest wywołana odpowiednia funkcja , która tworzymy list śladów. 
