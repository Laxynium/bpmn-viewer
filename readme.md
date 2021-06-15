# Projekt zaliczeniowy
Aplikacja webowa do wyświetlania diagramu bpmn na podstawie śladów procesu

## Struktura projektu
W skład projektu wchodzi aplikacja frontendowa, która znajduje się w folderze `client` 
oraz aplikacja backendowa, która znajduje się w folderze `server`

Do projektu zostały również dołączone skrypty bash budujące cały projekt, które są opisane poniżej.

## Uruchomienie projektu
W celu zbudowania projektu należy wykonać skrypt `build-app.bash`.
Następnie można już uruchomić samą aplikację wykonując skrypt `run-app.bash`.

## Użyte biblioteki
W celu utworzenia pliku xml z BPMN 2.0 wykorzystano bibliotekę `https://github.com/KrzyHonk/bpmn-python`.
Do samej prezentacji diagramu BPMN wykoarzystano bibliotekę `https://github.com/bpmn-io/bpmn-js` oraz do automatycznego ułożenia elementów skorzystano z biblioteki `https://github.com/bpmn-io/bpmn-auto-layout`.

## Demo aplikacji
Poniżej jest krótkie demo aplikacji(video znajduje się w `images/demo.mp4`):


https://user-images.githubusercontent.com/22114978/122017653-74b06980-cdc2-11eb-95d2-e14935d8dbca.mp4
