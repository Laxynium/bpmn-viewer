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

## Opis aplikacji frontendowej

Aplikacja została wykonana w czystym javascript. Składa się z plików index.js, index.html, style.css.
W ramach pliku html został umieszczony formularz do wyboru pliku jak również dodtkowych informacji na temat struktury pliku csv.

W pliku index.js znajduje się kod, który nasłuchuje na zmiany związane z wyborem pliku - gdy wybierzemy plik csv pokazuje dodatkowe pola, 
w przeciwnym wypadku pola te są chowane. 
W pliku tym również nasłuchujemy na zatwierdzenie formularza i gdy to nastąpi wywołujemy zapytanie do serwera przesyłając dane z formularza.
Serwer w ramach pozytywnej odpowiedzi zwraca xml zawierający strukturę diagramu BPMN.
Następnie korzystamy z biblioteki bpmn-auto-layout, która dodaje informację o położeniu poszczególnych elementów diagramu BPMN(odpowiedź z serwera ich nie zawiera).
I tak przekształcony xml jest następnie wyświetlany przy użyciu biblioteki bpmn-js.

Projekt ten róznież korzysta z biblioteki webpack, aby móc wykorzystać gotowe biblioteki npm.
### Uwagi
Biblioteka bpmn-auto-layout została dodana bezpośrednio do projektu a nie w postaci paczki npm, gdyż zawierała błędy, 
które wymagały naprawy(https://github.com/bpmn-io/bpmn-auto-layout/issues/18).

## Opis aplikacji backendowej

Aplikacja została oparta o pythonową bibliotekę flask. 
W ramach aplikacji został umieszczony plik `server.py`, który odpowiada za konfigurację serwera oraz obsługę przychodzących zapytań http.

Po stronie serwera włączono możliwość serwowania statycznych plików, aby móc bezpośrednio zwrócić pliki potrzebne do działania aplikacji frontendowej w przeglądarce. Skrypt budujący cały projekt kopiuje wygenerowane pliki z folderu `client/dist` do folderu `server/static`. Takie rozwiązanie pozwoli uniknąć potrzebe uruchamiania dwóch aplikacji jak rówież konfigurowania CORS.

Serwer wystawia endpoint `/api/upload` pod którym można wysyłać dane z formularza. 
Dane te są w pierwszej kolejności walidowane a nastepnie jest wywołana metoda `logic/get_xml_file`, która na ich podstawie generuje xmla z diagramem BPMN.
Sama metoda korzysta z rozwiązań z zajęć, aby utworzyć odpowiednią listę śladów zdarzeń w zależności od rodzaju pliku, jak również aby wykryć odpowiednie relacje w tych śladach w celu późniejszego zbudowania diagramu BPMN. Kod ten został zawarty w pliku `logic/bpmn_builder.py`. Rozwiązanie z zajęć zostało przekształcone w taki sposób, że zamiast dodawać zdarzenia/bramki/połączenia bezpośrednio do grafu z biblioteki pygraphviz, zdarzenia te są dodawane do klasy InMemoryGraph.
Następnie na podstawie danych(bramki/krawędzie/zdarzenia) zawartych w tej klasie budujemy graf przy użyciu biblioteki bpmn-python. 
W celu uniknięcia kilku krotnego dodania tych samych elementów wywołania z tej biblioteki zostały przykryte wywołaniami z własnej klasy BpmnGraphCreator, 
która zapamiętuje wcześniej dodane elementy. Biblioteka ta, tak utworzony graf zapisuje do pliku BPMN 2.0 xml, którego zawartość jest nastepnie odczytywana i zwracana w odpowiedzi HTTP.

### Uwagi
Biblioteka https://github.com/KrzyHonk/bpmn-python została dodana bezpośrednio do projektu, a nie przy użyciu pip, gdyż również zawierała błędy, które wymagały naprawy(https://github.com/KrzyHonk/bpmn-python/issues/42). Biblioteka pozwala również zawrzeć informację o położeniu elementów bpmn, jednak przy próbie użycia tej funkcjonalności pojawiały się błędy, których nie udało się rozwiązać, więc zdecydowano się na obsługę tej funkcjonalności po stronie klienta.  


